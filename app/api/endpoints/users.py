from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Import app dependencies
from app.db import get_db 
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.db.models import User
from app.services import UserService 
from app.core.dependencies import get_current_user, get_current_admin_user
from app.db.models import User

# Initialize APIRouter
router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """ Create a new user."""
    user_service = UserService(db)
    return user_service.create_user(user_in=user_in)

@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), admin_user: User = Depends(get_current_admin_user)):
    """ Get all users from the database. Admin only."""
    user_service = UserService(db)
    return user_service.get_users()

@router.get("/me", response_model=UserResponse)
def get_logged_user(current_user: UserResponse = Depends(get_current_user)):
    """Fetch the current logged in user's profile."""
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserResponse = Depends(get_current_user)
):
    """ Get user by ID from the database. Only allows a user to fetch their own data or an admin to fetch any user."""
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's information"
        )
    user_service = UserService(db)
    db_user = user_service.get_user_by_id(user_id=user_id)
    if db_user is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, 
    user_update_in: UserUpdate, 
    db: Session = Depends(get_db), 
    current_user: UserResponse = Depends(get_current_user)
):
    """ Update user by ID. Only allows a user to update their own data or an admin to update any user."""
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user's information"
        )
    user_service = UserService(db)
    return user_service.update_user(user_id=user_id, user_in=user_update_in, current_user=current_user)


@router.put("/{user_id}/cv", response_model=UserResponse, description="Update user's CV from form data.")
def update_user_cv_from_form(
    user_id: int,
    cv_text: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update user's CV from form data to handle multi-line text easily."""
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user's information",
        )

    user_service = UserService(db)
    user_update_in = UserUpdate(cv_text=cv_text)
    return user_service.update_user(
        user_id=user_id, user_in=user_update_in, current_user=current_user
    )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserResponse = Depends(get_current_user)
):
    """ Delete a user by ID. Only allows a user to delete their own account or an admin to delete any user."""
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user's information"
        )
    user_service = UserService(db)
    deleted_user = user_service.delete_user(user_id=user_id)
    if deleted_user is None: 
        pass 
    return None 