from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Form
from typing import Optional, List

# Import app dependencies
from app.db import get_db, User, JobSourceType
from app.schemas.job import JobCreate, JobResponse, JobUpdate
from app.services.job_service import JobService
from app.core.dependencies import get_current_user
from app.api.dependencies import get_job_service

# Initialize APIRouter
router = APIRouter()

@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    source_text: Optional[str] = Form(None, description="The raw text of the job description."),
    source_url: Optional[str] = Form(None, description="The URL of the job posting."),
    source_files: List[UploadFile] = File([], description="A file containing the job description (e.g., PDF, TXT)."),
    job_service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new job from one of three sources: raw text, a URL, or an uploaded file.

    - **Provide exactly one source:** `source_text`, `source_url`, or `source_file`.
    - The service will automatically determine the source type and process the job.
    """
    # Handle file input
    if source_files and len(source_files) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only one file can be uploaded at a time."
        )
    source_file = source_files[0] if source_files else None

    # Validate that exactly one source is provided
    sources = [source_text, source_url, source_file]
    if sum(s is not None for s in sources) != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exactly one of source_text, source_url, or source_file must be provided."
        )

    # Prepare the JobCreate schema based on the provided source
    if source_file:
        job_in = JobCreate(
            source_type=JobSourceType.file,
            source_value=source_file.filename, # Use filename as the initial value
            source_filename=source_file.filename,
            source_mime_type=source_file.content_type
        )
    elif source_url:
        job_in = JobCreate(
            source_type=JobSourceType.url,
            source_value=source_url
        )
    else: # source_text
        job_in = JobCreate(
            source_type=JobSourceType.text,
            source_value=source_text
        )

    # Create the job using the service layer
    return await job_service.create_job(
        job_in=job_in, 
        user_id=current_user.id, 
        file=source_file
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    job_service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user)
):
    """Retrieve a specific job by its ID, checking for ownership or admin rights."""
    return job_service.get_job_by_id(job_id=job_id, current_user=current_user)


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_update: JobUpdate,
    job_service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user)
):
     """Update an existing job, checking for ownership or admin rights."""
     return job_service.update_job(job_id=job_id, job_in=job_update, current_user=current_user)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    job_service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user)
):
    """Delete a specific job by its ID, checking for ownership or admin rights."""
    job_service.delete_job(job_id=job_id, current_user=current_user)
    return None


@router.get("/", response_model=List[JobResponse])
def get_all_jobs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    job_service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user)
):
    """Retrieve jobs. Non-admins can only retrieve their own jobs."""
    # If the user is not an admin, force the query to only their user_id
    if not current_user.is_admin:
        user_id = current_user.id
    
    # Admins can optionally filter by any user_id, or get all if user_id is None
    return job_service.get_jobs(user_id=user_id, skip=skip, limit=limit)
