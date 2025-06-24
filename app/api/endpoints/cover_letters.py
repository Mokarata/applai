# Python standard library - Core types
from typing import List, Optional

# FastAPI - Web framework components
from fastapi import APIRouter, Depends, HTTPException, status, Query

# App dependencies
from app.db import User
from app.core.dependencies import get_current_user

# Application schemas - Data validation 
from app.schemas.cover_letter import CoverLetterCreate, CoverLetterResponse, CoverLetterUpdate

# Application services - Business logic
from app.services.cover_letter_service import CoverLetterService

# API dependencies - Service injection
from app.api.dependencies import get_cover_letter_service

router = APIRouter()

@router.post("/", response_model=CoverLetterResponse, status_code=status.HTTP_201_CREATED)
async def create_cover_letter(
    *,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service),
    job_id: int = Query(..., description="ID of the job to base the letter on."),
    cover_letter_in: CoverLetterCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new cover letter for the authenticated user.
    Requires job_id as a query parameter and generation_options in the body.
    """
    try:
        new_cover_letter = await cover_letter_service.generate_cover_letter(
            cover_letter_data=cover_letter_in,
            user_id=current_user.id,
            job_id=job_id,
            current_user=current_user
        )
        return new_cover_letter
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/{cover_letter_id}", response_model=CoverLetterResponse)
def get_cover_letter(
    *,
    cover_letter_id: int,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service),
    current_user: User = Depends(get_current_user)
):
    """ Get a specific cover letter by ID, checking for ownership or admin rights. """
    try:
        cover_letter = cover_letter_service.get_cover_letter(
            cover_letter_id=cover_letter_id,
            current_user=current_user
        )
        return cover_letter
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[CoverLetterResponse])
def get_all_cover_letters(
    *,
    user_id: Optional[int] = None,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service),
    current_user: User = Depends(get_current_user)
):
    """ 
    Get all cover letters.
    - Non-admins can only retrieve their own.
    - Admins can retrieve for a specific user_id or all if user_id is not provided.
    """ 
    try:
        query_user_id = current_user.id if not current_user.is_admin else user_id
        cover_letters = cover_letter_service.get_cover_letters_by_user(user_id=query_user_id)
        return cover_letters
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{cover_letter_id}", response_model=CoverLetterResponse)
async def update_cover_letter(
    *,
    cover_letter_id: int,
    cover_letter_update: CoverLetterUpdate,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service),
    current_user: User = Depends(get_current_user)
):
    """ Update a cover letter by ID, checking for ownership or admin rights. """
    try:
        updated_cover_letter = await cover_letter_service.update_cover_letter(
            cover_letter_id=cover_letter_id,
            update_data=cover_letter_update,
            current_user=current_user
        )
        return updated_cover_letter
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{cover_letter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cover_letter(
    *,
    cover_letter_id: int,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service),
    current_user: User = Depends(get_current_user)
):
    """ Delete a cover letter by ID, checking for ownership or admin rights. """
    try:
        cover_letter_service.delete_cover_letter(
            cover_letter_id=cover_letter_id,
            current_user=current_user
        )
        return None
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")