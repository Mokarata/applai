from datetime import datetime
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.db.models import Company
from app.schemas.company import CompanyUpdate


# Helper to create a valid company object for mocking
def create_mock_company(id: int, name: str) -> Company:
    now = datetime.now()
    return Company(
        id=id, name=name, status="pending", time_created=now, time_updated=now
    )


@pytest.mark.asyncio
async def test_list_companies(
    client: AsyncClient, mock_company_service: MagicMock, auth_headers: dict
) -> None:
    mock_companies = [
        create_mock_company(1, "Test Co 1"),
        create_mock_company(2, "Test Co 2"),
    ]
    mock_company_service.get_companies.return_value = mock_companies
    response = await client.get(
        f"{settings.API_V1_STR}/companies/", headers=auth_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 2
    assert content[0]["name"] == "Test Co 1"


@pytest.mark.asyncio
async def test_read_company(
    client: AsyncClient, mock_company_service: MagicMock, auth_headers: dict
) -> None:
    company = create_mock_company(1, "Test Co")
    mock_company_service.get_company.return_value = company
    response = await client.get(
        f"{settings.API_V1_STR}/companies/{company.id}", headers=auth_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == company.name


@pytest.mark.asyncio
async def test_update_company(
    client: AsyncClient, mock_company_service: MagicMock, auth_headers: dict
) -> None:
    updated_company = create_mock_company(1, "Updated Name")
    mock_company_service.update_company.return_value = updated_company
    data = CompanyUpdate(name="Updated Name")
    response = await client.put(
        f"{settings.API_V1_STR}/companies/1",
        json=data.model_dump(),
        headers=auth_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_delete_company(
    client: AsyncClient, mock_company_service: MagicMock, auth_headers: dict
) -> None:
    company_to_delete = create_mock_company(1, "Test Co")
    mock_company_service.delete_company.return_value = company_to_delete
    response = await client.delete(
        f"{settings.API_V1_STR}/companies/{company_to_delete.id}", headers=auth_headers
    )
    assert response.status_code == 204

    # Verify that the company is gone
    mock_company_service.get_company.return_value = None
    response = await client.get(
        f"{settings.API_V1_STR}/companies/{company_to_delete.id}", headers=auth_headers
    )
    assert response.status_code == 404
