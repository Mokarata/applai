"""
API endpoint for chat interactions.
"""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_chat_service
from app.schemas import ChatRequest, ChatResponse
from app.services import ChatService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def handle_chat_message(
    chat_request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """
    Handles a single chat message from the user and returns the bot's response.

    This endpoint uses a session_id to maintain conversation history.
    If a session_id is not provided in the request, a new one is created.
    """
    bot_response_text = await chat_service.get_chat_response(
        session_id=str(chat_request.session_id),
        user_message=chat_request.user_message,
        ai_message=chat_request.ai_message,  # Pass the new field to the service
    )

    return ChatResponse(
        bot_response=bot_response_text,
        session_id=chat_request.session_id,
    )
