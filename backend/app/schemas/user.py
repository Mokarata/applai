"""Schemas for user management."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .common import UserContact
from .cv_extraction import CVData


class UserBase(BaseModel):
    """Base user model"""

    name: str
    surname: str
    user_name: str
    email: str
    contact_info: Optional[UserContact] = None
    structured_cv_data: Optional[CVData] = None
    cv_text: Optional[str] = None
    cv_source_metadata: Optional[dict] = None
    is_active: Optional[bool] = True
    is_admin: Optional[bool] = False


class UserCreate(BaseModel):
    """Schema for creating a new user"""

    name: str
    surname: str
    user_name: str
    email: str
    password: str
    is_admin: Optional[bool] = False


class UserUpdate(UserBase):
    """Schema for updating an existing user"""

    name: Optional[str] = Field(default=None, description="User's name")
    surname: Optional[str] = Field(default=None, description="User's surname")
    user_name: Optional[str] = Field(default=None, description="User's username")
    email: Optional[str] = Field(default=None, description="User's email")
    cv_text: Optional[str] = Field(default=None, description="User's CV text")
    cv_source_metadata: Optional[dict] = Field(
        default=None, description="Metadata from the processed CV source"
    )
    structured_cv_data: Optional[CVData] = Field(
        default=None, description="Structured data extracted from the user's CV"
    )
    contact_info: Optional[UserContact] = Field(
        default=None, description="User's contact information"
    )
    password: Optional[str] = Field(default=None, description="User's password")
    is_active: Optional[bool] = Field(default=None, description="User's active status")
    is_admin: Optional[bool] = Field(default=None, description="User's admin status")


class UserResponse(UserBase):
    """Schema for user response, include ID and status."""

    id: int
    is_active: bool
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)
