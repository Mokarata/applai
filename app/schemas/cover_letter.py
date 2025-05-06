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
    template_name: Optional[str] = Field(None, description="Name of the template used")
    sections: Optional[CoverLetterSections] = Field(None, description="The structured sections of the cover letter.")
    cover_letter_text: Optional[str] = Field(None, description="The final assembled text of the cover letter.")

    class Config:
        from_attributes = True

class CoverLetterCreate(BaseModel): 
    """ Schema for initiating cover letter generation."""
    template_name: str = Field(..., description="Name of the template to use for generation.")

class CoverLetterUpdate(BaseModel):
    """ Schema for updating an existing cover letter."""
    sections: Optional[CoverLetterSections] = Field(None, description="The updated structured sections for the cover letter.")
    cover_letter_text: Optional[str] = Field(None, description="The updated text for the cover letter.")
    template_name: Optional[str] = Field(None, description="Optionally update the template name associated.")

class CoverLetterResponse(BaseModel): 
    """ Schema for cover letter response, include IDs and creation time."""
    id: int
    user_id: int
    job_id: int
    template_name: Optional[str] = None 
    sections: Optional[CoverLetterSections] = None
    cover_letter_text: Optional[str] = None 
    time_created: datetime

    class Config:
        """ Configure Pydantic to work with ORM."""
        from_attributes = True