""" Schemas for job management."""
from pydantic import BaseModel
from typing import Optional

# Base schema defines common fields for job
class JobBase(BaseModel):
    """ Base schema for job data."""
    title: str
    description: str
    company: str
    location: str
    
# Create schemas: add fields required for creation 
class JobCreate(JobBase):
    """ Schema for creating a new job."""
    user_id: int

# Response schemas: add fields required for response
class JobResponse(JobBase):
    """ Schema for job response, include ID and status."""
    id: int
    user_id: int

    class Config:
        """ Configure Pydantic to work with ORM."""
        from_attributes = True