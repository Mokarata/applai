""" Schemas for job extraction."""
from pydantic import BaseModel
from typing import Optional

class JobExtractionRequest(BaseModel):
    """ Schema for job extraction request."""
    job_data: str
    user_id: int


class JobExtractionResponse(BaseModel):
    """ Schema for job extraction response."""
    title: str
    company: str
    location: str
    job_data: str
    user_id: int
