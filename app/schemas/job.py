""" Schemas for job management."""
from pydantic import BaseModel, Field, HttpUrl 
from typing import Optional
from datetime import datetime
from app.db.models import JobSourceType 

# --- Base Schema ---
# Represents the full data of a job object, often after processing
class JobBase(BaseModel):
    """ Base schema for job data, reflecting the DB model."""
    # Source Info (usually read-only after creation)
    source_type: Optional[JobSourceType] = None
    source_value: Optional[str] = None # URL, file path, or raw text
    source_filename: Optional[str] = None
    source_mime_type: Optional[str] = None

    # Extracted/Structured Info
    title: Optional[str] = Field(None, description="Extracted job title", example="Software Engineer")
    company: Optional[str] = Field(None, description="Extracted company name", example="Example Corp")
    location: Optional[str] = Field(None, description="Extracted job location", example="Remote")
    job_url: Optional[HttpUrl] = Field(None, description="Extracted/Provided URL of the job posting") 
    date_posted: Optional[datetime] = Field(None, description="Extracted date the job was posted")
    submission_deadline: Optional[datetime] = Field(None, description="Extracted application deadline")
    hiring_manager: Optional[str] = Field(None, description="Extracted hiring manager contact")
    status: Optional[str] = Field(None, description="Processing status", example="Ready")
    full_description: Optional[str] = Field(None, description="Extracted full job description text")

    class Config:
        """ Configure Pydantic to work with ORM and Enums."""
        from_attributes = True
        use_enum_values = True 


# --- Create Schema ---
# Used when initially adding a job from a source
class JobCreate(BaseModel):
    """ Schema for creating a new job entry from a source."""
    user_id: int
    source_type: JobSourceType
    source_value: str = Field(description="URL, raw text, or path to uploaded file.")
    # Optional for file uploads
    source_filename: Optional[str] = Field(None, description="Original filename for file uploads.")
    source_mime_type: Optional[str] = Field(None, description="MIME type for file uploads.")

    # Note: Extracted fields like title, company are NOT included here.


# --- Update Schema ---
# Used to update the *extracted* data or status of a job
class JobUpdate(BaseModel):
    """ Schema for updating the extracted fields or status of an existing job."""
    # Allow updating extracted fields
    title: Optional[str] = Field(None, description="Job title")
    company: Optional[str] = Field(None, description="Company name")
    location: Optional[str] = Field(None, description="Job location")
    job_url: Optional[HttpUrl] = Field(None, description="URL of the job posting") 
    date_posted: Optional[datetime] = Field(None, description="Date posted")
    submission_deadline: Optional[datetime] = Field(None, description="Application deadline")
    hiring_manager: Optional[str] = Field(None, description="Hiring manager")
    full_description: Optional[str] = Field(None, description="Full job description text")

    # Allow updating status
    status: Optional[str] = Field(None, description="Job processing status (e.g., Ready, Error)")

    # Generally, source_type and source_value should not be updatable via this schema.


# --- Response Schema ---
# Includes all fields from JobBase plus DB-generated fields
class JobResponse(JobBase):
    """ Schema for job response, includes IDs and timestamps."""
    id: int
    user_id: int
    time_created: Optional[datetime] = None
    time_updated: Optional[datetime] = None

    # Inherits all fields from JobBase
    # Config is inherited from JobBase