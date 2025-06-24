# Python standard library - Core language functionality
from typing import Optional, Dict, Any, Type

# Application dependencies
from app.core.config import settings
from app.core.logging import get_logger
from .llm_service_protocol import LLMServiceProtocol, T_BaseModel

# FastAPI components - Web framework utilities
from fastapi import HTTPException, status

# LangChain dependencies - AI model and prompt components
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import PydanticOutputParser

# Initialize logger
logger = get_logger(__name__)

class OpenAIService(LLMServiceProtocol):
    """ Service for interacting with OpenAI's LLM using langchain. """
    def __init__(self):
        try:
            # Initialize the LangChain Chat Model
            self.chat_model = ChatOpenAI(
                model= settings.OPENAI_MODEL or "gpt-3.5-turbo",
                api_key= settings.OPENAI_API_KEY,
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
            )
            logger.info(f"OpenAIService initialized successfully with model: {settings.OPENAI_MODEL}")
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
            system_message_prompt = SystemMessagePromptTemplate.from_template(system_prompt)
            human_message_prompt = HumanMessagePromptTemplate.from_template(user_prompt)
            chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

            # Create the chain: prompt -> model -> parser
            chain = chat_prompt | self.chat_model | StrOutputParser()

            logger.debug(f"Sending request to OpenAI with variables: {input_vars}")
            generated_text = await chain.ainvoke(input_vars)
            logger.debug(f"Received Text response from OpenAI: {generated_text[:200]}...")
            return generated_text
        except Exception as e:
            logger.error(f"Error during OpenAI text generation: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to generate text content via OpenAI: {e}"
            )

    async def generate_structured_output(
        self,
        output_schema: Type[T_BaseModel],
        system_prompt: str,
        user_prompt: str,
        input_vars: Optional[Dict[str, Any]] = None,
    ) -> T_BaseModel:
        """ Asynchronously generates structured output from the llm based on a Pydantic model."""

        try:
            output_parser = PydanticOutputParser(pydantic_object=output_schema)

            # Include format instructions in the system prompt or as a separat message
            format_instructions = output_parser.get_format_instructions()
            system_prompt = f"{system_prompt}\n\n{format_instructions}"

            # Create prompt templates
            system_message_prompt = SystemMessagePromptTemplate.from_template(system_prompt)
            human_message_prompt = HumanMessagePromptTemplate.from_template(user_prompt)
            chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

            # Create the chain: prompt -> model -> parser
            chain = chat_prompt | self.chat_model | output_parser
            
            # Invoke the chain
            logger.debug(f"Sending request to OpenAI with variables: {input_vars}")
            structured_response = await chain.ainvoke(input_vars)
            logger.debug(f"Received Structured response from OpenAI: {structured_response}")
            return structured_response
        except Exception as e:
            logger.error(f"Error during OpenAI async structured output generation: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to generate structured content via OpenAI: {e}"
            )