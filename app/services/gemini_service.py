"""
Service for AI operations using Google's Gemini.
"""
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import json
from resources.prompts import (
    JOB_EXTRACTION_SYSTEM,
    JOB_EXTRACTION_USER,
    COVER_LETTER_SYSTEM,
    COVER_LETTER_USER
)
from app.core.logging import get_logger
from app.schemas.cover_letter import CoverLetterSections
from datetime import date

# Get a logger for this module
logger = get_logger(__name__)

load_dotenv()

class GeminiService:
    """Service for AI operations using Google's Gemini."""
    
    def __init__(self):
        """ initialize Gemini service with API key from environment variables"""
        logger.info("Initializing GeminiService")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.1,
            max_output_tokens=1024,
            convert_system_message_to_human=True
        )

    def extract_job_data(self, job_data: str) -> Dict[str, Any]:
        """ 
            Extract job data from raw job data using Gemini.
            Args: job_data (str): Raw job data text.
            Returns: Dict[str, Any]: Extracted job data.
        """
        logger.info("Extracting job data")
        
        # Create structured prompt with system and user messages
        system_message_prompt = SystemMessagePromptTemplate.from_template(JOB_EXTRACTION_SYSTEM)
        user_message_prompt = HumanMessagePromptTemplate.from_template(JOB_EXTRACTION_USER)
        
        # Combine into a chat prompt template
        chat_prompt = ChatPromptTemplate.from_messages([
            system_message_prompt,
            user_message_prompt
        ])
        
        # Format the prompt with job data
        formatted_messages = chat_prompt.format_messages(job_data=job_data)
        logger.debug(f"Formatted messages for job extraction")
        
        try:
            # Get response from LLM
            response = self.llm.invoke(formatted_messages)
            logger.debug("Received response from Gemini")
            
            # Extract and parse JSON from response
            response_text = response.content
            logger.debug("Processing response text")
            
            # Clean the response text if needed
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
                logger.debug("Cleaned JSON code block from response")
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                logger.debug("Cleaned code block from response")

            # Parse JSON
            extracted_data = json.loads(response_text)
            logger.debug("Successfully parsed job data JSON")
            
            # Add validation with fallbacks
            if not extracted_data.get("title"):
                extracted_data["title"] = "Software Engineer"
                logger.warning("Missing job title, using default: 'Software Engineer'")
            if not extracted_data.get("company"):
                extracted_data["company"] = "Tech Company"
                logger.warning("Missing company name, using default: 'Tech Company'")
            if not extracted_data.get("location"):
                extracted_data["location"] = "Remote"
                logger.warning("Missing location, using default: 'Remote'")
            
            logger.info(f"Successfully extracted job data for {extracted_data.get('title')} at {extracted_data.get('company')}")
            return extracted_data
            
        except json.JSONDecodeError as e:
            # Handle JSON parsing errors
            logger.error(f"JSON decode error: {str(e)}")
            logger.error("Failed to parse response text")
            return {
                "title": "Software Engineer",
                "company": "Tech Company",
                "location": "Remote"
            }
        except Exception as e:
            # Handle errors gracefully
            logger.error(f"Error extracting job data: {str(e)}", exc_info=True)
            return {
                "title": "Software Engineer",
                "company": "Tech Company",
                "location": "Remote"
            }

    async def generate_cover_letter(self, job_details: dict, user_profile: dict, template_name: str = "standard") -> CoverLetterSections:
        """
        Generates a cover letter using the Gemini API based on job details and user profile.
        Uses system/user prompts and returns a structured CoverLetterSections object.
        """
        logger.info(f"Generating cover letter for job: {job_details.get('title', 'N/A')} at {job_details.get('company', 'N/A')}, template: {template_name}")
        logger.debug(f"User profile keys: {list(user_profile.keys())}")

        # Ensure prompts are loaded correctly
        if not COVER_LETTER_SYSTEM or not COVER_LETTER_USER:
            logger.error("System or User prompt constants not loaded!")
            raise ValueError("Cover letter prompts are not configured.")
            
        # Create prompt templates from constants
        system_message_prompt = SystemMessagePromptTemplate.from_template(COVER_LETTER_SYSTEM)
        user_message_prompt = HumanMessagePromptTemplate.from_template(COVER_LETTER_USER)

        # Combine into a chat prompt template
        chat_prompt = ChatPromptTemplate.from_messages([
            system_message_prompt,
            user_message_prompt
        ])

        current_date_str = date.today().isoformat()

        # Format the prompt with necessary data
        # Using json.dumps ensures dicts are passed as readable strings in the prompt
        try:
            formatted_messages = chat_prompt.format_messages(
                job_details=json.dumps(job_details, indent=2),
                user_profile=json.dumps(user_profile, indent=2),
                template_name=template_name,
                current_date=current_date_str
            )
            logger.debug("Formatted cover letter prompt using system/user templates.")
        except Exception as format_err:
            logger.error(f"Error formatting prompt messages: {format_err}", exc_info=True)
            raise Exception("Internal error formatting generation request.")

        # Invoke the LLM
        try:
            logger.debug("Sending request to Gemini via LangChain invoke.")
            response = self.llm.invoke(formatted_messages)
            raw_text = response.content.strip() # Get raw text output
            logger.debug(f"Received raw response from Gemini (first 200 chars): {raw_text[:200]}...")

            # Attempt to parse the raw text as JSON
            try:
                # Handle potential markdown code blocks
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                
                # Trim potential leading/trailing whitespace again after stripping code fences
                raw_text = raw_text.strip()
                
                parsed_json = json.loads(raw_text)
                logger.debug("Successfully parsed JSON from response.")

            except json.JSONDecodeError as json_err:
                logger.error(f"Failed to decode JSON response: {json_err}", exc_info=True)
                logger.error(f"Raw response content that failed parsing was: {raw_text}")
                raise Exception("AI response was not valid JSON.")

            # Validate the parsed JSON against the Pydantic schema
            try:
                cover_letter_sections = CoverLetterSections(**parsed_json)
                logger.info("Successfully validated JSON against CoverLetterSections schema.")
                return cover_letter_sections # Return the validated Pydantic object
            
            except Exception as validation_err: # Catch Pydantic validation errors more broadly
                logger.error(f"Failed to validate parsed JSON against schema: {validation_err}", exc_info=True)
                logger.error(f"Parsed JSON data that failed validation was: {parsed_json}")
                raise Exception("AI response structure did not match expected format.")

        except Exception as e:
            # Catch errors during LLM invocation or other unexpected issues
            logger.error(f"Error during cover letter generation or processing: {str(e)}", exc_info=True)
            raise Exception(f"An unexpected error occurred during cover letter generation: {str(e)}")