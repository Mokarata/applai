""" Schemas for job extraction."""
from pydantic import BaseModel
from typing import Optional

class JobExtractionRequest(BaseModel):
    """ Schema for job extraction request."""
    description: str
    user_id: int


class JobExtractionResponse(BaseModel):
    """ Schema for job extraction response."""
    title: str
    company: str
    location: str
    description: str
    user_id: int
