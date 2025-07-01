"""Schemas for data sources.

This module defines the standardized data structures for handling processed
data sources.
"""

from typing import Any, Dict

from pydantic import BaseModel, Field


class ProcessedSource(BaseModel):
    """A standardized schema for processed source data.

    This schema holds the clean, extracted markdown content and any relevant
    metadata produced by the data loaders.
    """

    markdown_content: str = Field(
        description="The extracted and cleaned content in Markdown format."
    )
    metadata: Dict[str, Any] = Field(
        description="A dictionary of metadata extracted from the source."
    )
