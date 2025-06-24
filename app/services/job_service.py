# Python standard library - Core language functionality
import base64
import binascii
from typing import Optional, Dict, Any, List
from datetime import datetime

# FastAPI and database components - Web and persistence layers
from fastapi import HTTPException, status, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Application-specific imports - Models, schemas and services
from app.db import User, Job, JobSourceType, Company, get_db
from app.core import get_logger
from app.schemas import (
    JobCreate,
    JobUpdate,
    JobSourceData,
    JobExtractedData,
    CompanyCreate
)
from app.utils.text_processing import source_to_text
from .llm_service_protocol import LLMServiceProtocol
from .company_service import CompanyService
from resources.prompts import JOB_EXTRACTION_SYSTEM, JOB_EXTRACTION_USER

logger = get_logger(__name__)

class JobService:
    def __init__(
        self, 
        db: Session, 
        llm_service: LLMServiceProtocol, 
        company_service: CompanyService, 
        background_tasks: BackgroundTasks
    ):
        self.db = db
        self.llm_service = llm_service
        self.company_service = company_service
        self.background_tasks = background_tasks

    def _get_user(self, user_id: int) -> User:
        """Helper to get user or raise 404."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    def _authorize_job_access(self, job: Job, current_user: User):
        """Helper to authorize if a user can access a job."""
        if job.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this job."
            )

    async def create_job(
        self, 
           *, 
        user_id: int, 
        job_in: JobCreate, 
        file: Optional[UploadFile] = None
    ) -> Job:
        """ 
        Creates a new job, processes the source, and enriches the data.
        """
        logger.info(f"Unified job creation for user {user_id} from source: {job_in.source_type.value}")

        # 1. Prepare JobSourceData
        source_data_schema = JobSourceData(
            type=job_in.source_type,
            original_value=job_in.source_value,
            filename=job_in.source_filename,
            mime_type=job_in.source_mime_type
        )

        # 2. Extract text content from the source
        file_content_bytes = await file.read() if file else None
        clean_text = await source_to_text(source_data_schema, file_content_bytes)
        if not clean_text:
            raise HTTPException(status_code=400, detail="Could not extract text from the provided source.")

        # 3. Create initial Job in DB
        db_job = Job(
            user_id=user_id,
            source_data=source_data_schema.model_dump(),
            raw_text=clean_text, # Save processed text to the dedicated column
            status="processing"
        )
        self.db.add(db_job)
        self.db.commit()
        self.db.refresh(db_job)

        logger.info(f"Job {db_job.id} created, starting background processing.")

        # 4. Add LLM job processing to background tasks
        self.background_tasks.add_task(
            self.process_job, 
            job_id=db_job.id
        )

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
                    input_vars={"job_details": job.raw_text}
                )
                if not extracted_data or not extracted_data.company_name:
                    raise ValueError("LLM failed to extract company name or essential details.")

                # --- Link or Create Company ---
                # This now handles getting an existing company or creating a new one
                # and automatically triggers the analysis task for new companies.
                company = self.company_service.create_company(
                    name=extracted_data.company_name, 
                    background_tasks=self.background_tasks
                )
                job.company_id = company.id

                # Merge LLM data into job's extracted_data
                existing_extracted = job.extracted_data or {}
                new_extracted = extracted_data.model_dump(exclude_none=True)
                existing_extracted.update(new_extracted)
                job.extracted_data = existing_extracted
                job.status = "completed"
                
                db.commit()
                logger.info(f"Successfully processed job {job_id} and linked company {company.id}.")

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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        
        self._authorize_job_access(job, current_user)
        return job

    def get_jobs(self, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Job]:
        """Retrieve a list of jobs, optionally filtered by user_id."""
        filters = []
        if user_id:
            filters.append(Job.user_id == user_id)
        return self.db.query(Job).filter(*filters).offset(skip).limit(limit).all()

    def update_job(self, job_id: int, job_in: JobUpdate, current_user: User) -> Job:
        """Updates a job's details after authorization."""
        job = self.get_job_by_id(job_id=job_id, current_user=current_user) # This already performs the auth check

        update_data = job_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job, field, value)

        self.db.commit()
        self.db.refresh(job)
        return job

    def delete_job(self, job_id: int, current_user: User):
        """Deletes a job after authorization."""
        job = self.get_job_by_id(job_id=job_id, current_user=current_user) # This already performs the auth check
        self.db.delete(job)
        self.db.commit()
        logger.info(f"Successfully deleted job {job_id}")
