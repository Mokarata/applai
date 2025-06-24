# Python standard library - Core language functionality
import json
import logging
import traceback
from datetime import date, datetime
from typing import List, Optional, Dict, Any

# FastAPI and database components - Web and persistence layers
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

# Application-specific imports - Models, schemas and services
from app.db import User, Job, CoverLetter
from app.schemas import (
    CoverLetterStructure, 
    CoverLetterCreate, 
    CoverLetterUpdate, 
    UserResponse, 
    JobResponse,
    GenerationOptions
)
from .llm_service_protocol import LLMServiceProtocol
from resources.prompts import cover_letter_prompts
from app.core.config import settings

# Setup logger for this service
logger = logging.getLogger(__name__)

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


class CoverLetterService:
    """
    Service layer for handling cover letter generation, retrieval, and management,
    using LangChain via LLMService.
    """
    def __init__(self, db: Session, llm_service: LLMServiceProtocol):
        self.db = db
        self.llm_service = llm_service

    def _authorize_cover_letter_access(self, cover_letter: CoverLetter, current_user: User):
        """Helper to authorize if a user can access a cover letter."""
        if cover_letter.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this cover letter."
            )

    def _get_user(self, user_id: int) -> User:
        """Helper to fetch user by ID or raise 404."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User not found with id: {user_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def _get_job(self, job_id: int) -> Job:
        """Helper to fetch job by ID or raise 404."""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.warning(f"Job not found with id: {job_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        return job

    def _get_cover_letter(self, cover_letter_id: int, user_id: Optional[int] = None) -> CoverLetter:
        """Helper to fetch cover letter by ID, optionally checking user ownership."""
        query = self.db.query(CoverLetter).filter(CoverLetter.id == cover_letter_id)
        if user_id is not None:
            query = query.filter(CoverLetter.user_id == user_id)

        cover_letter = query.first()
        if not cover_letter:
            log_msg = f"Cover letter not found with id: {cover_letter_id}"
            if user_id:
                 log_msg += f" for user_id: {user_id}"
            logger.warning(log_msg)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cover letter not found")
        return cover_letter

    def get_cover_letter(self, cover_letter_id: int, current_user: User) -> CoverLetter:
        """Fetches a cover letter by ID with authorization checks."""
        cover_letter = self.db.query(CoverLetter).filter(CoverLetter.id == cover_letter_id).first()
        if not cover_letter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cover letter not found")
        
        self._authorize_cover_letter_access(cover_letter, current_user)
        return cover_letter

    def get_cover_letters_by_user(self, user_id: Optional[int]) -> List[CoverLetter]:
        """
        Get all cover letters. If user_id is provided, filter by it.
        Otherwise, returns all cover letters (intended for admin use).
        """
        query = self.db.query(CoverLetter)
        if user_id is not None:
            # Also validate user exists
            self._get_user(user_id)
            query = query.filter(CoverLetter.user_id == user_id)
        
        return query.order_by(CoverLetter.time_created.desc()).all()

    def _assemble_cover_letter_text(self, sections: CoverLetterStructure) -> str:
        """Assembles the cover letter from structured sections into a single string."""
        # Using a list and join is more efficient than repeated string concatenation
        parts = [
            f"To: {sections.recipient_name}" if sections.recipient_name else "To Whom It May Concern,",
            sections.recipient_title,
            sections.recipient_company,
            sections.recipient_address,
            f"\n{sections.greeting}\n" if sections.greeting else "\nDear Hiring Team,\n",
            sections.introduction,
            sections.skills,
            sections.projects,
            sections.company_fit,
            sections.conclusion,
            f"\n{sections.closing}" if sections.closing else "\nSincerely,",
            sections.applicant_name
        ]
        return "\n".join(filter(None, parts))

    async def generate_cover_letter(
        self,
        cover_letter_data: CoverLetterCreate,
        user_id: int,
        job_id: int,
        current_user: User
    ) -> CoverLetter:
        """
        Generates a cover letter using an LLM service based on user and job data,
        then saves it to the database. Uses structured JSON prompts.
        """
        logger.info(f"Generating cover letter for user_id: {user_id}, job_id: {job_id}")
        try:
            # 1. Fetch required data
            user = self._get_user(user_id)
            job = self._get_job(job_id)
            logger.debug(f"DEBUG TRACE: Fetched user: {user.id if user else 'None'}, job: {job.id if job else 'None'}")

            # Extract generation options with defaults
            options = cover_letter_data.generation_options if cover_letter_data.generation_options is not None else GenerationOptions()
            style = options.style
            language = options.language
            tone = options.tone
            length = options.length
            logger.debug(f"DEBUG TRACE: GenerationOptions: style={style}, language={language}, tone={tone}, length={length}")

            # 2. Prepare input variables for the prompt templates
            # Use Pydantic response models for consistent and maintainable data serialization
            user_details_dict = UserResponse.model_validate(user).model_dump(exclude_unset=True, exclude_none=True)
            job_details_dict = JobResponse.model_validate(job).model_dump(exclude_unset=True, exclude_none=True)

            # Prepare final input variables, serializing complex objects to JSON strings
            input_vars = {
                "job_details": json.dumps(job_details_dict, indent=2, default=json_serial),
                "user_details": json.dumps(user_details_dict, indent=2, default=json_serial),
                "style": style,
                "language": language,
                "tone": tone,
                "length": length,
                "current_date": date.today().isoformat()
            }
            logger.debug(f"Input variables prepared for LLM service: {list(input_vars.keys())}")

            # 3. Generate structured data from LLM
            active_llm_service = self.llm_service
            logger.info(f"Using LLM service: {type(active_llm_service).__name__}")

            generated_data: CoverLetterStructure = await active_llm_service.generate_structured_output(
                system_prompt=cover_letter_prompts.COVER_LETTER_SYSTEM,
                user_prompt=cover_letter_prompts.COVER_LETTER_USER,
                input_vars=input_vars,
                output_schema=CoverLetterStructure
            )
            logger.info("Successfully generated structured data from LLM.")
            logger.debug(f"LLM output (CoverLetterStructure): {generated_data.model_dump_json(indent=2)}")

            # 4. Assemble and save the cover letter
            job_title = job.extracted_data.get('title', 'Untitled Job') if job.extracted_data else 'Untitled Job'
            letter_title = generated_data.title if hasattr(generated_data, 'title') and generated_data.title else f"Cover Letter for {job_title}"
            
            final_cover_letter_text = self._assemble_cover_letter_text(generated_data)
            logger.debug("Assembled structured data into final cover letter text.")

            # Create CoverLetter DB instance
            db_cover_letter = CoverLetter(
                user_id=user_id,
                job_id=job_id,
                title=letter_title,
                generation_options=options.model_dump() if options else None,
                sections=generated_data.model_dump(),
                text=final_cover_letter_text,
                llm_service_used=settings.ACTIVE_LLM_SERVICE,
            )
            
            self.db.add(db_cover_letter)
            self.db.commit()
            self.db.refresh(db_cover_letter)
            logger.info(f"Cover letter {db_cover_letter.id} saved successfully for user {user_id}, job {job_id}.")
            return db_cover_letter

        except HTTPException as http_exc:
            # Re-raise HTTP exceptions to be handled by FastAPI
            raise http_exc
        except Exception as e:
            # Log the full traceback for any other exceptions
            logger.error(f"An unexpected error occurred in generate_cover_letter: {e}", exc_info=True)
            # Also log the state of relevant variables
            logger.error(f"Traceback: {traceback.format_exc()}")
            logger.error(f"User ID: {user_id}, Job ID: {job_id}")
            if 'options' in locals():
                 logger.error(f"Generation Options: {options.model_dump_json() if options else 'None'}")
            if 'generated_data' in locals():
                logger.error(f"Generated Data from LLM: {generated_data.model_dump_json() if generated_data else 'None'}")
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An internal error occurred during cover letter generation."
            )

    async def update_cover_letter(
        self,
        cover_letter_id: int,
        update_data: CoverLetterUpdate,
        current_user: User
    ) -> CoverLetter:
        """Updates a cover letter after authorization."""
        cover_letter = self.get_cover_letter(cover_letter_id, current_user)
        update_dict = update_data.model_dump(exclude_unset=True)

        if 'title' in update_dict:
            cover_letter.title = update_dict['title']

        # Check if sections (structure) are being updated
        if 'sections' in update_dict and update_data.sections is not None:
            # Merge existing sections with new data
            existing_sections_data = cover_letter.sections or {}
            
            new_section_data = update_dict['sections']
            # Ensure new_section_data is a dict, whether it comes from a Pydantic model or raw dict
            if isinstance(new_section_data, CoverLetterStructure):
                new_section_data = new_section_data.model_dump(exclude_unset=True)
            
            updated_sections_data = {**existing_sections_data, **new_section_data}
            
            new_sections_model = CoverLetterStructure(**updated_sections_data)
            
            cover_letter.sections = new_sections_model.model_dump()
            # Regenerate text from the updated sections
            cover_letter.text = self._assemble_cover_letter_text(new_sections_model)
        
        # Else, if only text is updated (and sections were not part of the update_dict)
        elif 'text' in update_dict:
            cover_letter.text = update_dict['text']
            # Clear sections as they are now out of sync with the manually edited text
            cover_letter.sections = {}

        self.db.commit()
        self.db.refresh(cover_letter)
        return cover_letter

    def delete_cover_letter(self, cover_letter_id: int, current_user: User):
        """Deletes a cover letter after authorization."""
        cover_letter = self.get_cover_letter(cover_letter_id, current_user)
        self.db.delete(cover_letter)
        self.db.commit()

    def get_cover_letter_by_id(self, cover_letter_id: int) -> Optional[CoverLetter]:
        logger.info(f"Fetching cover letter id: {cover_letter_id}")
        return self.db.query(CoverLetter).filter(CoverLetter.id == cover_letter_id).first()
