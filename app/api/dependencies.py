# Python standard library - Core language functionality
from typing import Generator

# FastAPI - Dependency injection
from fastapi import Depends, HTTPException, status

# SQLAlchemy - Database components
from sqlalchemy.orm import Session

# Application services - Business logic layer
from app.services.user_service import UserService
from app.services.job_service import JobService  
from app.services.cover_letter_service import CoverLetterService
from app.services.gemini_service import GeminiService

# Application configuration - Database connection
from app.db.database import get_db
from app.core.config import get_settings # Assuming settings hold API key

def get_gemini_service() -> GeminiService:
    """Provides an instance of the GeminiService."""
    settings = get_settings()
    # Ensure the API key is configured (add error handling if needed)
    # Use the exact field name defined in the Settings model (uppercase)
    if not settings.GOOGLE_API_KEY: 
         # Use HTTPException for consistency in API layer dependencies
         raise HTTPException(
             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
             detail="GOOGLE_API_KEY must be configured in settings."
         )
    # Use the exact field name defined in the Settings model (uppercase)
    return GeminiService(api_key=settings.GOOGLE_API_KEY)

def get_job_service(db: Session = Depends(get_db)) -> JobService:
    """Provides an instance of the JobService with a database session."""
    # JobService currently gets GeminiService internally if needed,
    # but we could inject it here too for consistency if preferred.
    # Assuming GeminiService is initialized within JobService when required.
    return JobService(db=db)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Provides an instance of the UserService with a database session."""
    return UserService(db=db)

def get_cover_letter_service(
    db: Session = Depends(get_db),
    gemini_service: GeminiService = Depends(get_gemini_service)
) -> CoverLetterService:
    """
    Provides an instance of the CoverLetterService with a database session
    and a GeminiService instance.
    """
    return CoverLetterService(db=db, gemini_service=gemini_service)
