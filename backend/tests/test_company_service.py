from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.db.models import Company
from app.schemas.company import (CompanyAnalytics, CompanyLLMResponse,
                                 ContactInfo)
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
        analytics=CompanyAnalytics(
            core_business="AI Solutions", vision="To dominate the world"
        ),
    )
    llm_service_mock.generate_structured_output = AsyncMock(
        return_value=llm_response_data
    )

    # Create a company to be analyzed
    company = Company(name="Test Company", status="pending")
    db.add(company)
    db.commit()
    db.expire(company)
    db.refresh(company)

    assert company.status == "pending"

    # 2. Execute
    # Patch get_db to ensure the background task uses the same DB session.
    patch_target = "app.services.company_service.get_db"
    with patch(patch_target) as mock_get_db:
        # We need to mock the full sequence: get_db() -> generator -> next() -> context_manager
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = (
            db  # Let the `with` block use our test db
        )

        mock_generator = MagicMock()
        mock_generator.__next__.return_value = mock_context_manager

        mock_get_db.return_value = mock_generator

        # Run the service method that uses the patched dependency
        await company_service.analyze_company(company.id)

    # 3. Assert
    # The changes should now be visible in our test session.
    db.refresh(company)
    assert company.status == "completed"
    # Verify the JSON fields were updated correctly
    assert company.contact_info["website_url"] == "https://analyzed.com/"
    assert company.analytics["core_business"] == "AI Solutions"

    llm_service_mock.generate_structured_output.assert_called_once()
