"""
Pydantic models for chat functionality.
"""

from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for a chat message."""

    session_id: UUID = Field(
        default_factory=uuid4,
        description="The unique identifier for the conversation session.",
    )
    user_message: Optional[str] = Field(None, description="The message from the user.")
    ai_message: Optional[str] = Field(
        None, description="An initial AI message to seed the chat history."
    )


class ChatResponse(BaseModel):
    """Response model for a chat message."""

    bot_response: str = Field(..., description="The response from the chatbot.")
    session_id: UUID = Field(
        ..., description="The unique identifier for the conversation session."
    )
