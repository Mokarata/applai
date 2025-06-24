# Python standard library - Core language functionality
import logging
from typing import Dict, Any, Type, Optional

# LangChain dependencies - AI model and prompt components
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import PydanticOutputParser

# FastAPI components - Web framework utilities
from fastapi import HTTPException, status

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
            self.chat_model = ChatGoogleGenerativeAI(
                google_api_key=settings.GOOGLE_API_KEY,
                model=settings.GEMINI_MODEL,
                temperature=settings.GEMINI_TEMPERATURE,
                max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
                convert_system_message_to_human=True,
            )
            self.text_parser = StrOutputParser()
            logger.info(f"GeminiService initialized successfully with model: {self.chat_model.model}")
        except Exception as e:
            logger.error(f"Failed to initialize ChatGoogleGenerativeAI: {e}", exc_info=True)
            # Depending on desired behavior, re-raise or handle gracefully
            raise RuntimeError(f"Failed to initialize Gemini model: {e}")

    async def generate_text_from_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        input_vars: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generates plain text based on system and user prompts."""
        logger.info(f"Generating text output with input keys: {list(input_vars.keys())}")
        try:
            # Create prompt templates
            system_message_prompt = SystemMessagePromptTemplate.from_template(system_prompt)
            human_message_prompt = HumanMessagePromptTemplate.from_template(user_prompt)
            chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

            # Use String Output Parser for plain text
            chain = chat_prompt | self.chat_model | self.text_parser
            
            response = await chain.ainvoke(input_vars)
            logger.info("Successfully generated text output from Gemini.")
            return response
        except Exception as e:
            logger.error(f"Error during Gemini text generation: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to generate text content via LLM: {e}"
            )

    async def generate_structured_output(
        self,
        output_schema: Type[T_BaseModel],
        system_prompt: str,
        user_prompt: str,
        input_vars: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> T_BaseModel:
        """Generates structured output (JSON) based on prompts and a Pydantic schema."""
        logger.info(f"Generating Structured Output for schema: {output_schema.__name__}"
                    f"with temp={temperature}, max_tokens={max_tokens}")
        try:
            # Initialize the PydanticOutputParser with the provided schema
            parser = PydanticOutputParser(pydantic_object=output_schema)
            format_instructions = parser.get_format_instructions()

            # Define a system prompt that includes a placeholder for the format instructions.
            # This prevents LangChain from parsing the JSON schema for variables.
            system_prompt_with_format = f"{system_prompt}\n\n{{format_instructions}}"

            chat_prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt_with_format),
                ("human", user_prompt)
            ])

            # Use .partial to inject the format instructions as a pre-filled variable.
            final_prompt = chat_prompt.partial(format_instructions=format_instructions)

            chain = final_prompt | self.chat_model | parser
            
            response = await chain.ainvoke(input_vars)
            logger.info(f"Successfully generated structured output for {output_schema.__name__}.")
            return response
        except Exception as e:
            logger.error(f"Error generating structured output from Gemini: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error processing request with Gemini: {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing request with Gemini: {str(e)}"
            )