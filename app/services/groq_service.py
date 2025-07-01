# Python standard library - Core language functionality
import logging
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
from langchain_groq import ChatGroq  # Groq specific chat model

# Application-specific imports - Configuration access
from app.core.config import settings

from .llm_service_protocol import LLMServiceProtocol, T_BaseModel

# Initialize logger
logger = logging.getLogger(__name__)


class GroqService(LLMServiceProtocol):
    """
    Service for interacting with the Groq API via LangChain.
    Handles prompt formatting, API calls, and output parsing.
    """

    def __init__(self):
        if not settings.GROQ_API_KEY:
            logger.error("GROQ_API_KEY not found in settings.")
            raise ValueError("Groq API Key is required but not configured.")

        try:
            # Initialize the LangChain Chat Model for Groq
            self.chat_model = ChatGroq(
                api_key=settings.GROQ_API_KEY,
                model=settings.GROQ_MODEL_NAME,
                temperature=settings.GROQ_TEMPERATURE,
                max_tokens=settings.GROQ_MAX_TOKENS,
            )
            self.text_parser = StrOutputParser()
            logger.info(
                f"GroqService initialized successfully with model: {settings.GROQ_MODEL_NAME}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChatGroq: {e}", exc_info=True)
            raise RuntimeError(f"Failed to initialize Groq model: {e}")

    async def generate_text_from_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        input_vars: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generates plain text based on system and user prompts using Groq."""
        if input_vars is None:
            input_vars = {}
        logger.info(
            f"Groq - Generating text output with input keys: {list(input_vars.keys())}"
        )
        try:
            system_message_prompt = SystemMessagePromptTemplate.from_template(
                system_prompt
            )
            human_message_prompt = HumanMessagePromptTemplate.from_template(user_prompt)
            chat_prompt = ChatPromptTemplate.from_messages(
                [system_message_prompt, human_message_prompt]
            )

            chain = chat_prompt | self.chat_model | self.text_parser

            response = await chain.ainvoke(input_vars)
            logger.info("Groq - Successfully generated text output.")
            logger.debug(f"Groq - Text response: {response[:200]}...")
            return response
        except Exception as e:
            logger.error(f"Groq - Error generating text output: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating text from Groq: {e}",
            )

    async def generate_structured_output(
        self,
        output_schema: Type[T_BaseModel],
        system_prompt: str,
        user_prompt: str,
        input_vars: Optional[Dict[str, Any]] = None,
    ) -> T_BaseModel:
        """Generates structured output (JSON) based on prompts and a Pydantic schema using Groq."""
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
                "Output parsing error in Groq structured output: %s", e, exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to parse LLM output: {e}",
            ) from e
        except Exception as e:
            logger.error(
                "Error during Groq structured output generation: %s", e, exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to generate structured content via LLM: {e}",
            ) from e
