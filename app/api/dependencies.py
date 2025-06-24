""" Dependencies for API endpoints layer"""

# Python standard library - Core language functionality
from typing import Generator, Optional
import threading

# FastAPI - Dependency injection
from fastapi import Depends, HTTPException, status, BackgroundTasks

# SQLAlchemy - Database components
from sqlalchemy.orm import Session

# Application services - Business logic layer
from app.services import (
    UserService,
    JobService,
    CoverLetterService,
    CompanyService,
    GeminiService,
    OpenAIService,
    GroqService,
    LLMServiceProtocol, 
)

# Application configuration - Database connection
from app.db import get_db
from app.core import settings  

class LLMServiceProvider:
    """
    A thread-safe, lazy-loading provider for the LLM service.
    Acts as a singleton factory to ensure only one instance of the LLM service
    is created during the application's lifecycle.
    """
    _instance: Optional[LLMServiceProtocol] = None
    _lock = threading.Lock()

    def __call__(self) -> LLMServiceProtocol:
        # Use a lock to ensure thread-safe singleton creation
        with self._lock:
            if self._instance is None:
                llm_service_name = settings.ACTIVE_LLM_SERVICE
                api_key_is_present = False
                
                if llm_service_name == "GEMINI" and settings.GOOGLE_API_KEY:
                    self._instance = GeminiService()
                    api_key_is_present = True
                elif llm_service_name == "OPENAI" and settings.OPENAI_API_KEY:
                    self._instance = OpenAIService()
                    api_key_is_present = True
                elif llm_service_name == "GROQ" and settings.GROQ_API_KEY:
                    self._instance = GroqService()
                    api_key_is_present = True

                if not api_key_is_present:
                    # This will be raised only if no valid LLM service is configured
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail=f"LLM service '{llm_service_name}' is not configured with an API key."
                    )
        return self._instance

# Create a single instance of the provider that will be used for dependency injection
get_llm_service = LLMServiceProvider()

def get_company_service(
    db: Session = Depends(get_db),
    llm_service: LLMServiceProtocol = Depends(get_llm_service)
) -> CompanyService:
    """Provides an instance of the CompanyService with a database session and LLM service."""
    return CompanyService(db=db, llm_service=llm_service)

def get_job_service(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db), 
    llm_service: LLMServiceProtocol = Depends(get_llm_service),
    company_service: CompanyService = Depends(get_company_service),
) -> JobService:
    """Provides an instance of the JobService with a database session, LLM service, and background tasks."""
    return JobService(db=db, llm_service=llm_service, company_service=company_service, background_tasks=background_tasks)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Provides an instance of the UserService with a database session."""
    return UserService(db=db)

def get_cover_letter_service(
    db: Session = Depends(get_db),
    llm_service: LLMServiceProtocol = Depends(get_llm_service)
) -> CoverLetterService:
    """
    Provides an instance of the CoverLetterService with a database session
    and a LLMServiceProtocol instance.
    """
    return CoverLetterService(db=db, llm_service=llm_service)
