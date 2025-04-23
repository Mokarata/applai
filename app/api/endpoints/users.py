from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import List

# Import app dependencies
from app.db import get_db, User
from app.schemas.user import UserCreate, UserResponse, UserUpdate

# Initialize APIRouter
router = APIRouter()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """ Create a new user."""
    # Check if user with email already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )

    # Hash the password
    hashed_password = pwd_context.hash(user.password)

    # Create new user with hashed password
    new_user = User(
        name=user.name,
        surname=user.surname,
        email=user.email,
        password=hashed_password,
        cv_text=user.cv_text,
    )

    # Add new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    """ Get all users from the database. """
    users = db.query(User).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """ Get user by ID form the data base."""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """ Update user by ID. """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields if provided in the request
    user_data = user_update.model_dump(exclude_unset=True)
    
    # Hash password if it's being updated
    if "password" in user_data and user_data["password"]:
        user_data["password"] = pwd_context.hash(user_data["password"])
    
    # Update user attributes
    for key, value in user_data.items():
        if getattr(user, key) != value:
            setattr(user, key, value)
    
    # Commit changes to database
    db.commit()
    db.refresh(user)
    
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """ Delete a user by ID. """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Delete user
    db.delete(user)
    db.commit()

    return None