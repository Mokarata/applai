"""
Prompt module for AI operations.
"""

from .company_prompts import COMPANY_ANALYSIS_SYSTEM, COMPANY_ANALYSIS_USER
from .cover_letter_prompts import COVER_LETTER_SYSTEM, COVER_LETTER_USER
from .job_prompts import JOB_EXTRACTION_SYSTEM, JOB_EXTRACTION_USER

__all__ = [
    "JOB_EXTRACTION_SYSTEM",
    "JOB_EXTRACTION_USER",
    "COVER_LETTER_SYSTEM",
    "COVER_LETTER_USER",
    "COMPANY_ANALYSIS_SYSTEM",
    "COMPANY_ANALYSIS_USER",
]
