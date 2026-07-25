# app/schemas/common.py
"""Common, shared Pydantic schemas to avoid circular imports."""

from typing import Optional

from pydantic import BaseModel


class UserAddress(BaseModel):
    """Schema for user address details."""

    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None


class UserContact(BaseModel):
    """Schema for user contact details."""

    address: Optional[UserAddress] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None
