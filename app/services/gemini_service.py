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

    def generate_cover_letter(self, job_data: str,
                             user_profile: str,
                             output_format: str) -> str:
        """
        Generate a cover letter based on the provided job data and user profile.
        Args:
            job_data (str): raw job data from job posting
            user_profile (str): CV data from user
            output_format (str): desired output format
        Returns:
            str: generated cover letter
        """
        logger.info("Generating cover letter")
        
        # Create structured prompt with system and user messages
        system_message_prompt = SystemMessagePromptTemplate.from_template(COVER_LETTER_SYSTEM)
        user_message_prompt = HumanMessagePromptTemplate.from_template(COVER_LETTER_USER)

        # Combine into a chat prompt template
        chat_prompt = ChatPromptTemplate.from_messages([
            system_message_prompt,
            user_message_prompt
        ])

        # Format the prompt with job and user data
        formatted_messages = chat_prompt.format_messages(
            job_details=job_data,
            user_profile=user_profile,
            output_format=output_format
        )
        logger.debug("Formatted cover letter prompt")

        try:
            # Get response from LLM
            logger.debug("Sending request to Gemini")
            response = self.llm.invoke(formatted_messages)

            # Extract text from response
            cover_letter_text = response.content
            logger.debug("Received response from Gemini")

            # Clean the response if needed
            if "```" in cover_letter_text:
                cover_letter_text = cover_letter_text.split("```")[1].strip()
                logger.debug("Cleaned code blocks from response")

            logger.info("Successfully generated cover letter")
            return cover_letter_text
        
        except Exception as e:
            # Handle errors gracefully
            logger.error(f"Error generating cover letter: {str(e)}", exc_info=True)
            return "An error occurred while generating the cover letter."