from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Import app dependencies
from app.db import get_db, Job, User
from app.schemas.job import JobCreate, JobResponse

# Initialize APIRouter
router = APIRouter()

@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    """ Create a new job."""
    # Verify user exists
    user = db.query(User).filter(User.id == job.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create new job
    new_job = Job(
        title=job.title,
        description=job.description,
        company=job.company,
        location=job.location,
        user_id=job.user_id
    )

    # Add new job to the database
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """ Get job by ID form the data base."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return job

@router.get("/", response_model=List[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    """ Get all jobs from the database. """
    jobs = db.query(Job).all()
    return jobs

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """ Delete a job by ID. """
    # Verify job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Delete job
    db.delete(job)
    db.commit()

    return None


