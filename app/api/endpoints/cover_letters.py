from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List

from app.db import User, Job, CoverLetter, get_db
from app.schemas.cover_letter import CoverLetterCreate, CoverLetterResponse, CoverLetterSections, CoverLetterUpdate
from app.services.gemini_service import GeminiService
import json

router = APIRouter()

gemini_service = GeminiService()

@router.post("/", response_model=CoverLetterResponse, status_code=status.HTTP_201_CREATED)
async def create_cover_letter(
    *,
    db: Session = Depends(get_db),
    user_id: int = Query(...),
    job_id: int = Query(...),
    cover_letter_in: CoverLetterCreate = Body(...)
):
    """ 
    Creates a new cover letter: 
    1. Fetches User and Job context.
    2. Calls Gemini service to generate structured sections (header+body).
    3. Saves the structured data directly to the DB's JSON column.
    """
    # 1. Fetch User Profile for context
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    # Prepare user context dict for the service
    user_profile_dict = {
        "full_name": getattr(user, 'full_name', f"{user.name} {user.surname}"), 
        "email": user.email,
        "cv_text": getattr(user, 'cv_text', None)
        # Add any other relevant fields from the User model needed by the prompt
    }

    # 2. Fetch Job Details for context
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    # Prepare job context dict for the service
    job_details_dict = {
        "title": job.title,
        "company": job.company,
        # Pass structured job_data if it exists and is useful, or specific fields
        "job_data": getattr(job, 'job_data', None)
    }
    
    # 3. Generate structured cover letter sections via Gemini Service
    try:
        # Call the asynchronous service method
        generated_sections: CoverLetterSections = await gemini_service.generate_cover_letter(
            job_details=job_details_dict,
            user_profile=user_profile_dict,
            template_name=cover_letter_in.template_name
        )
    except Exception as e:
        # Catch errors from the service (API issues, parsing, validation)
        # TODO: Add logging: logger.error(f"Gemini service failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate cover letter content: {str(e)}")

    # 4. Create and Save the new CoverLetter record to the database
    try:
        # Instantiate the SQLAlchemy model (CoverLetter from app.db.models)
        new_cover_letter = CoverLetter(
            template_name=cover_letter_in.template_name,
            # Convert the Pydantic sections object to a dict for the JSON column
            sections=generated_sections.model_dump(mode="json"), 
            user_id=user_id,
            job_id=job_id
            # time_created is handled by DB default
        )

        # Add the new record to the session
        db.add(new_cover_letter)
        # Commit the transaction to save to the database
        db.commit()
        # Refresh the instance to get the generated ID and timestamp
        db.refresh(new_cover_letter)
        # TODO: Add logging: logger.info(f"Created Cover Letter ID: {new_cover_letter.id}")

        # Return the newly created cover letter object
        # FastAPI will serialize it based on the response_model (CoverLetterResponse)
        return new_cover_letter

    except Exception as e:
        # Roll back the transaction if any database error occurs
        db.rollback()
        # TODO: Add logging: logger.error(f"Database error creating cover letter: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save cover letter to database: {str(e)}"
        )

@router.get("/{cover_letter_id}", response_model=CoverLetterResponse)
def get_cover_letter(cover_letter_id: int, db: Session = Depends(get_db)):
    """ Get cover letter by ID """
    cover_letter = db.query(CoverLetter).filter(CoverLetter.id == cover_letter_id).first()
    if cover_letter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="cover letter not found"
        )   
    return cover_letter

@router.get("/user/{user_id}", response_model=List[CoverLetterResponse])
def get_user_cover_letters(user_id: int, db: Session = Depends(get_db)):
    """ Get all cover letters for a specific user. """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get all cover letters for the user
    cover_letters = db.query(CoverLetter).filter(CoverLetter.user_id == user_id).all()
    return cover_letters

@router.get("/job/{job_id}", response_model=List[CoverLetterResponse])
def get_job_cover_letters(job_id: int, db: Session = Depends(get_db)):
    """ Get all cover letters for a specific job. """
    # Verify job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Get all cover letters for the job
    cover_letters = db.query(CoverLetter).filter(CoverLetter.job_id == job_id).all()
    return cover_letters

@router.get("/", response_model=List[CoverLetterResponse])
def list_cover_letters(db: Session = Depends(get_db)):
    """ Get all cover letters from the database. """
    cover_letters = db.query(CoverLetter).all()
    return cover_letters

@router.put("/{cover_letter_id}", response_model=CoverLetterResponse)
def update_cover_letter(
    cover_letter_id: int, 
    cover_letter_update: CoverLetterUpdate, 
    db: Session = Depends(get_db)
):
    """ Update a cover letter by ID. """
    # Verify cover letter exists
    cover_letter = db.query(CoverLetter).filter(CoverLetter.id == cover_letter_id).first()
    if not cover_letter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cover letter not found"
        )
    
    # Update cover letter fields if provided in the request
    cover_letter_data = cover_letter_update.model_dump(exclude_unset=True, mode="json")
    
    # Update cover letter attributes
    for key, value in cover_letter_data.items():
        if getattr(cover_letter, key) != value: 
            setattr(cover_letter, key, value)
    
    # Commit changes to database
    db.commit()
    db.refresh(cover_letter)
    
    return cover_letter

@router.delete("/{cover_letter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cover_letter(cover_letter_id: int, db: Session = Depends(get_db)):
    """ Delete a cover letter by ID. """
    # Verify cover letter exists
    cover_letter = db.query(CoverLetter).filter(CoverLetter.id == cover_letter_id).first()
    if not cover_letter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cover letter not found"
        )
    
    # Delete cover letter
    db.delete(cover_letter)
    db.commit()

    return None