# Python standard library - Core language functionality
from typing import List, Optional

# FastAPI and database components - Web and persistence layers
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, BackgroundTasks

# Application-specific imports - Models, schemas and services
from app.db import Company
from app.schemas import (
    CompanyCreate,
    CompanyUpdate,
    CompanyLLMResponse
)
from app.core import get_logger
from app.services import LLMServiceProtocol
from resources.prompts import COMPANY_ANALYSIS_SYSTEM, COMPANY_ANALYSIS_USER
from app.db import get_db

logger = get_logger(__name__)

class CompanyService:
    def __init__(self, db: Session, llm_service: LLMServiceProtocol):
        self.db = db
        self.llm_service = llm_service

    def get_company(
        self, 
        company_id: Optional[int] = None, 
        company_name: Optional[str] = None
    ) -> Optional[Company]:
        """Retrieves a company by its ID."""
        if company_id:
            return self.db.query(Company).filter(Company.id == company_id).first()
        elif company_name:
            return self.db.query(Company).filter(Company.name == company_name).first()
        return None

    def get_companies(self, skip: int = 0, limit: int = 100) -> List[Company]:
        """Retrieves all companies."""
        return self.db.query(Company).offset(skip).limit(limit).all()

    def create_company(
        self, 
        name: str,
        background_tasks: BackgroundTasks
    ) -> Company:
        """Creates a new company entry in the database and triggers background analysis."""
        # Check if company already exists
        company = self.get_company(company_name=name)
        if company:
            logger.info(f"Company '{name}' already exists with ID: {company.id}")
            return company
        
        # Create company with a pending status
        try:
            logger.info(f"Creating new company '{name}' with pending analysis status.")
            db_company = Company(
                name=name,
                status="pending_analysis" # Mark for background processing
            )
            self.db.add(db_company)
            self.db.commit()
            self.db.refresh(db_company)

            # Trigger background task to analyze the company
            background_tasks.add_task(self.analyze_company, company_id=db_company.id)
            logger.info(f"Enqueued analysis task for new company ID: {db_company.id}")

            return db_company
        except Exception as e:
            logger.error(f"Error creating company '{name}': {e}")
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create company in database."
            )

    async def analyze_company(self, company_id: int) -> Optional[CompanyLLMResponse]:
        """
        Analyzes a company by its ID using an LLM, and updates the database record.
        This method is designed to be run as a background task.
        """

        try:
            # Get company by ID
            company = self.db.query(Company).filter(Company.id == company_id).first()
            if not company:
                logger.error(f"[Analyze_Company] Company ID '{company_id}' not found.")
                return None
            
            logger.info(f"Starting LLM analysis for company: {company.name} (ID: {company_id})")
            try:
                analysis_result = await self.llm_service.generate_structured_output(
                    system_prompt=COMPANY_ANALYSIS_SYSTEM,
                    user_prompt=COMPANY_ANALYSIS_USER,
                    output_schema=CompanyLLMResponse,
                    input_vars={"company_name": company.name}
                )

                if not analysis_result:
                    logger.warning(f"LLM analysis for '{company.name}' returned no data. Setting status to 'failed_analysis'.")
                    company.status = "failed_analysis"
                else:
                    logger.info(f"Successfully received LLM analysis data for company: {company.name}")
                    company.contact_info = analysis_result.contact_info.model_dump(mode='json') if analysis_result.contact_info else None
                    company.analytics = analysis_result.analytics.model_dump(mode='json') if analysis_result.analytics else None
                    company.status = "completed"

                self.db.commit()
                logger.info(f"Successfully updated company: {company.name}")
                return company

            except Exception as e:
                logger.error(f"Error during LLM analysis for company name '{company.name}': {e}", exc_info=True)
                self.db.rollback()
                company = self.db.query(Company).filter(Company.id == company_id).first()
                if company:
                    company.status = "failed_analysis"
                    self.db.commit()

                return None
        except Exception as e:
            logger.error(f"Error analyzing company ID '{company_id}': {e}", exc_info=True)
            return None


    def update_company(
        self,
        company_id: int,
        company_in: CompanyUpdate
    ) -> Optional[Company]:
        """Updates a company's information in the database."""
        company = self.get_company(company_id=company_id)
        if not company:
            return None

        update_data = company_in.model_dump(exclude_unset=True)

        # Handle nested Pydantic models by converting them to dicts
        if "contact_info" in update_data and update_data["contact_info"]:
            update_data["contact_info"] = update_data["contact_info"]

        if "analytics" in update_data and update_data["analytics"]:
            update_data["analytics"] = update_data["analytics"]

        for key, value in update_data.items():
            setattr(company, key, value)

        try:
            self.db.add(company)
            self.db.commit()
            self.db.refresh(company)
            logger.info(f"Successfully updated company {company_id}")
            return company
        except Exception as e:
            self.db.rollback()
            logger.error(f"Database error updating company {company_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update company in database."
            )

    def delete_company(self, company_id: int) -> Optional[Company]:
        """Deletes a company from the database."""
        company = self.get_company(company_id=company_id)
        if not company:
            return None

        try:
            self.db.delete(company)
            self.db.commit()
            logger.info(f"Successfully deleted company {company_id}")
            return company
        except Exception as e:
            self.db.rollback()
            logger.error(f"Database error deleting company {company_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete company."
            )