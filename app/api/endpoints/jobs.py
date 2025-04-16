from fastapi import APIRouter, Depends, HTTPException, status, File, Form, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional

# Import app dependencies
from app.db import get_db, Job, User
from app.schemas.job import JobCreate, JobResponse
from app.services.gemini_service import GeminiService

# Initialize APIRouter
router = APIRouter()

def clean_job_data(data):
    """Clean job data to handle various input formats.
    
    Args:
        data (str): Raw job data text that may contain problematic characters
        
    Returns:
        str: Cleaned job data with problematic control characters removed
    """
    if not data:
        return ""
    
    # Remove any control characters that might cause JSON parsing issues
    # but preserve newlines, tabs, and carriage returns
    return ''.join(char for char in data if ord(char) >= 32 or char in '\n\r\t')

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
    # Clean job_data to handle various input formats
    job_data_cleaned = clean_job_data(job.job_data)
    
    # Extract job data if title, company or location are not provided
    if not job.title or not job.company or not job.location:
        try:
            # Use Gemini to extract job data
            gemini_service = GeminiService()
            extracted_data = gemini_service.extract_job_data(job_data_cleaned)
            
            # Use extracted data or defaults
            job_title = job.title or extracted_data.get("title", "Untitled Position")
            job_company = job.company or extracted_data.get("company", "Unknown Company")
            job_location = job.location or extracted_data.get("location", "Remote/Unspecified")
        except Exception as e:
            # Log the error but continue with default values
            print(f"Error extracting job data: {str(e)}")
            job_title = job.title or "Untitled Position"
            job_company = job.company or "Unknown Company"
            job_location = job.location or "Remote/Unspecified"
    else:
        # Use provided values
        job_title = job.title
        job_company = job.company
        job_location = job.location
    
    # Create new job
    new_job = Job(
        title=job_title,
        job_data=job_data_cleaned,
        company=job_company,
        location=job_location,
        user_id=job.user_id
    )

    # Add new job to the database
    db.add(new_job)
    db.commit()
    db.refresh(new_job) # Refresh the new job to get the generated ID

    return new_job

@router.post("/upload", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job_from_file(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    title: Optional[str] = Form(None),
    company: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Create a job from an uploaded file.
    
    This endpoint allows you to upload a markdown file containing the job description
    instead of pasting the content directly into the request body.
    """
    # Read file contents
    job_data = await file.read()
    job_data = job_data.decode("utf-8")
    
    # Create JobCreate object
    job = JobCreate(
        job_data=job_data,
        user_id=user_id,
        title=title,
        company=company,
        location=location
    )
    
    # Use existing create_job function
    return create_job(job, db)

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
