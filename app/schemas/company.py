""" Schemas for company data management."""
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from typing import Optional
from datetime import datetime

# --- Address Schema (can be shared or specific to Company) ---
class CompanyAddress(BaseModel):
    """ Schema for company address details."""
    street: Optional[str] = Field(None, description="Street address", json_schema_extra={"example": "123 Main St"})
    city: Optional[str] = Field(None, description="City", json_schema_extra={"example": "San Francisco"})
    state: Optional[str] = Field(None, description="State or Province", json_schema_extra={"example": "CA"})
    zip_code: Optional[str] = Field(None, description="Zip or Postal Code", json_schema_extra={"example": "94107"})
    country: Optional[str] = Field(None, description="Country", json_schema_extra={"example": "USA"})

    model_config = ConfigDict(from_attributes=True)

class ContactInfo(BaseModel):
    """ Schema for company contact details."""
    address: Optional[CompanyAddress] = None
    email: Optional[str] = Field(None, description="Company email address")
    phone: Optional[str] = Field(None, description="Company phone number")
    website_url: Optional[HttpUrl] = Field(None, description="Company website URL")

    model_config = ConfigDict(from_attributes=True)

class CompanyAnalytics(BaseModel):
    """ Schema for company enrichment data intended to be used for better LLM responses."""
    core_business: Optional[str] = Field(
        None, 
        description="""Business/Industry: 
            What the company does and the sector they operate in.
            Why: Helps the LLM use industry-specific terminology, understand the problems they solve, and tailor the applicant's impact to that domain.
        """,
        examples=[
            "Leading SaaS provider for project management",
            "Pioneer in renewable energy solutions",
            "Global automotive technology supplier",
            "E-commerce platform for sustainable products"
        ]
    )
    vision: Optional[str] = Field(
        None,
        description="""Mission Statement & Vision: 
            The company's overarching purpose, long-term goals, and what they aim to achieve.
            Why: This is crucial for aligning with "morale and core values." The LLM can draw themes from here to express shared purpose, passion, and future contribution.
        """,
        examples=[
            "To make transportation safer and more accessible for everyone",
            "Empowering businesses through intelligent data insights",
            "Creating a sustainable future through innovative engineering"
        ]
    )
    core_values: Optional[str] = Field(
        None,
        description=""" Core Business / Industry (2-5 keywords/phrases): 
            The principles that guide their culture, decisions, and how employees are expected to work.
            Why: Direct input for cultural alignment. The LLM can integrate these keywords or their concepts into the letter to show the applicant embodies these values.
        """,
        examples=[
            "Innovation, Collaboration, Integrity",
            "Customer-centric, Agile, Sustainable",
            "Excellence, Responsibility, Pioneering"
        ]
    )
    key_products: Optional[str] = Field(
        None,
        description="""Product/Services/Projects (1-2 relevant to the role): 
            What the company is known for, especially if the role contributes to it, or recent significant achievements.
            Why: Allows the LLM to show the applicant has done their homework and is excited about specific work. 
                It enables phrases like "I'm particularly impressed by your recent launch of [Product X] 
                and believe my skills in [Skill Y] would directly contribute to its continued success."
        """,
        examples=[
            "Their flagship product, 'DataFlow Pro'," 
            "Their recent work on AI-powered predictive maintenance," 
            "The development of their new mobile banking app."
        ]
    )
    culture: Optional[str] = Field(
        None,
        description=""" Company Culture Keywords (if publicly stated)
            How they describe their work environment.
            Why: Helps adjust the tone of the letter. If they emphasize "collaboration," the letter can stress teamwork. If "fast-paced innovation," it can convey dynamism.
        """,
        examples=[
            "Highly collaborative environment",
            "Fast-paced and innovative culture",
            "Strong focus on work-life balance and employee well-being"
        ]
    )

    model_config = ConfigDict(from_attributes=True)

class CompanyLLMResponse(BaseModel):
    """ Schema for company LLM response."""
    contact_info: Optional[ContactInfo] = Field(None, description="Company contact details")
    analytics: Optional[CompanyAnalytics] = Field(None, description="Company analytics enrichment data")
    
    model_config = ConfigDict(from_attributes=True)
    
# --- Base Company Schema ---
class CompanyBase(BaseModel):
    """ Base schema for company data."""
    name: str = Field(..., description="Company name", json_schema_extra={"example": "Innovatech Solutions Inc."})
    contact_info: Optional[ContactInfo] = Field(None, description="Company contact details")
    analytics: Optional[CompanyAnalytics] = Field(None, description="Company analytics enrichment data")
    
    model_config = ConfigDict(from_attributes=True)

# --- Schema for Creating a Company ---
class CompanyCreate(CompanyBase):
    """ Schema used when creating a new company."""
    name: str = Field(..., description="Company name", json_schema_extra={"example": "Innovatech Solutions Inc."})

# --- Schema for Updating a Company ---
class CompanyUpdate(BaseModel):
    """ Schema for updating an existing company. All fields are optional."""
    name: Optional[str] = Field(None, description="Company name")
    contact_info: Optional[ContactInfo] = Field(None, description="Company contact details")
    analytics: Optional[CompanyAnalytics] = Field(None, description="Company analytics enrichment data")

    model_config = ConfigDict(from_attributes=True)

# --- Schema for Company Response (includes DB-generated fields) ---
class CompanyResponse(CompanyBase):
    """ Schema for representing a company in API responses."""
    id: int
    time_created: datetime
    time_updated: datetime

    model_config = ConfigDict(from_attributes=True)
