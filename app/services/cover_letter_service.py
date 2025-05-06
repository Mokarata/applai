# Python standard library - Core language functionality
import json
import logging
from datetime import date
from typing import List, Optional, Dict, Any

# FastAPI and database components - Web and persistence layers
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

# Application-specific imports - Models, schemas and services
from app.db import models
from app.schemas import cover_letter as cover_letter_schema, CoverLetterSections
from app.services.gemini_service import GeminiService, CoverLetterJson
from resources.prompts import cover_letter_prompts


# Setup logger for this service
logger = logging.getLogger(__name__)


class CoverLetterService:
    """
    Service layer for handling cover letter generation, retrieval, and management,
    using LangChain via GeminiService and structured prompts.
    """
    def __init__(self, db: Session, gemini_service: GeminiService):
        self.db = db
        self.gemini_service = gemini_service

    def _get_user_or_404(self, user_id: int) -> models.User | None:
        """Helper to fetch user by ID or raise 404."""
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            logger.warning(f"User not found with id: {user_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def _get_job_or_404(self, job_id: int) -> models.Job | None:
        """Helper to fetch job by ID or raise 404."""
        job = self.db.query(models.Job).filter(models.Job.id == job_id).first()
        if not job:
            logger.warning(f"Job not found with id: {job_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        return job

    def _get_cover_letter_or_404(self, cover_letter_id: int, user_id: Optional[int] = None) -> models.CoverLetter:
        """Helper to fetch cover letter by ID, optionally checking user ownership."""
        query = self.db.query(models.CoverLetter).filter(models.CoverLetter.id == cover_letter_id)
        if user_id is not None:
            query = query.filter(models.CoverLetter.user_id == user_id)

        cover_letter = query.first()
        if not cover_letter:
            log_msg = f"Cover letter not found with id: {cover_letter_id}"
            if user_id:
                 log_msg += f" for user_id: {user_id}"
            logger.warning(log_msg)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cover letter not found")
        return cover_letter

    def _assemble_cover_letter_text(self, sections: CoverLetterSections) -> str:
        # Simple assembly logic, improve as needed
        # This assumes your CoverLetterSections model has these fields.
        # Adjust based on your actual CoverLetterSections fields.
        parts = [
            # sections.title, # Title usually isn't part of the letter body itself
            f"Applicant: {sections.applicant_name}" if sections.applicant_name else None,
            f"Contact: {', '.join(sections.applicant_contact)}" if sections.applicant_contact else None,
            f"Date: {sections.date_generated}" if sections.date_generated else None,
            f"\nTo: {sections.recipient_name}" if sections.recipient_name else None,
            sections.recipient_title,
            sections.recipient_company,
            sections.recipient_address,
            f"\n{sections.greeting}\n" if sections.greeting else None,
            sections.introduction,
            sections.skills,
            sections.projects,
            sections.company_fit,
            sections.conclusion,
            f"\n{sections.closing}" if sections.closing else None,
            sections.applicant_name # Signature
        ]
        return "\n".join(filter(None, parts))

    def generate_and_save_cover_letter(
        self,
        cover_letter_data: cover_letter_schema.CoverLetterCreate,
        user_id: int,
        job_id: int
    ) -> models.CoverLetter:
        """
        Generates a cover letter using GeminiService (LangChain) based on user and job data,
        then saves it to the database. Uses structured JSON prompts.
        """
        logger.info(f"Generating cover letter for user_id: {user_id}, job_id: {job_id}")

        # 1. Fetch required data
        user = self._get_user_or_404(user_id)
        job = self._get_job_or_404(job_id)

        # Extract generation options with defaults
        options = cover_letter_data.generation_options
        style = options.style if options and options.style else "standard"
        language = options.language if options and options.language else "German"
        tone = options.tone if options and options.tone else "professional"
        # example_ids = options.example_ids if options and options.example_ids else [] # For future few-shot

        logger.info(f"Generation options: style='{style}', language='{language}', tone='{tone}'")

        # 2. Prepare input variables for the prompt templates
        # Convert models to simple dictionaries first
        user_profile_dict = {
            "full_name": f"{user.name} {user.surname}",
            "email": user.email,
            "phone": getattr(user, 'phone', None),
            "linkedin_url": getattr(user, 'linkedin_url', None),
            "portfolio_url": getattr(user, 'portfolio_url', None),
            "resume_text": user.cv_text,
            # Add other fields present in your User model AND used in the prompt
        }
        job_details_dict = {
            "job_title": job.title,
            "company_name": job.company,
            "job_description": job.full_description,
            "location": getattr(job, 'location', None),
            # Add other fields present in your Job model AND used in the prompt
        }

        # Use json.dumps for complex objects within the prompt if needed,
        # otherwise pass directly if the prompt template handles simple fields.
        input_vars = {
            "job_details": json.dumps(job_details_dict, indent=2), # Pass as JSON string
            "user_profile": json.dumps(user_profile_dict, indent=2), # Pass as JSON string
            "style": style, # Add new style option
            "language": language, # Add new language option
            "tone": tone, # Add new tone option
            "current_date": date.today().isoformat()
            # Add placeholder for few-shot examples if implementing
            # "few_shot_examples": formatted_examples_string
        }
        logger.debug(f"Input variables prepared for GeminiService: {list(input_vars.keys())}")

        # 3. Call Gemini service to get structured output
        try:
            # Use the structured output method and the Pydantic schema defined in GeminiService
            generated_data = self.gemini_service.generate_structured_output(
                system_prompt_template=cover_letter_prompts.COVER_LETTER_SYSTEM,
                user_prompt_template=cover_letter_prompts.COVER_LETTER_USER,
                input_variables=input_vars,
                output_schema=CoverLetterJson # Specify the expected structure
            )
            logger.info(f"Successfully generated structured data from Gemini.")

        except HTTPException as http_exc:
             # Re-raise HTTP exceptions from GeminiService
             raise http_exc
        except Exception as e:
            logger.error(f"Unexpected error calling Gemini service: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An internal error occurred during cover letter generation."
            )

        # 4. Extract title from the generated data
        letter_title = generated_data.get("title", "Untitled Cover Letter")

        # 5. Map available fields from structured_output (which is a CoverLetterJson dict) to CoverLetterSections
        sections_data_dict = {}
        for field_name in CoverLetterSections.model_fields.keys():
            if field_name in generated_data:
                sections_data_dict[field_name] = generated_data[field_name]
            elif field_name == 'title': # Ensure title is set from letter_title if not directly in output with that key for sections
                sections_data_dict[field_name] = letter_title
            # else: field will be default or None as per CoverLetterSections definition

        sections_model = CoverLetterSections(**sections_data_dict)
        logger.debug(f"CoverLetterSections model populated: {sections_model.model_dump_json(indent=2)}")

        # 6. Assemble the structured parts into final text
        final_cover_letter_text = self._assemble_cover_letter_text(sections_model)
        logger.debug("Assembled structured data into final cover letter text.")

        # 7. Create and save the cover letter database record with BOTH fields
        db_cover_letter = models.CoverLetter(
            user_id=user_id,
            job_id=job_id,
            title=letter_title, # Save the extracted title
            generation_options=options.model_dump(mode='json') if options else None,
            sections=sections_model.model_dump(mode='json'), # Save the CoverLetterSections model
            cover_letter_text=final_cover_letter_text,
        )
        self.db.add(db_cover_letter)
        try:
            self.db.commit()
            self.db.refresh(db_cover_letter)
            logger.info(f"Saved new cover letter with id: {db_cover_letter.id}")
            return db_cover_letter
        except Exception as e:
            self.db.rollback()
            logger.error(f"Database error saving cover letter for user_id {user_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save cover letter to database."
            )

    # --- Standard CRUD methods (adapt as needed) ---

    def get_cover_letter(self, cover_letter_id: int, user_id: int) -> models.CoverLetter:
        """Retrieves a specific cover letter for a user."""
        logger.info(f"Fetching cover letter id: {cover_letter_id} for user_id: {user_id}")
        return self._get_cover_letter_or_404(cover_letter_id, user_id=user_id)

    def get_cover_letters_by_user(self, user_id: int) -> List[models.CoverLetter]:
        """Retrieves all cover letters for a specific user."""
        logger.info(f"Fetching all cover letters for user_id: {user_id}")
        self._get_user_or_404(user_id) # Ensure user exists
        return self.db.query(models.CoverLetter).filter(models.CoverLetter.user_id == user_id).order_by(models.CoverLetter.created_at.desc()).all()

    def update_cover_letter(
        self,
        cover_letter_id: int,
        user_id: int,
        update_data: cover_letter_schema.CoverLetterUpdate
    ) -> models.CoverLetter:
        """
        Updates an existing cover letter.
        NOTE: This currently updates the assembled text. If you need to edit
        structured parts and regenerate, the logic would be more complex.
        """
        logger.info(f"Updating cover letter id: {cover_letter_id} for user_id: {user_id}")
        db_cover_letter = self._get_cover_letter_or_404(cover_letter_id, user_id=user_id)

        update_data_dict = update_data.model_dump(exclude_unset=True)

        for key, value in update_data_dict.items():
            # Only update fields present in the model (primarily cover_letter_text)
            if hasattr(db_cover_letter, key):
                 setattr(db_cover_letter, key, value)

        try:
            self.db.commit()
            self.db.refresh(db_cover_letter)
            logger.info(f"Successfully updated cover letter id: {cover_letter_id}")
            return db_cover_letter
        except Exception as e:
            self.db.rollback()
            logger.error(f"Database error updating cover letter id {cover_letter_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update cover letter in database."
            )


    def delete_cover_letter(self, cover_letter_id: int, user_id: int) -> Dict[str, Any]:
        """Deletes a specific cover letter for a user."""
        logger.info(f"Attempting to delete cover letter id: {cover_letter_id} for user_id: {user_id}")
        db_cover_letter = self._get_cover_letter_or_404(cover_letter_id, user_id=user_id)

        self.db.delete(db_cover_letter)
        try:
            self.db.commit()
            logger.info(f"Successfully deleted cover letter id: {cover_letter_id}")
            return {"detail": f"Cover letter {cover_letter_id} deleted successfully."}
        except Exception as e:
            self.db.rollback()
            logger.error(f"Database error deleting cover letter id {cover_letter_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete cover letter from database."
            )

    def get_cover_letter_by_id(self, cover_letter_id: int) -> Optional[models.CoverLetter]:
        logger.info(f"Fetching cover letter id: {cover_letter_id}")
        return self.db.query(models.CoverLetter).filter(models.CoverLetter.id == cover_letter_id).first()
