""" Schemas for job management."""
from pydantic import BaseModel
from typing import Optional

class JobBase(BaseModel):
    """ Base schema for job data."""
    title: str
    description: str
    company: str
    location: str
    
class JobCreate(JobBase):
    """ Schema for creating a new job."""
    user_id: int

class JobResponse(JobBase):
    """ Schema for job response, include ID and status."""
    id: int
    user_id: int

    class Config:
        """ Configure Pydantic to work with ORM."""
        from_attributes = True