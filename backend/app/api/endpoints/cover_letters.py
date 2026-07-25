# Python standard library - Core types
from typing import List, Optional

# FastAPI - Web framework components
from fastapi import APIRouter, Depends, HTTPException, Query, status

# API dependencies - Service injection
from app.api.dependencies import get_cover_letter_service
from app.core.dependencies import get_current_user
# App dependencies
from app.db import User
# Application schemas - Data validation
from app.schemas.cover_letter import (CoverLetterCreate, CoverLetterDelete,
                                      CoverLetterGenerationResponse,
                                      CoverLetterResponse, CoverLetterUpdate)
# Application services - Business logic
from app.services.cover_letter_service import CoverLetterService

router = APIRouter()


@router.post("/generate", response_model=CoverLetterGenerationResponse)
async def generate_cover_letter_only(
    *,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service),
    job_id: int = Query(..., description="ID of the job to base the letter on."),
    cover_letter_in: CoverLetterCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Generates a cover letter without saving it to the database.
    """
    try:
        generated_instance = await cover_letter_service.generate_cover_letter_instance(
            cover_letter_data=cover_letter_in,
            user_id=current_user.id,
            job_id=job_id,
        )
        return generated_instance
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during generation: {str(e)}",
        )


@router.post(
    "/", response_model=CoverLetterResponse, status_code=status.HTTP_201_CREATED
)
async def create_cover_letter(
    *,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service),
    job_id: int = Query(..., description="ID of the job to base the letter on."),
    cover_letter_in: CoverLetterCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Generate a cover letter for the given job and save it to the database.
    """
    try:
        # First, generate the cover letter instance (unsaved)
        generated_instance = await cover_letter_service.generate_cover_letter_instance(
            cover_letter_data=cover_letter_in,
            user_id=current_user.id,
            job_id=job_id,
        )

        # Prepare data to persist using the existing create service
        from app.schemas.cover_letter import CoverLetterCreate as CLC
        from app.schemas.cover_letter import (CoverLetterStructure,
                                              GenerationOptions)

        save_payload = CLC(
            title=generated_instance.title,
            sections=(
                CoverLetterStructure(**generated_instance.sections)
                if generated_instance.sections
                else None
            ),
            text=generated_instance.text,
            generation_options=(
                GenerationOptions(**generated_instance.generation_options)
                if generated_instance.generation_options
                else None
            ),
            job_id=job_id,
            llm_service_used=generated_instance.llm_service_used,
        )

        saved_letter = cover_letter_service.create_cover_letter(
            cover_letter_data=save_payload,
            user_id=current_user.id,
            current_user=current_user,
        )
        return saved_letter
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while generating or saving: {str(e)}",
        )


@router.get("/{cover_letter_id}", response_model=CoverLetterResponse)
def get_cover_letter(
    *,
    cover_letter_id: int,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service),
    current_user: User = Depends(get_current_user),
):
    """Get a specific cover letter by ID, checking for ownership or admin rights."""
    try:
        cover_letter = cover_letter_service.get_cover_letter(
            cover_letter_id=cover_letter_id, current_user=current_user
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
    current_user: User = Depends(get_current_user),
):
    """
    Get all cover letters.
    - Non-admins can only retrieve their own.
    - Admins can retrieve for a specific user_id or all if user_id is not provided.
    """
    try:
        query_user_id = current_user.id if not current_user.is_admin else user_id
        cover_letters = cover_letter_service.get_cover_letters_by_user(
            user_id=query_user_id
        )
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
    current_user: User = Depends(get_current_user),
):
    """Update a cover letter by ID, checking for ownership or admin rights."""
    try:
        updated_cover_letter = await cover_letter_service.update_cover_letter(
            cover_letter_id=cover_letter_id,
            update_data=cover_letter_update,
            current_user=current_user,
        )
        return updated_cover_letter
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_cover_letters(
    *,
    letters_to_delete: CoverLetterDelete,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service),
    current_user: User = Depends(get_current_user),
):
    """Delete one or more cover letters by their IDs."""
    try:
        cover_letter_service.delete_cover_letters(
            cover_letter_ids=letters_to_delete.cover_letter_ids,
            current_user=current_user,
        )
        return None
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
