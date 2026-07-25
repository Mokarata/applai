from typing import List, Optional

from fastapi import (APIRouter, Depends, File, Form, HTTPException, UploadFile,
                     status)

from app.api.dependencies import get_job_service
from app.core import get_logger
from app.core.dependencies import get_current_user
# Import app dependencies
from app.db import User, get_db
from app.schemas.job import JobCreate, JobDelete, JobResponse, JobUpdate
from app.services.job_service import JobService

# Initialize APIRouter
router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    source_text: Optional[str] = Form(
        None, description="The raw text of the job description."
    ),
    source_url: Optional[str] = Form(None, description="The URL of the job posting."),
    source_files: UploadFile = File(
        None, description="A file containing the job description (e.g., PDF, TXT)."
    ),
    job_service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new job from one of three sources: raw text, a URL, or an uploaded file.

    - **Provide exactly one source:** `source_text`, `source_url`, or `source_file`.
    - This endpoint delegates the source processing and job creation to the service layer.
    """
    logger.info(f"Received request to create job for user {current_user.id}")
    return await job_service.create_job_from_source(
        current_user=current_user,
        source_text=source_text,
        source_url=source_url,
        source_file=source_files,
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    job_service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a specific job by its ID, checking for ownership or admin rights."""
    logger.info(f"Received request to get job {job_id} for user {current_user.id}")
    return job_service.get_job_by_id(job_id=job_id, current_user=current_user)


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_update: JobUpdate,
    job_service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user),
):
    """Update an existing job, checking for ownership or admin rights."""
    return job_service.update_job(
        job_id=job_id, job_in=job_update, current_user=current_user
    )


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    job_service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user),
):
    """Delete a single job by its ID, checking for ownership or admin rights."""
    job_service.delete_job(job_id=job_id, current_user=current_user)
    return None


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_jobs(
    jobs_to_delete: JobDelete,
    job_service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user),
):
    """Delete one or more jobs by their IDs, checking for ownership or admin rights."""
    job_service.delete_jobs(job_ids=jobs_to_delete.job_ids, current_user=current_user)
    return None


@router.get("/", response_model=List[JobResponse])
def get_all_jobs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    job_service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user),
):
    """Retrieve jobs. Non-admins can only retrieve their own jobs."""
    # If the user is not an admin, force the query to only their user_id
    if not current_user.is_admin:
        user_id = current_user.id

    # Admins can optionally filter by any user_id, or get all if user_id is None
    return job_service.get_jobs(user_id=user_id, skip=skip, limit=limit)
