""" Schemas for user management."""
from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserAddress(BaseModel):
    """ Schema for user address details."""
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None

class UserContact(BaseModel):
    """ Schema for user contact details."""
    address: Optional[UserAddress] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None

class UserBase(BaseModel):
    """ Base user model """
    name: str
    surname: str
    user_name: str
    email: str
    contact_info: Optional[UserContact] = None
    cv_text: Optional[str] = None
    is_active: Optional[bool] = True
    is_admin: Optional[bool] = False

class UserCreate(UserBase):
    """ Schema for creating a new user """
    password: str

class UserUpdate(BaseModel):
    """ Schema for updating an existing user """
    name: Optional[str] = None
    surname: Optional[str] = None
    user_name: Optional[str] = None
    email: Optional[str] = None
    cv_text: Optional[str] = None
    contact_info: Optional[UserContact] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

class UserResponse(UserBase):
    """ Schema for user response, include ID and status."""
    id: int
    is_active: bool
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)