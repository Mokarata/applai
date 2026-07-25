"""Schemas for data validation and serialization."""

from .chat import ChatRequest, ChatResponse
from .common import UserAddress, UserContact
from .company import (CompanyAddress, CompanyAnalytics, CompanyBase,
                      CompanyCreate, CompanyLLMResponse, CompanyResponse,
                      CompanyUpdate, ContactInfo)
from .cover_letter import (CoverLetterBase, CoverLetterCreate,
                           CoverLetterResponse, CoverLetterStructure,
                           CoverLetterUpdate, GenerationOptions)
from .job import JobBase, JobCreate, JobExtractedData, JobResponse, JobUpdate
from .token import Token, TokenData
from .user import UserBase, UserCreate, UserResponse

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserResponse",
    "UserAddress",
    "UserContact",
    # Token
    "Token",
    "TokenData",
    # Job
    "JobBase",
    "JobCreate",
    "JobResponse",
    "JobUpdate",
    "JobExtractedData",
    # Cover Letter
    "CoverLetterBase",
    "CoverLetterCreate",
    "CoverLetterResponse",
    "CoverLetterStructure",
    "GenerationOptions",
    "CoverLetterUpdate",
    # Company
    "CompanyAddress",
    "ContactInfo",
    "CompanyBase",
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    "CompanyAnalytics",
    "CompanyLLMResponse",
    # Chat
    "ChatRequest",
    "ChatResponse",
]
