import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock

from app.db.models import Job, User
from app.schemas.cover_letter import CoverLetterStructure


@pytest.mark.asyncio
async def test_create_cover_letter(
    client: AsyncClient,
    test_job: Job,
    test_user: User,
    auth_headers: dict[str, str],
    mock_llm_service: MagicMock,
):
    """Test creating a cover letter successfully."""
    # Arrange
    mock_letter_structure = CoverLetterStructure(
        introduction="Mocked introduction.",
        body="Mocked body.",
        conclusion="Mocked conclusion.",
    )
    mock_llm_service.generate_structured_output.return_value = mock_letter_structure

    request_data = {
        "generation_options": {"length": "medium", "style": "professional"}
    }
    params = {"job_id": test_job.id}

    # Act
    response = await client.post(
        "/api/cover-letters/",
        json=request_data,
        params=params,
        headers=auth_headers,
    )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["job_id"] == test_job.id
    assert "text" in data
    assert "Mocked introduction." in data["text"]
    assert "Mocked conclusion." in data["text"]

    # Verify that the mock was called
    mock_llm_service.generate_structured_output.assert_called_once()
