import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_company_service
from app.core.dependencies import get_current_user
from app.db.models import User
from app.schemas.company import CompanyResponse, CompanyUpdate
from app.services.company_service import CompanyService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[CompanyResponse])
def list_companies(
    skip: int = 0,
    limit: int = 100,
    company_service: CompanyService = Depends(get_company_service),
    current_user: User = Depends(get_current_user),
) -> List[CompanyResponse]:
    """Retrieve all companies with pagination."""
    logger.info(f"User {current_user.id} fetching all companies.")
    companies = company_service.get_companies(skip=skip, limit=limit)
    return companies


@router.get("/{company_id}", response_model=CompanyResponse)
def read_company(
    company_id: int,
    company_service: CompanyService = Depends(get_company_service),
    current_user: User = Depends(get_current_user),
) -> CompanyResponse:
    """Retrieve a single company by its ID."""
    logger.info(f"User {current_user.id} fetching company {company_id}.")
    company = company_service.get_company(company_id=company_id)
    if not company:
        logger.warning(f"Company {company_id} not found for user {current_user.id}.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    company_in: CompanyUpdate,
    company_service: CompanyService = Depends(get_company_service),
    current_user: User = Depends(get_current_user),
) -> CompanyResponse:
    """Update a company's information."""
    logger.info(f"User {current_user.id} updating company {company_id}.")
    company = company_service.update_company(
        company_id=company_id, company_in=company_in
    )
    if not company:
        logger.warning(
            f"Company {company_id} not found for update by user {current_user.id}."
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: int,
    company_service: CompanyService = Depends(get_company_service),
    current_user: User = Depends(get_current_user),
):
    """Delete a company."""
    logger.info(f"User {current_user.id} deleting company {company_id}.")
    company = company_service.delete_company(company_id=company_id)
    if not company:
        logger.warning(
            f"Company {company_id} not found for deletion by user {current_user.id}."
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )
    return
