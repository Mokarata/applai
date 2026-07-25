# Python standard library - Core language functionality
import logging
from typing import Any, Dict, Optional, Type

# FastAPI components - Web framework utilities
from fastapi import HTTPException, status
from langchain.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (ChatPromptTemplate,
                                    HumanMessagePromptTemplate,
                                    SystemMessagePromptTemplate)
# LangChain dependencies - AI model and prompt components
from langchain_google_genai import ChatGoogleGenerativeAI

# Application-specific imports - Configuration access
from app.core.config import settings  # Import your settings

from .llm_service_protocol import LLMServiceProtocol, T_BaseModel

# Initialize logger
logger = logging.getLogger(__name__)


class GeminiService(LLMServiceProtocol):
    """
    Service for interacting with the Google Gemini API via LangChain.
    Handles prompt formatting, API calls, and output parsing.
    """

    def __init__(self):
        try:
            # Initialize the Gemini chat model with configurations from settings
            self._model_name = settings.GEMINI_MODEL
            self.chat_model = ChatGoogleGenerativeAI(
                google_api_key=settings.GOOGLE_API_KEY,
                model=self._model_name,
                temperature=settings.GEMINI_TEMPERATURE,
                max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
            )
            self.text_parser = StrOutputParser()
            logger.info(
                "GeminiService initialized successfully with model: %s",
                self.chat_model.model,
            )
        except Exception as e:
            logger.error(
                "Failed to initialize ChatGoogleGenerativeAI: %s", e, exc_info=True
            )
            # Depending on desired behavior, re-raise or handle gracefully
            raise RuntimeError("Failed to initialize Gemini model: %s" % e) from e

    async def generate_text_from_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        input_vars: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generates plain text based on system and user prompts."""
        if input_vars is None:
            input_vars = {}

        logger.info(
            "Generating text output with input keys: %s", list(input_vars.keys())
        )
        try:
            # Create prompt templates
            system_message_prompt = SystemMessagePromptTemplate.from_template(
                system_prompt
            )
            human_message_prompt = HumanMessagePromptTemplate.from_template(user_prompt)
            chat_prompt = ChatPromptTemplate.from_messages(
                [system_message_prompt, human_message_prompt]
            )

            # Use String Output Parser for plain text
            chain = chat_prompt | self.chat_model | self.text_parser

            response = await chain.ainvoke(input_vars)
            logger.info("Successfully generated text output from Gemini.")
            return response
        except Exception as e:
            # Attempt a one-time fallback if model is not found/supported
            err_msg = str(e)
            if "NotFound" in err_msg or "not found for API version" in err_msg:
                fallback_models = [
                    "gemini-pro",
                    "gemini-1.0-pro",
                ]
                for fb in fallback_models:
                    if fb == self._model_name:
                        continue
                    try:
                        logger.warning(
                            "Gemini model '%s' failed, retrying with fallback model '%s'",
                            self._model_name,
                            fb,
                        )
                        self._model_name = fb
                        self.chat_model = ChatGoogleGenerativeAI(
                            google_api_key=settings.GOOGLE_API_KEY,
                            model=self._model_name,
                            temperature=settings.GEMINI_TEMPERATURE,
                            max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
                        )
                        # Rebuild chain with new model
                        system_message_prompt = (
                            SystemMessagePromptTemplate.from_template(system_prompt)
                        )
                        human_message_prompt = HumanMessagePromptTemplate.from_template(
                            user_prompt
                        )
                        chat_prompt = ChatPromptTemplate.from_messages(
                            [system_message_prompt, human_message_prompt]
                        )
                        chain = chat_prompt | self.chat_model | self.text_parser
                        response = await chain.ainvoke(input_vars)
                        logger.info(
                            "Successfully generated text output from Gemini using fallback '%s'.",
                            self._model_name,
                        )
                        return response
                    except Exception:  # try next fallback
                        continue
            logger.error("Error during Gemini text generation: %s", e, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to generate text content via LLM: {e}",
            ) from e

    async def generate_structured_output(
        self,
        system_prompt: str,
        user_prompt: str,
        output_schema: Type[T_BaseModel],
        input_vars: Optional[Dict[str, Any]] = None,
    ) -> T_BaseModel:
        """Generates structured output (JSON) based on prompts and a Pydantic schema."""

        logger.info(
            "Generating Structured Output for schema: %s", output_schema.__name__
        )
        parser = PydanticOutputParser(pydantic_object=output_schema)

        try:
            format_instructions = parser.get_format_instructions()

            # The format instructions from PydanticOutputParser contain curly braces
            # that are misinterpreted as template variables. We must escape them by doubling them.
            escaped_format_instructions = format_instructions.replace(
                "{", "{{"
            ).replace("}", "}}")

            # We combine the system prompt and the escaped format instructions into a single prompt.
            # This is necessary because the Gemini API expects only one system message at the beginning.
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

            # Use Pydantic Output Parser for structured data
            chain = chat_prompt | self.chat_model | parser

            # Invoke the chain with input variables
            response = await chain.ainvoke(input_vars)
            logger.info(
                "Successfully generated and parsed structured output for schema: %s",
                output_schema.__name__,
            )
            return response
        except OutputParserException as e:
            logger.error(
                "Output parsing error in Gemini structured output: %s", e, exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to parse LLM output: {e}",
            ) from e
        except Exception as e:
            # Attempt a one-time fallback if model is not found/supported
            err_msg = str(e)
            if "NotFound" in err_msg or "not found for API version" in err_msg:
                fallback_models = [
                    "gemini-pro",
                    "gemini-1.0-pro",
                ]
                for fb in fallback_models:
                    if fb == getattr(self, "_model_name", settings.GEMINI_MODEL):
                        continue
                    try:
                        logger.warning(
                            "Gemini model '%s' failed, retrying structured generation with fallback '%s'",
                            getattr(self, "_model_name", settings.GEMINI_MODEL),
                            fb,
                        )
                        self._model_name = fb
                        self.chat_model = ChatGoogleGenerativeAI(
                            google_api_key=settings.GOOGLE_API_KEY,
                            model=self._model_name,
                            temperature=settings.GEMINI_TEMPERATURE,
                            max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
                        )
                        # Rebuild parser and prompt chain
                        parser = PydanticOutputParser(pydantic_object=output_schema)
                        format_instructions = parser.get_format_instructions()
                        escaped_format_instructions = format_instructions.replace(
                            "{", "{{"
                        ).replace("}", "}}")
                        final_system_prompt = (
                            f"{system_prompt}\n\n{escaped_format_instructions}"
                        )
                        system_message_prompt = (
                            SystemMessagePromptTemplate.from_template(
                                final_system_prompt
                            )
                        )
                        human_message_prompt = HumanMessagePromptTemplate.from_template(
                            user_prompt
                        )
                        chat_prompt = ChatPromptTemplate.from_messages(
                            [system_message_prompt, human_message_prompt]
                        )
                        chain = chat_prompt | self.chat_model | parser
                        response = await chain.ainvoke(input_vars)
                        logger.info(
                            "Successfully generated structured output using fallback '%s'",
                            self._model_name,
                        )
                        return response
                    except Exception:  # try next fallback
                        continue
            logger.error(
                "Error during Gemini structured output generation: %s", e, exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to generate structured content via LLM: {e}",
            ) from e
