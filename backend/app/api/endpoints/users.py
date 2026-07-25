# app/api/endpoints/users.py
import logging
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.dependencies import get_user_service
from app.core import get_logger
from app.core.dependencies import get_current_admin_user, get_current_user
from app.db.models import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

# Initialize APIRouter and logger
router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate, user_service: UserService = Depends(get_user_service)
):
    """Create a new user."""
    logger.info(f"Received request to create user with email: {user_in.email}")
    return user_service.create_user(user_in=user_in)


@router.get("/", response_model=List[UserResponse])
def get_users(
    user_service: UserService = Depends(get_user_service),
    admin_user: User = Depends(get_current_admin_user),
):
    """Get all users from the database. Admin only."""
    return user_service.get_users()


@router.get("/me", response_model=UserResponse)
def get_logged_user(current_user: UserResponse = Depends(get_current_user)):
    """Fetch the current logged in user's profile."""
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: UserResponse = Depends(get_current_user),
):
    """Get user by ID. User can fetch their own data; admin can fetch any."""
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's information",
        )
    db_user = user_service.get_user_by_id(user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return db_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update_in: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: UserResponse = Depends(get_current_user),
):
    """Update user by ID. User can update their own data; admin can update any."""
    if current_user.id != user_id and not current_user.is_admin:
        logger.warning(
            f"Authorization failed: User {current_user.id} attempted to update user {user_id}."
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user's information",
        )
    logger.info(f"Received request to update user {user_id}")
    return user_service.update_user(
        user_id=user_id, user_in=user_update_in, current_user=current_user
    )


@router.post("/{user_id}/cv", response_model=UserResponse)
async def upload_user_cv(
    user_id: int,
    cv_file: UploadFile = File(...),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    """
    Upload and process a user's CV.

    This endpoint accepts a CV file (PDF, DOCX, TXT, MD), processes it to extract
    raw text and metadata, and then uses an LLM to parse the text into a
    structured format (`CVData`). The results are saved to the user's profile.
    """
    if current_user.id != user_id and not current_user.is_admin:
        logger.warning(
            f"Authorization failed: User {current_user.id} attempted to upload CV for user {user_id}."
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to upload a CV for this user.",
        )

    logger.info(f"Received request to upload CV for user {user_id}")
    return await user_service.process_user_cv(
        user_id=user_id, cv_file=cv_file, current_user=current_user
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: UserResponse = Depends(get_current_user),
):
    """Delete a user by ID. User can delete their own account; admin can delete any."""
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user",
        )
    user_service.delete_user(user_id=user_id)
    return None
