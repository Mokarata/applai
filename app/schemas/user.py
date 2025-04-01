""" Schemas for user management."""
from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    """ Base user model """
    name: str
    surname: str
    email: str
    cv_text: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    """ Schema for creating a new user """
    password: str

class UserResponse(UserBase):
    """ Schema for user response, include ID and status."""
    id: int
    is_active: bool

    class Config:
        """ Configure Pydantic to work with ORM."""
        orm_mode = True