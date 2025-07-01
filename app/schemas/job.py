"""Schemas for job management."""

from datetime import date, datetime
from typing import Dict, Optional

from pydantic import (BaseModel, ConfigDict, Field, HttpUrl, field_validator)


class JobExtractedData(BaseModel):
    """Schema for extracted job data via llm processing."""

    title: Optional[str] = Field(
        None,
        description="Extracted job title",
        examples=["Software Engineer", "Senior Software Engineer"],
    )
    company_name: Optional[str] = Field(
        None,
        description="Extracted company name",
        examples=["Tech Solutions Inc.", "Example Corp"],
    )
    location: Optional[str] = Field(
        None,
        description="Extracted job location",
        examples=["San Francisco, CA or Remote", "New York, NY or Remote"],
    )
    job_url: Optional[HttpUrl] = Field(
        None,
        description="URL of the job posting",
        examples=["https://example.com/jobs/123", "https://example.com/jobs/456"],
    )
    date_posted: Optional[date] = Field(
        None,
        description="Date the job was posted",
        examples=["2023-01-01", "2023-01-02"],
    )

    @field_validator("date_posted", mode='before')
    @classmethod
    def normalize_date(cls, v):
        """Normalize date from different formats into a standard date object."""
        if v is None or isinstance(v, date):
            return v
        if isinstance(v, str):
            for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
                try:
                    return datetime.strptime(v, fmt).date()
                except ValueError:
                    continue  # Try the next format
        raise ValueError(f"Unable to parse date from: {v}")
    submission_deadline: Optional[datetime] = Field(
        None,
        description="Application submission deadline",
        examples=["2023-01-01", "2023-01-02"],
    )
    hiring_manager_name: Optional[str] = Field(
        None, description="Name of the hiring manager, if available"
    )

    model_config = ConfigDict(from_attributes=True, extra="allow")


# --- Base Schema ---
class JobBase(BaseModel):
    """Base schema for job data, reflecting the DB model.
    Defines the contract for representing a job in the system.
    Optimized for data structure and consistency.
    """

    source_data: Optional[Dict] = Field(
        None, description="Metadata from the processed source."
    )
    raw_text: Optional[str] = Field(
        None, description="The processed raw text from the job source."
    )
    extracted_data: Optional[JobExtractedData] = Field(
        None,
        description="All structured data extracted from the job source or provided manually.",
    )
    status: Optional[str] = Field(
        None,
        description="Processing status of the job (e.g., pending, processing, ready, error)",
        json_schema_extra={"examples": ["Ready"]},
    )

    model_config = ConfigDict(from_attributes=True)


# --- Create Schema ---
class JobCreate(BaseModel):
    """Schema for creating a new job from processed source data.

    This schema defines the data required to create a new job, which comes
    from the initial source processing. It intentionally excludes server-managed
    fields like 'status' or 'id' to prevent conflicts during object creation.
    """

    source_data: Optional[Dict] = Field(
        None, description="Metadata from the processed source."
    )
    raw_text: Optional[str] = Field(
        None, description="The processed raw text from the job source."
    )

    model_config = ConfigDict(from_attributes=True)


# --- Update Schema ---
class JobUpdate(BaseModel):
    """Schema for updating the extracted fields or status of an existing job."""

    extracted_data: Optional[JobExtractedData] = Field(
        None, description="Updated structured data for the job."
    )
    status: Optional[str] = Field(
        None, description="Updated job processing status (e.g., Ready, Error)"
    )

    model_config = ConfigDict(from_attributes=True)


# --- Response Schema ---
class JobResponse(JobBase):
    """Schema for job response, includes IDs and timestamps.
    Defines the contract for job data returned to the client.
    """

    id: int
    user_id: int
    company_id: Optional[int] = None  # From Job model

    time_created: datetime
    time_updated: datetime

    model_config = ConfigDict(from_attributes=True)
