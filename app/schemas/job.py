""" Schemas for job management."""
from pydantic import BaseModel, Field
from typing import Optional

# Base schema defines common fields for job
class JobBase(BaseModel):
    """ Base schema for job data."""
    title: str
    job_data: str
    company: str
    location: str
    
# Create schemas: add fields required for creation 
class JobCreate(BaseModel):
    """ Schema for creating a new job."""
    job_data: str = Field(
        description="The job data text is the raw job offer text. Can be in markdown format.",
        example="# Software Engineer\n\n**Company:** Example Corp\n**Location:** Remote"
    )
    user_id: int
    title: Optional[str] = Field(None, description="Job title (optional)", example="Software Engineer")
    company: Optional[str] = Field(None, description="Company name (optional)", example="Example Corp")
    location: Optional[str] = Field(None, description="Job location (optional)", example="Remote")

# Update schema: for updating existing jobs
class JobUpdate(BaseModel):
    """ Schema for updating an existing job."""
    title: Optional[str] = Field(None, description="Job title", example="Senior Software Engineer")
    job_data: Optional[str] = Field(
        None,
        description="The job data text is the raw job offer text. Can be in markdown format.",
        example="# Senior Software Engineer\n\n**Company:** Example Corp\n**Location:** Remote"
    )
    company: Optional[str] = Field(None, description="Company name", example="Example Corp")
    location: Optional[str] = Field(None, description="Job location", example="Remote")

# Response schemas: add fields required for response
class JobResponse(JobBase):
    """ Schema for job response, include ID and status."""
    id: int
    user_id: int

    class Config:
        """ Configure Pydantic to work with ORM."""
        from_attributes = True