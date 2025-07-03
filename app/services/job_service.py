# Python standard library - Core language functionality
from typing import List, Optional

# FastAPI and database components - Web and persistence layers
from fastapi import BackgroundTasks, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core import get_logger
# Application-specific imports - Models, schemas and services
from app.db import Company, Job, User, get_db
from app.schemas import CompanyCreate, JobCreate, JobExtractedData, JobUpdate
from app.utils.data_loader import process_source_to_markdown
from resources.prompts import JOB_EXTRACTION_SYSTEM, JOB_EXTRACTION_USER

from .company_service import CompanyService
from .llm_service_protocol import LLMServiceProtocol

logger = get_logger(__name__)


class JobService:
    def __init__(
        self,
        db: Session,
        llm_service: LLMServiceProtocol,
        company_service: CompanyService,
        background_tasks: BackgroundTasks,
    ):
        self.db = db
        self.llm_service = llm_service
        self.company_service = company_service
        self.background_tasks = background_tasks

    def _authorize_job_access(self, job: Job, current_user: User):
        """Helper to authorize if a user can access a job."""
        if job.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this job.",
            )

    async def create_job_from_source(
        self,
        *,
        current_user: User,
        source_text: Optional[str] = None,
        source_url: Optional[str] = None,
        source_file: Optional[UploadFile] = None,
    ) -> Job:
        """
        Validates raw sources, processes the valid source to markdown,
        and creates a new job.
        """
        # Validate that exactly one source is provided
        sources = [source_text, source_url, source_file]
        if sum(s is not None for s in sources) != 1:
            logger.warning(
                f"Job creation failed for user {current_user.id}: Incorrect number of sources provided."
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exactly one of source_text, source_url, or source_file must be provided.",
            )

        source_to_process = source_file or source_url or source_text

        logger.info(f"Processing source for job creation for user {current_user.id}.")
        try:
            processed_source = await process_source_to_markdown(source_to_process)
        except Exception as e:
            logger.error(
                f"Failed to process source for user {current_user.id}. Error: {e}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process the provided source.",
            ) from e

        if not processed_source or not processed_source.markdown_content:
            logger.warning(
                f"Job creation failed for user {current_user.id}: Failed to extract content from source."
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Failed to extract content from the provided source.",
            )

        job_in = JobCreate(
            source_data=processed_source.metadata,
            raw_text=processed_source.markdown_content,
        )

        # Call the original method to create the job in the DB
        return await self.create_job(current_user=current_user, job_in=job_in)

    async def create_job(self, *, current_user: User, job_in: JobCreate) -> Job:
        """
        Creates a new job from a JobCreate schema and queues it for enrichment.
        """
        logger.info(f"Creating job for user {current_user.id} from processed data.")

        # Explicitly create the Job object to prevent mass assignment vulnerabilities.
        # Only fields from JobCreate are used, and user_id/status are set securely.
        try:
            db_job = Job(
                user_id=current_user.id,
                source_data=job_in.source_data,
                raw_text=job_in.raw_text,
                status="processing",  # This job is ready for background enrichment
            )
            self.db.add(db_job)
            self.db.commit()
            self.db.refresh(db_job)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(
                f"Database error creating job for user {current_user.id}: {e}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create job in the database.",
            ) from e

        logger.info(f"Job {db_job.id} created, starting background processing.")

        # Add LLM job processing to background tasks
        self.background_tasks.add_task(self.process_job, job_id=db_job.id)

        return db_job

    async def process_job(self, job_id: int) -> None:
        """
        Processes a job in the background to extract details and link a company.
        The company creation will trigger its own background task for analysis.
        """
        with next(get_db()) as db:
            try:
                logger.info(f"Background task started for job {job_id}")
                job = db.query(Job).filter(Job.id == job_id).first()
                if not job:
                    logger.error(f"Job {job_id} not found in background task.")
                    return

                # Extract structured job data via LLM
                extracted_data = await self.llm_service.generate_structured_output(
                    system_prompt=JOB_EXTRACTION_SYSTEM,
                    user_prompt=JOB_EXTRACTION_USER,
                    output_schema=JobExtractedData,
                    input_vars={"job_details": job.raw_text},
                )
                if not extracted_data or not extracted_data.company_name:
                    raise ValueError(
                        "LLM failed to extract company name or essential details."
                    )

                # --- Link or Create Company ---
                # Use the background task's own DB session to create a fresh service
                # instance, ensuring the database operations are safe.
                company_service_bg = CompanyService(db=db, llm_service=self.llm_service)
                company = company_service_bg.create_company(
                    name=extracted_data.company_name,
                    background_tasks=self.background_tasks,
                )
                job.company_id = company.id

                # Merge LLM data into job's extracted_data
                existing_extracted = job.extracted_data or {}
                new_extracted = extracted_data.model_dump(mode="json", exclude_none=True)
                existing_extracted.update(new_extracted)
                job.extracted_data = existing_extracted
                job.status = "completed"

                db.commit()
                logger.info(
                    f"Successfully processed job {job_id} and linked company {company.id}."
                )

            except Exception as e:
                logger.error(f"Error processing job {job_id}: {e}", exc_info=True)
                db.rollback()
                job = db.query(Job).filter(Job.id == job_id).first()
                if job:
                    job.status = "failed_processing"
                    db.commit()

    def get_job_by_id(self, job_id: int, current_user: User) -> Job:
        """Retrieve a single job by its ID with authorization."""
        logger.info(f"Fetching job {job_id} for user {current_user.id}")
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
            )

        self._authorize_job_access(job, current_user)
        return job

    def get_jobs(
        self, user_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> List[Job]:
        """Retrieve a list of jobs, optionally filtered by user_id."""
        filters = []
        if user_id:
            filters.append(Job.user_id == user_id)
        return self.db.query(Job).filter(*filters).offset(skip).limit(limit).all()

    def update_job(self, job_id: int, job_in: JobUpdate, current_user: User) -> Job:
        """Updates a job's details after authorization."""
        job = self.get_job_by_id(
            job_id=job_id, current_user=current_user
        )  # This already performs the auth check

        update_data = job_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job, field, value)

        self.db.commit()
        self.db.refresh(job)
        return job

    def delete_job(self, job_id: int, current_user: User):
        """Deletes a job after authorization."""
        job = self.get_job_by_id(
            job_id=job_id, current_user=current_user
        )  # This already performs the auth check
        self.db.delete(job)
        self.db.commit()
        logger.info(f"Successfully deleted job {job_id}")

    def delete_jobs(self, job_ids: List[int], current_user: User):
        """Deletes multiple jobs after checking authorization for each."""
        if not job_ids:
            return

        # Fetch all jobs to be deleted in a single query
        jobs_to_delete = self.db.query(Job).filter(Job.id.in_(job_ids)).all()

        if len(jobs_to_delete) != len(set(job_ids)):
            # This check handles cases where some job_ids do not exist.
            # You might want to log this or handle it differently based on requirements.
            logger.warning("Some job IDs provided for deletion were not found.")

        # Authorize access for all jobs before proceeding
        for job in jobs_to_delete:
            self._authorize_job_access(job, current_user)

        # Perform the bulk deletion
        try:
            for job in jobs_to_delete:
                self.db.delete(job)
            self.db.commit()
            logger.info(f"Successfully deleted jobs with IDs: {job_ids}")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error during bulk job deletion: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not delete jobs from the database.",
            ) from e
