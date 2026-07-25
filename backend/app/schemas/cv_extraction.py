"""Pydantic schemas for structured data extraction from CVs."""

from typing import List, Optional

from pydantic import BaseModel, Field

from .common import UserContact


class CVEducation(BaseModel):
    """Schema for an educational entry from a CV."""

    institution: Optional[str] = Field(
        None, description="The name of the educational institution."
    )
    degree: Optional[str] = Field(
        None, description="The degree or qualification obtained."
    )
    start_date: Optional[str] = Field(
        None, description="The start date of the education."
    )
    end_date: Optional[str] = Field(None, description="The end date of the education.")
    description: Optional[str] = Field(
        None, description="A brief description of the studies or achievements."
    )


class CVWorkExperience(BaseModel):
    """Schema for a work experience entry from a CV."""

    company: Optional[str] = Field(None, description="The name of the company.")
    job_title: Optional[str] = Field(None, description="The job title.")
    start_date: Optional[str] = Field(
        None, description="The start date of the employment."
    )
    end_date: Optional[str] = Field(None, description="The end date of the employment.")
    description: Optional[str] = Field(
        None, description="A description of the responsibilities and achievements."
    )


class CVSkills(BaseModel):
    """Schema for skills extracted from a CV."""

    technical: Optional[List[str]] = Field(
        None, description="A list of technical skills."
    )
    soft: Optional[List[str]] = Field(None, description="A list of soft skills.")


class CVData(BaseModel):
    """Main schema for all data extracted from a CV."""

    contact_info: Optional[UserContact] = Field(
        None, description="The contact information from the CV."
    )
    summary: Optional[str] = Field(
        None, description="The professional summary or objective from the CV."
    )
    work_experience: Optional[List[CVWorkExperience]] = Field(
        None, description="A list of work experiences."
    )
    education: Optional[List[CVEducation]] = Field(
        None, description="A list of educational qualifications."
    )
    skills: Optional[CVSkills] = Field(
        None, description="The skills section from the CV."
    )
