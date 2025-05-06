""" Schemas for cover letter management."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime

class CoverLetterSections(BaseModel):
    """ Schema defining the standard sections of a cover letter"""
    title: Optional[str] = Field(None, description="A concise title for the cover letter (e.g., 'Application for Software Engineer at TechCorp')")
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

# Define Generation Options
class GenerationOptions(BaseModel):
    style: Optional[str] = Field("standard", description="Desired style (e.g., standard, creative, technical)")
    language: Optional[str] = Field("English", description="Desired language")
    tone: Optional[str] = Field("professional", description="Desired tone (e.g., professional, enthusiastic, concise)")
    # example_ids: Optional[List[int]] = Field(None, description="List of IDs for example cover letters to use as few-shot examples")
    # Add more options as needed

# Base schema defines common fields for cover letter
class CoverLetterBase(BaseModel):
    """ Base schema for cover letter data."""
    title: Optional[str] = Field(None, description="The title of the cover letter.")
    sections: Optional[CoverLetterSections] = Field(None, description="The structured sections of the cover letter.")
    cover_letter_text: Optional[str] = Field(None, description="The final assembled text of the cover letter.")

    class Config:
        from_attributes = True

class CoverLetterCreate(BaseModel): 
    """ Schema for initiating cover letter generation."""
    generation_options: Optional[GenerationOptions] = Field(None, description="Options for customizing the generation process")

class CoverLetterUpdate(BaseModel):
    """ Schema for updating an existing cover letter."""
    title: Optional[str] = Field(None, description="The updated title for the cover letter.")
    sections: Optional[CoverLetterSections] = Field(None, description="The updated structured sections for the cover letter.")
    cover_letter_text: Optional[str] = Field(None, description="The updated text for the cover letter.")

class CoverLetterResponse(BaseModel): 
    """ Schema for cover letter response, include IDs and creation time."""
    id: int
    user_id: int
    job_id: int
    title: Optional[str] = Field(None, description="The title of the cover letter.")
    generation_options: Optional[GenerationOptions] = Field(None, description="Options used during generation")
    sections: Optional[CoverLetterSections] = None
    cover_letter_text: Optional[str] = None 
    time_created: datetime

    class Config:
        """ Configure Pydantic to work with ORM."""
        from_attributes = True