""" Schemas for cover letter management."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CoverLetterBase(BaseModel):
    """ Base schema for cover letter data."""
    template_name: str
    cover_letter_text: str

class CoverLetterCreate(CoverLetterBase):
    """ Schema for creating a new cover letter."""
    pass

class CoverLetterResponse(CoverLetterBase):
    """ Schema for cover letter response, include IDs and creation time."""
    id: int
    user_id: int
    job_id: int
    time_created: datetime

    class Config:
        """ Configure Pydantic to work with ORM."""
        from_attributes = True