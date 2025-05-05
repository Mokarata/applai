""" Schemas for cover letter management."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

class CoverLetterSections(BaseModel):
    """ Schema defining the standard sections of a cover letter"""
    applicant_name: Optional[str] = Field(None, description="Applicant's full name.")
    applicant_contact: Optional[List[str]] = Field(None, description="Applicant contact details (e.g., phone, email, LinkedIn URL). List of strings.")
    date_generated: Optional[date] = Field(None, description="Date the cover letter was generated.")
    recipient_name: Optional[str] = Field(None, description="Recipient's name (e.g., 'Hiring Manager').")
    recipient_title: Optional[str] = Field(None, description="Recipient's title (e.g., 'Engineering Manager').")
    recipient_company: Optional[str] = Field(None, description="Company name.")
    recipient_address: Optional[str] = Field(None, description="Company address.")
    
    # Body Fields
    greeting: Optional[str] = Field(None, description="e.g., 'Dear Ms. Smith,' or 'Dear Hiring Team,'")
    introduction: Optional[str] = Field(None, description="Opening paragraph: hook, state purpose.")
    skills: Optional[str] = Field(None, description="Paragraph highlighting relevant skills/experience.")
    projects: Optional[str] = Field(None, description="Paragraph showcasing key projects/achievements.")
    company_fit: Optional[str] = Field(None, description="Paragraph explaining interest in the company.")
    conclusion: Optional[str] = Field(None, description="Closing paragraph: reiterate interest, call to action.")
    closing: Optional[str] = Field(None, description="e.g., 'Sincerely,'.")

# Base schema defines common fields for cover letter
class CoverLetterBase(BaseModel):
    """ Base schema for cover letter data."""
    template_name: Optional[str] = Field(None, description="Name of the template used, e.g., 'standard', 'creative'")
    sections: Optional[CoverLetterSections] = Field(None, description="The structured content of the cover letter")

    class Config:
        from_attributes = True

class CoverLetterCreate(CoverLetterBase):
    """ Schema for creating a new cover letter."""
    template_name: str
    sections: Optional[CoverLetterSections] = None

class CoverLetterUpdate(BaseModel):
    """ Schema for updating an existing cover letter."""
    template_name: Optional[str] = Field(None, description="Name of the template used, e.g., 'standard', 'creative'")
    sections: Optional[CoverLetterSections] = Field(None, description="The structured content of the cover letter")

class CoverLetterResponse(CoverLetterBase):
    """ Schema for cover letter response, include IDs and creation time."""
    id: int
    user_id: int
    job_id: int
    time_created: datetime

    class Config:
        """ Configure Pydantic to work with ORM."""
        from_attributes = True