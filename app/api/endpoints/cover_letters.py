from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List

from app.schemas.cover_letter import CoverLetterCreate, CoverLetterResponse, CoverLetterUpdate
from app.services.cover_letter_service import CoverLetterService
from app.api.dependencies import get_cover_letter_service

router = APIRouter()

@router.post("/", response_model=CoverLetterResponse, status_code=status.HTTP_201_CREATED)
async def create_cover_letter(
    *,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service),
    user_id: int = Query(..., description="ID of the user requesting the letter."),
    job_id: int = Query(..., description="ID of the job to base the letter on."),
    cover_letter_in: CoverLetterCreate
):
    """
    Creates a new cover letter using the CoverLetterService.
    Requires user_id and job_id as query parameters and generation_options in the body.
    """
    try:
        new_cover_letter = cover_letter_service.generate_and_save_cover_letter(
            cover_letter_data=cover_letter_in,
            user_id=user_id,
            job_id=job_id
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
    user_id: int = Query(..., description="ID of the user owning the letter."),
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service)
):
    """ Get a specific cover letter by ID for a given user. """
    try:
        cover_letter = cover_letter_service.get_cover_letter(
            cover_letter_id=cover_letter_id,
            user_id=user_id
        )
        return cover_letter
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/user/{user_id}", response_model=List[CoverLetterResponse])
def get_user_cover_letters(
    *,
    user_id: int,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service)
):
    """ Get all cover letters for a specific user. """
    try:
        cover_letters = cover_letter_service.get_cover_letters_by_user(user_id=user_id)
        return cover_letters
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{cover_letter_id}", response_model=CoverLetterResponse)
def update_cover_letter(
    *,
    cover_letter_id: int,
    user_id: int = Query(..., description="ID of the user owning the letter."),
    cover_letter_update: CoverLetterUpdate,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service)
):
    """ Update a cover letter by ID for a given user. """
    try:
        updated_cover_letter = cover_letter_service.update_cover_letter(
            cover_letter_id=cover_letter_id,
            user_id=user_id,
            update_data=cover_letter_update
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
    user_id: int = Query(..., description="ID of the user owning the letter."),
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service)
):
    """ Delete a cover letter by ID for a given user. """
    try:
        cover_letter_service.delete_cover_letter(
            cover_letter_id=cover_letter_id,
            user_id=user_id
        )
        return None
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")