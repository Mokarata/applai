# app/services/user_service.py
from typing import List, Optional

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.exc import SQLAlchemyError

from app.core.security import get_password_hash, verify_password
from app.db import User
from app.schemas.cv_extraction import CVData
from app.schemas.user import UserCreate, UserUpdate
from app.services.llm_service_protocol import LLMServiceProtocol
from app.utils.data_loader import process_source_to_markdown
from resources.prompts.cv_prompts import (CV_EXTRACTION_SYSTEM_PROMPT,
                                          CV_EXTRACTION_USER_PROMPT)

from app.core import get_logger

logger = get_logger(__name__)

class UserService:
    def __init__(self, db: Session, llm_service: LLMServiceProtocol):
        self.db = db
        self.llm_service = llm_service

    def get_user_by_id(self, user_id: int) -> User:
        """Retrieve a user by ID or raise 404."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user by their username."""
        return self.db.query(User).filter(User.user_name == username).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Retrieve a list of users."""
        return self.db.query(User).offset(skip).limit(limit).all()

    def create_user(self, user_in: UserCreate) -> User:
        """Create a new user."""
        if self.get_user_by_email(user_in.email):
            logger.warning(f"User creation failed: Email '{user_in.email}' already registered.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        if self.get_user_by_username(user_in.user_name):
            logger.warning(f"User creation failed: Username '{user_in.user_name}' already registered.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        try:
            hashed_password = get_password_hash(user_in.password)
            db_user = User(
                name=user_in.name,
                surname=user_in.surname,
                user_name=user_in.user_name,
                email=user_in.email,
                hashed_password=hashed_password,
                is_admin=user_in.is_admin,
            )

            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            logger.info(f"Successfully created user with ID: {db_user.id} and email: {db_user.email}")
            return db_user
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error while creating user '{user_in.user_name}': {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create user.",
            ) from e

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def update_user(
        self, user_id: int, user_in: UserUpdate, current_user: User
    ) -> User:
        """
        Update an existing user, with authorization checks.
        This method handles partial updates and filters out placeholder "string" values
        that may be sent from a UI like Swagger.
        """
        logger.info(f"User {current_user.id} attempting to update user {user_id}.")
        db_user = self.get_user_by_id(user_id)
        update_data = user_in.model_dump(exclude_unset=True)

        try:
            # --- Authorization ---
            if "is_admin" in update_data and not current_user.is_admin:
                logger.warning(
                    f"Forbidden: User {current_user.id} attempted to change admin status for user {user_id}."
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only administrators can change admin status.",
                )

            # --- Password Update ---
            if (
                "password" in update_data
                and update_data["password"]
                and update_data["password"] != "string"
            ):
                hashed_password = get_password_hash(update_data["password"])
                db_user.hashed_password = hashed_password
            update_data.pop("password", None)

            # --- Email Uniqueness Check ---
            if (
                "email" in update_data
                and update_data["email"] != db_user.email
                and update_data["email"] != "string"
            ):
                existing_user = self.get_user_by_email(update_data["email"])
                if existing_user and existing_user.id != user_id:
                    logger.warning(
                        f"User {current_user.id} failed to update email for user {user_id}: email '{update_data['email']}' already registered."
                    )
                    raise HTTPException(
                        status_code=400, detail="Email already registered by another user."
                    )

            # --- Nested JSON Field Updates ---
            if "contact_info" in update_data:
                self._update_contact_info(db_user, update_data.pop("contact_info"))

            if "cv_source_metadata" in update_data:
                self._update_cv_source_metadata(
                    db_user, update_data.pop("cv_source_metadata")
                )

            # --- Update other top-level fields ---
            for field, value in update_data.items():
                if value == "string":
                    continue
                if hasattr(db_user, field):
                    setattr(db_user, field, value)

            self.db.commit()
            self.db.refresh(db_user)
            logger.info(f"Successfully updated user {user_id}.")
            return db_user

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error while updating user {user_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not update user.",
            ) from e

    def delete_user(self, user_id: int) -> None:
        """Delete a user by ID."""
        db_user = self.get_user_by_id(user_id)
        # Add cascade delete check or related object handling if necessary
        # e.g., delete associated jobs/cover letters or handle FK constraints
        try:
            self.db.delete(db_user)
            self.db.commit()
            logger.info(f"Successfully deleted user {user_id}.")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error while deleting user {user_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not delete user.",
            ) from e

    def _update_contact_info(self, db_user: User, new_contact_data: dict):
        """Helper to perform a deep merge on the contact_info JSON field."""
        if not isinstance(new_contact_data, dict):
            return

        existing_contact_info = (
            db_user.contact_info if db_user.contact_info is not None else {}
        )

        # Deep merge for address
        if "address" in new_contact_data and isinstance(
            new_contact_data["address"], dict
        ):
            new_address_data = new_contact_data.pop("address")
            # Filter out placeholders from the incoming address data
            filtered_address = {k: v for k, v in new_address_data.items() if v != "string"}

            existing_address = existing_contact_info.get("address", {}) or {}
            existing_address.update(filtered_address)
            existing_contact_info["address"] = existing_address

        # Filter and update remaining contact_info fields
        filtered_contact_info = {
            k: v for k, v in new_contact_data.items() if v != "string"
        }
        existing_contact_info.update(filtered_contact_info)

        db_user.contact_info = existing_contact_info
        flag_modified(db_user, "contact_info")

    def _update_cv_source_metadata(self, db_user: User, new_metadata: dict):
        """Helper to update the cv_source_metadata JSON field."""
        if isinstance(new_metadata, dict):
            db_user.cv_source_metadata = new_metadata
            flag_modified(db_user, "cv_source_metadata")

    async def _extract_cv_data(self, cv_text: str) -> Optional[CVData]:
        """Uses the LLM service to extract structured data from CV text."""
        try:
            structured_data = await self.llm_service.generate_structured_output(
                output_schema=CVData,
                system_prompt=CV_EXTRACTION_SYSTEM_PROMPT,
                user_prompt=CV_EXTRACTION_USER_PROMPT,
                input_vars={"cv_text": cv_text},
            )
            return structured_data
        except Exception as e:
            # Log the exception but don't block the user update
            # In a real-world app, this might go to a monitoring service
            print(f"Error extracting CV data: {e}")
            return None

    async def process_user_cv(
        self, user_id: int, cv_file: UploadFile, current_user: User
    ) -> User:
        """Processes an uploaded CV, extracts data, and updates the user."""
        logger.info(f"Starting CV processing for user {user_id} from file: {cv_file.filename}")
        try:
            processed_source = await process_source_to_markdown(cv_file)

            if not processed_source or processed_source.metadata.get("error"):
                error_detail = processed_source.metadata.get(
                    "error", "Unknown processing error"
                )
                logger.warning(f"CV processing failed for user {user_id}: {error_detail}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Failed to process CV file: {error_detail}",
                )

            update_data = {
                "cv_text": processed_source.markdown_content,
                "cv_source_metadata": processed_source.metadata,
            }

            # Extract structured data using the LLM
            logger.info(f"Extracting structured data from CV for user {user_id}")
            structured_data = await self._extract_cv_data(processed_source.markdown_content)
            if structured_data:
                logger.info(f"Successfully extracted structured data for user {user_id}")
                update_data["structured_cv_data"] = structured_data
                if structured_data.contact_info:
                    update_data["contact_info"] = structured_data.contact_info
            else:
                logger.warning(f"LLM extraction returned no structured data for user {user_id}")

            user_update_in = UserUpdate(**update_data)
            return self.update_user(
                user_id=user_id, user_in=user_update_in, current_user=current_user
            )
        except Exception as e:
            logger.error(
                f"An unexpected error occurred during CV processing for user {user_id}: {e}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while processing the CV.",
            ) from e
