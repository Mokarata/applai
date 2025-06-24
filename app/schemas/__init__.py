"""
Schemas for data validation and serialization
"""
from .user import UserBase, UserCreate, UserResponse, UserAddress
from .job import (
    JobBase,
    JobCreate,
    JobResponse,
    JobUpdate,
    JobSourceData,
    JobExtractedData
)
from .cover_letter import (
    CoverLetterBase,
    CoverLetterCreate,
    CoverLetterResponse, 
    CoverLetterStructure,
    GenerationOptions,
    CoverLetterUpdate
)
from .company import (
    CompanyAddress,
    ContactInfo,
    CompanyBase,
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyAnalytics,
    CompanyLLMResponse,
)

__all__ = [
    "UserBase",
    "UserCreate",
    "UserResponse",
    "UserAddress",
    "JobBase",
    "JobCreate",
    "JobResponse",
    "JobUpdate",
    "JobSourceData",
    "JobExtractedData",
    "CoverLetterBase",
    "CoverLetterCreate",
    "CoverLetterResponse", 
    "CoverLetterStructure",
    "GenerationOptions",
    "CoverLetterUpdate",
    "CompanyAddress",
    "ContactInfo",
    "CompanyBase",
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    "CompanyAnalytics",
    "CompanyLLMResponse",
]