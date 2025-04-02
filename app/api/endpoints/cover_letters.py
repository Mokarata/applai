from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import CoverLetter, User, Job, get_db
from app.schemas.cover_letter import CoverLetterCreate, CoverLetterResponse

router = APIRouter()

@router.post("/", response_model=CoverLetterResponse, status_code=status.HTTP_201_CREATED)
def create_cover_letter(
    cover_letter: CoverLetterCreate,
    user_id: int,
    job_id: int,
    db: Session = Depends(get_db)
):
    """ Creates a new cover letter for a specific job and user. """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Create new cover letter
    new_cover_letter = CoverLetter(
        template_name=cover_letter.template_name,
        cover_letter_text=cover_letter.cover_letter_text,
        user_id=user_id,
        job_id=job_id
    )
    
    # Add to database
    try:
        db.add(new_cover_letter)
        db.commit()
        db.refresh(new_cover_letter)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create cover letter: {str(e)}"
        )
    
    return new_cover_letter

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
