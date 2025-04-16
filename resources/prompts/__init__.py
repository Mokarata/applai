"""
Prompt module for AI operations.
"""

from .job_prompts import (
    JOB_EXTRACTION_SYSTEM,
    JOB_EXTRACTION_USER,
    JOB_EXTRACTION_EXAMPLE
)

from .cover_letter_prompts import (
    COVER_LETTER_SYSTEM,
    COVER_LETTER_USER
)

__all__ = [
    "JOB_EXTRACTION_SYSTEM",
    "JOB_EXTRACTION_USER",
    "JOB_EXTRACTION_EXAMPLE",
    "COVER_LETTER_SYSTEM",
    "COVER_LETTER_USER"
]