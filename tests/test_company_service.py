import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from sqlalchemy.orm import Session

from app.db.models import Company
from app.schemas.company import CompanyLLMResponse, ContactInfo, CompanyAnalytics
from app.services.company_service import CompanyService
from app.services.llm_service_protocol import LLMServiceProtocol
from tests.utils.company import create_random_company


@pytest.mark.asyncio
async def test_analyze_company_data(db: Session):
    # 1. Setup
    llm_service_mock = MagicMock(spec=LLMServiceProtocol)
    company_service = CompanyService(db=db, llm_service=llm_service_mock)

    # Mock the LLM service to return company analysis
    llm_response_data = CompanyLLMResponse(
        contact_info=ContactInfo(website_url="https://analyzed.com"),
        analytics=CompanyAnalytics(core_business="AI Solutions", vision="To dominate the world")
    )
    llm_service_mock.generate_structured_output = AsyncMock(return_value=llm_response_data)

    # Create a company to be analyzed
    company = Company(name="Test Company", status="pending")
    db.add(company)
    db.commit()
    db.refresh(company)

    assert company.status == "pending"

    # 2. Execute
    await company_service.analyze_company(company.id)

    # 3. Assert
    db.refresh(company)
    assert company.status == "completed"
    # Verify the JSON fields were updated correctly
    assert company.contact_info['website_url'] == 'https://analyzed.com/'
    assert company.analytics['core_business'] == 'AI Solutions'
    assert company.analytics['vision'] == 'To dominate the world'

    llm_service_mock.generate_structured_output.assert_called_once()
