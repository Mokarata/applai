# app/services/gemini_service.py
import logging
from typing import Dict, Any, Type, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field # Use langchain's Pydantic for parser definition
from fastapi import HTTPException, status

from app.core.config import settings # Import your settings

# Setup logger for this service
logger = logging.getLogger(__name__)
# Configure logging basics if not done elsewhere
# logging.basicConfig(level=logging.INFO)

# Define a Pydantic model mirroring the JSON structure requested in the system prompt
# This helps LangChain's JsonOutputParser validate the LLM's response.
class CoverLetterJson(BaseModel):
    applicant_name: str = Field(description="Applicant's full name.")
    applicant_contact: list[str] = Field(description="Applicant's contact details.")
    date_generated: str = Field(description="The date provided in YYYY-MM-DD format.")
    recipient_name: str = Field(description="Recipient's name.")
    recipient_title: Optional[str] = Field(description="Recipient's job title.", default=None)
    recipient_company: str = Field(description="Company name.")
    recipient_address: Optional[str] = Field(description="Company address.", default=None)
    greeting: str = Field(description="Formal greeting.")
    introduction: str = Field(description="Opening paragraph.")
    skills: str = Field(description="Paragraph highlighting relevant skills.")
    projects: str = Field(description="Paragraph showcasing key projects.")
    company_fit: str = Field(description="Paragraph explaining interest in the company.")
    conclusion: str = Field(description="Closing paragraph.")
    closing: str = Field(description="Formal closing.")
    # Add other fields if your system prompt defines them

class GeminiService:
    """
    Service for interacting with the Google Gemini API via LangChain.
    Handles prompt formatting, API calls, and output parsing.
    """
    def __init__(self, api_key: Optional[str] = settings.GOOGLE_API_KEY):
        if not api_key:
            logger.error("GOOGLE_API_KEY not found in settings.")
            raise ValueError("Gemini API Key is required but not configured.")

        try:
            # Initialize the LangChain Chat Model
            # Adjust model_name if needed (e.g., "gemini-1.5-flash", "gemini-1.0-pro")
            self.model = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash", # Or your preferred Gemini model
                google_api_key=api_key,
                temperature=0.7, # Adjust creativity/determinism
                convert_system_message_to_human=True,
                # convert_system_message_to_human=True # May be needed depending on model/LangChain version
            )
            logger.info("GeminiService initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize ChatGoogleGenerativeAI: {e}", exc_info=True)
            # Depending on desired behavior, re-raise or handle gracefully
            raise RuntimeError(f"Failed to initialize Gemini model: {e}")

    def generate_structured_output(
        self,
        system_prompt_template: str,
        user_prompt_template: str,
        input_variables: Dict[str, Any],
        output_schema: Type[BaseModel] = CoverLetterJson # Use the defined Pydantic model
    ) -> Dict[str, Any]:
        """
        Generates structured output (JSON/Pydantic object) from Gemini using LangChain.

        Args:
            system_prompt_template: The template string for the system message.
            user_prompt_template: The template string for the user/human message.
            input_variables: A dictionary of values to fill the prompt templates.
            output_schema: The Pydantic model defining the expected JSON structure.

        Returns:
            A dictionary representing the parsed JSON output from the LLM.

        Raises:
            HTTPException: If the generation or parsing fails.
        """
        logger.info(f"Generating structured output with input keys: {list(input_variables.keys())}")

        try:
            # Create prompt templates
            system_message_prompt = SystemMessagePromptTemplate.from_template(system_prompt_template)
            human_message_prompt = HumanMessagePromptTemplate.from_template(user_prompt_template)
            chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

            # Create the output parser based on the Pydantic schema
            parser = JsonOutputParser(pydantic_object=output_schema)

            # Create the LangChain Expression Language (LCEL) chain
            chain = chat_prompt | self.model | parser

            # Invoke the chain
            response = chain.invoke(input_variables)
            logger.info("Successfully generated and parsed structured output from Gemini.")
            # The parser returns a dictionary here
            return response

        except Exception as e:
            logger.error(f"Error during Gemini generation or parsing: {e}", exc_info=True)
            # Consider more specific error handling based on LangChain exceptions if needed
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to generate content via LLM: {e}"
            )

    def generate_text_output(
            self,
            system_prompt_template: str,
            user_prompt_template: str,
            input_variables: Dict[str, Any]
    ) -> str:
        """Generates plain text output from Gemini."""
        logger.info(f"Generating text output with input keys: {list(input_variables.keys())}")
        try:
             # Create prompt templates
            system_message_prompt = SystemMessagePromptTemplate.from_template(system_prompt_template)
            human_message_prompt = HumanMessagePromptTemplate.from_template(user_prompt_template)
            chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

            # Use String Output Parser for plain text
            parser = StrOutputParser()

            # Create the LangChain Expression Language (LCEL) chain
            chain = chat_prompt | self.model | parser

            # Invoke the chain
            response = chain.invoke(input_variables)
            logger.info("Successfully generated text output from Gemini.")
            return response
        except Exception as e:
            logger.error(f"Error during Gemini text generation: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to generate text content via LLM: {e}"
            )