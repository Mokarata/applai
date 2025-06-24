# app/services/user_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional

from app.db import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> User:
        """Retrieve a user by ID or raise 404."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user by their username."""
        return self.db.query(User).filter(User.user_name == username).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Retrieve a list of users."""
        return self.db.query(User).offset(skip).limit(limit).all()

    def create_user(self, user_in: UserCreate) -> User:
        """Create a new user."""
        db_user_by_email = self.get_user_by_email(user_in.email)
        if db_user_by_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        db_user_by_username = self.get_user_by_username(user_in.user_name)
        if db_user_by_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        user_data = user_in.model_dump(exclude_unset=True)
        hashed_password = get_password_hash(user_data.pop('password'))
        
        db_user = User(**user_data, hashed_password=hashed_password)

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def update_user(self, user_id: int, user_in: UserUpdate, current_user: User) -> User:
        """Update an existing user, with authorization checks."""
        db_user = self.get_user_by_id(user_id) # Reuse get method for 404 check

        # Update user data
        update_data = user_in.model_dump(exclude_unset=True)

        # Authorization: Prevent non-admins from making another user an admin
        if 'is_admin' in update_data and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can change admin status."
            )

        # Update password if provided
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            db_user.hashed_password = hashed_password
            del update_data["password"] # Remove password from dict after hashing

        # Update email if provided
        if "email" in update_data and update_data["email"] != db_user.email:
             existing_user = self.get_user_by_email(update_data["email"])
             if existing_user and existing_user.id != user_id:
                 raise HTTPException(status_code=400, detail="Email already registered by another user.")
             # No need to delete from update_data if we are setting it below

        # Update other fields if provided
        for field, value in update_data.items():
            if hasattr(db_user, field):
                setattr(db_user, field, value)

        # Commit changes
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete_user(self, user_id: int) -> None:
         """Delete a user by ID."""
         db_user = self.get_user_by_id(user_id)
         # Add cascade delete check or related object handling if necessary
         # e.g., delete associated jobs/cover letters or handle FK constraints
         self.db.delete(db_user)
         self.db.commit()
