from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.db import User, Job, JobSourceType
from app.schemas.job import JobCreate, JobUpdate
from app.services.gemini_service import GeminiService
from app.utils.text_processing import process_job_data
# Potentially import logger if we want structured logging
# import logging
# logger = logging.getLogger(__name__)

class JobService:
    def __init__(self, db: Session):
        self.db = db
        self.gemini_service = GeminiService() # Instantiate Gemini service

    def _get_user(self, user_id: int) -> User:
        """Helper to get user or raise 404."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    def _extract_data_conditionally(
        self,
        processed_description: Optional[str],
        current_title: Optional[str],
        current_company: Optional[str]
    ) -> Dict[str, Any]:
        """Helper to extract data using Gemini if needed."""
        extracted_data = {}
        if processed_description and (not current_title or not current_company):
            try:
                extracted_data = self.gemini_service.extract_job_data(processed_description)
            except Exception as e:
                # Log warning instead of failing the request
                print(f"Warning: Error extracting job data: {str(e)}")
                # logger.warning(f"Error extracting job data: {str(e)}", exc_info=True)
        return extracted_data

    def _consolidate_and_create_job(self, job_data: Dict[str, Any]) -> Job:
        """Helper to filter None values and create/commit the Job object."""
         # Filter out None values before creating the model instance
        job_data_filtered = {k: v for k, v in job_data.items() if v is not None}

        # Create and add the job
        new_job = Job(**job_data_filtered)
        self.db.add(new_job)
        self.db.commit()
        self.db.refresh(new_job)
        return new_job

    def create_job_from_schema(self, job_input: JobCreate) -> Job:
        """Creates a job from a JobCreate schema (text, manual, url sources)."""
        user = self._get_user(job_input.user_id)

        processed_description = None
        source_value = job_input.source_value # Keep original source value

        # --- Handle different source types ---
        if job_input.source_type == JobSourceType.text:
            if not job_input.source_value:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Source value is required for text source type.")
            processed_description = process_job_data(job_input.source_value)
        elif job_input.source_type == JobSourceType.manual:
            processed_description = process_job_data(job_input.full_description) if job_input.full_description else None
        elif job_input.source_type == JobSourceType.url:
            # TODO: Implement URL fetching logic here
            # Example:
            # try:
            #     content = fetch_url_content(job_input.source_value) # Needs implementation
            #     processed_description = process_job_data(content)
            # except Exception as e:
            #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Could not process URL: {e}")
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="URL source type not yet implemented.")
        elif job_input.source_type == JobSourceType.file:
             # This method shouldn't handle files directly
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Internal Error: File source type should use create_job_from_file.")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid source type.")

        # --- Extract job data if needed ---
        extracted_data = self._extract_data_conditionally(
            processed_description,
            job_input.title,
            job_input.company
        )

        # --- Consolidate job details ---
        job_title = job_input.title or extracted_data.get("title")
        job_company = job_input.company or extracted_data.get("company")
        job_location = job_input.location or extracted_data.get("location")
        job_url = job_input.job_url or extracted_data.get("job_url")

        # --- Prepare Job model data ---
        new_job_data = {
            "user_id": job_input.user_id,
            "source_type": job_input.source_type,
            "source_value": source_value,
            "source_filename": job_input.source_filename, # Likely None for these types
            "source_mime_type": job_input.source_mime_type, # Likely None
            "title": job_title,
            "company": job_company,
            "location": job_location,
            "job_url": job_url,
            "date_posted": job_input.date_posted,
            "submission_deadline": job_input.submission_deadline,
            "hiring_manager": job_input.hiring_manager,
            "status": job_input.status or "pending",
            "full_description": processed_description,
        }

        return self._consolidate_and_create_job(new_job_data)


    async def create_job_from_file(
        self,
        file: UploadFile,
        user_id: int,
        form_data: Dict[str, Any] # Contains title, company, etc. from Form()
    ) -> Job:
        """Creates a job from an uploaded file and form data."""
        user = self._get_user(user_id)

        # Read file contents and metadata
        try:
            job_data_bytes = await file.read()
            job_data = job_data_bytes.decode("utf-8") # Raw content
            filename = file.filename
            mime_type = file.content_type
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error reading file: {e}")
        finally:
             # Ensure file is closed even if errors occur
            await file.close()


        # Process job data for full_description
        processed_description = process_job_data(job_data)

        # --- Extract job data if needed ---
        extracted_data = self._extract_data_conditionally(
            processed_description,
            form_data.get("title"),
            form_data.get("company")
        )

        # --- Consolidate job details ---
        job_title = form_data.get("title") or extracted_data.get("title")
        job_company = form_data.get("company") or extracted_data.get("company")
        job_location = form_data.get("location") or extracted_data.get("location")
        job_url = form_data.get("job_url") or extracted_data.get("job_url")

        # --- Prepare Job model data ---
        new_job_data = {
            "user_id": user_id,
            "source_type": JobSourceType.file,
            "source_value": job_data, # Store raw file content
            "source_filename": filename,
            "source_mime_type": mime_type,
            "title": job_title,
            "company": job_company,
            "location": job_location,
            "job_url": job_url,
            "date_posted": form_data.get("date_posted"),
            "submission_deadline": form_data.get("submission_deadline"),
            "hiring_manager": form_data.get("hiring_manager"),
            "status": form_data.get("status") or "pending",
            "full_description": processed_description,
        }

        return self._consolidate_and_create_job(new_job_data)

    def get_job_by_id(self, job_id: int) -> Job:
        """Retrieve a specific job by its ID or raise 404."""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        return job

    def get_jobs(
        self,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Job]:
        """Retrieve a list of jobs, optionally filtered by user_id."""
        query = self.db.query(Job)
        if user_id:
            # Ensure user exists if filtering by user_id (optional check)
            # self._get_user(user_id)
            query = query.filter(Job.user_id == user_id)
        jobs = query.offset(skip).limit(limit).all()
        return jobs

    def update_job(self, job_id: int, job_update: JobUpdate) -> Job:
        """Update an existing job."""
        db_job = self.get_job_by_id(job_id) # Reuse get_job_by_id to handle 404

        update_data = job_update.model_dump(exclude_unset=True)

        # Update specific fields if provided
        for key, value in update_data.items():
             # Optional: Add logic here to prevent updating certain fields if needed
             # e.g., if key in ['source_type', 'source_value']: continue
            setattr(db_job, key, value)

        # Optional: Re-process description if it's updated?
        if "full_description" in update_data and update_data["full_description"] is not None:
            # Current behavior: trusts the incoming description
            # Alternative: re-process it
            # db_job.full_description = process_job_data(update_data["full_description"])
            pass

        self.db.commit()
        self.db.refresh(db_job)
        return db_job

    def delete_job(self, job_id: int) -> None:
        """Delete a specific job by its ID."""
        db_job = self.get_job_by_id(job_id) # Reuse get_job_by_id to handle 404
        self.db.delete(db_job)
        self.db.commit()
        # No return needed for delete operation (usually 204 No Content response)
