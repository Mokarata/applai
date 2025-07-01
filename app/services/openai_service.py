# Python standard library - Core language functionality
from typing import Any, Dict, Optional, Type

# FastAPI components - Web framework utilities
from fastapi import HTTPException, status

from langchain.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
# LangChain dependencies - AI model and prompt components
from langchain_openai import ChatOpenAI

# Application dependencies
from app.core.config import settings
from app.core.logging import get_logger

from .llm_service_protocol import LLMServiceProtocol, T_BaseModel

# Initialize logger
logger = get_logger(__name__)


class OpenAIService(LLMServiceProtocol):
    """Service for interacting with OpenAI's LLM using langchain."""

    def __init__(self):
        try:
            # Initialize the LangChain Chat Model
            self.chat_model = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
            )
            logger.info(
                f"OpenAIService initialized successfully with model: {settings.OPENAI_MODEL}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize OpenAIService: {e}")
            raise

    async def generate_text_from_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        input_vars: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generates plain text output from OpenAI."""
        try:
            # Create prompt templates
            system_message_prompt = SystemMessagePromptTemplate.from_template(
                system_prompt
            )
            human_message_prompt = HumanMessagePromptTemplate.from_template(user_prompt)
            chat_prompt = ChatPromptTemplate.from_messages(
                [system_message_prompt, human_message_prompt]
            )

            # Create the chain: prompt -> model -> parser
            chain = chat_prompt | self.chat_model | StrOutputParser()

            logger.debug(f"Sending request to OpenAI with variables: {input_vars}")
            generated_text = await chain.ainvoke(input_vars)
            logger.debug(
                f"Received Text response from OpenAI: {generated_text[:200]}..."
            )
            return generated_text
        except Exception as e:
            logger.error(f"Error during OpenAI text generation: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to generate text content via OpenAI: {e}",
            )

    async def generate_structured_output(
        self,
        output_schema: Type[T_BaseModel],
        system_prompt: str,
        user_prompt: str,
        input_vars: Optional[Dict[str, Any]] = None,
    ) -> T_BaseModel:
        """Asynchronously generates structured output from the llm based on a Pydantic model."""
        logger.info(
            "Generating Structured Output for schema: %s", output_schema.__name__
        )
        parser = PydanticOutputParser(pydantic_object=output_schema)

        try:
            format_instructions = parser.get_format_instructions()
            escaped_format_instructions = format_instructions.replace("{", "{{").replace("}", "}}")
            final_system_prompt = f"{system_prompt}\n\n{escaped_format_instructions}"

            system_message_prompt = SystemMessagePromptTemplate.from_template(
                final_system_prompt
            )
            human_message_prompt = HumanMessagePromptTemplate.from_template(user_prompt)

            chat_prompt = ChatPromptTemplate.from_messages(
                [
                    system_message_prompt,
                    human_message_prompt,
                ]
            )

            chain = chat_prompt | self.chat_model | parser

            response = await chain.ainvoke(input_vars)
            logger.info(
                "Successfully generated and parsed structured output for schema: %s",
                output_schema.__name__,
            )
            return response
        except OutputParserException as e:
            logger.error(
                "Output parsing error in OpenAI structured output: %s", e, exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to parse LLM output: {e}",
            ) from e
        except Exception as e:
            logger.error(
                "Error during OpenAI structured output generation: %s", e, exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to generate structured content via LLM: {e}",
            ) from e
