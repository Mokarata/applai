from fastapi import APIRouter, Depends, HTTPException, status, File, Form, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import re
from datetime import datetime

# Import app dependencies
from app.db import get_db, Job, User, JobSourceType
from app.schemas.job import JobCreate, JobResponse, JobUpdate
from app.services.job_service import JobService

# Initialize APIRouter
router = APIRouter()

# Dependency for JobService (injects db session)
def get_job_service(db: Session = Depends(get_db)) -> JobService:
    return JobService(db)

@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_input: JobCreate,
    job_service: JobService = Depends(get_job_service) # Inject service
):
    """ Create a new job based on source type using JobService."""
    # Delegate core logic to the service
    # Exceptions raised in the service (like 404, 400, 501) will propagate
    return job_service.create_job_from_schema(job_input)


@router.post("/upload", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job_from_file(
    # Keep File and Form parameters as they define the request structure
    file: UploadFile = File(...),
    user_id: int = Form(...),
    title: Optional[str] = Form(None),
    company: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    job_url: Optional[str] = Form(None),
    date_posted: Optional[datetime] = Form(None),
    submission_deadline: Optional[datetime] = Form(None),
    hiring_manager: Optional[str] = Form(None),
    status: Optional[str] = Form("pending"),
    # Inject service
    job_service: JobService = Depends(get_job_service)
):
    """Create a job from an uploaded file using JobService."""
    # Collect form data into a dictionary to pass to the service
    form_data = {
        "title": title,
        "company": company,
        "location": location,
        "job_url": job_url,
        "date_posted": date_posted,
        "submission_deadline": submission_deadline,
        "hiring_manager": hiring_manager,
        "status": status,
    }
    # Delegate core logic to the service
    return await job_service.create_job_from_file(
        file=file,
        user_id=user_id,
        form_data=form_data
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    job_service: JobService = Depends(get_job_service)
):
    """Retrieve a specific job by its ID using JobService."""
    # Delegate to service, handles 404
    return job_service.get_job_by_id(job_id)


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_update: JobUpdate,
    job_service: JobService = Depends(get_job_service) # Inject service
):
     """Update an existing job using JobService."""
     # Delegate to service, handles 404 and update logic
     return job_service.update_job(job_id, job_update)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    job_service: JobService = Depends(get_job_service)
):
    """Delete a specific job by its ID using JobService."""
    # Delegate to service, handles 404
    job_service.delete_job(job_id)
    return None # Return None for 204 status code


@router.get("/", response_model=List[JobResponse])
def get_all_jobs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    job_service: JobService = Depends(get_job_service)
):
    """Retrieve all jobs using JobService, optionally filtered by user_id."""
    # Delegate to service
    return job_service.get_jobs(user_id=user_id, skip=skip, limit=limit)
