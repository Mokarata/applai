from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from langchain.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.messages import AIMessage

from app.schemas.common import UserContact
from app.services.gemini_service import GeminiService


@pytest.mark.asyncio
async def test_generate_structured_output_raises_http_exception_on_parse_failure():
    """
    Tests that GeminiService raises an HTTPException when the PydanticOutputParser fails.
    """
    # 1. Arrange
    gemini_service = GeminiService()
    raw_output_from_llm = AIMessage(content="this is not valid json")

    # The parser instance needs to be an AsyncMock because the chain will `await .ainvoke()` on it
    mock_parser_instance = AsyncMock(spec=PydanticOutputParser)
    mock_parser_instance.ainvoke.side_effect = OutputParserException(
        "Simulated parsing error"
    )
    # get_format_instructions is called synchronously during setup
    mock_parser_instance.get_format_instructions.return_value = "some instructions"

    # This mock will represent the PydanticOutputParser class itself
    mock_parser_class = MagicMock(return_value=mock_parser_instance)

    # 2. Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        # Patch the PydanticOutputParser class in the service module.
        # When PydanticOutputParser(...) is called, it will return our configured mock_parser_instance.
        patch_target = "app.services.gemini_service.PydanticOutputParser"
        with patch(patch_target, new=mock_parser_class) as mocked_class:
            # Patch the model's ainvoke to avoid a real API call
            with patch(
                "langchain_google_genai.ChatGoogleGenerativeAI.ainvoke",
                new_callable=AsyncMock,
                return_value=raw_output_from_llm,
            ):
                await gemini_service.generate_structured_output(
                    output_schema=UserContact,
                    system_prompt="any prompt",
                    user_prompt="any user prompt",
                    input_vars={},
                )

    # 3. Verify
    assert exc_info.value.status_code == 500
    assert "Failed to parse LLM output" in exc_info.value.detail
    mocked_class.assert_called_once_with(pydantic_object=UserContact)
    # Check that ainvoke was awaited on the parser instance with the correct content
    mock_parser_instance.ainvoke.assert_awaited_once_with(raw_output_from_llm, ANY)
