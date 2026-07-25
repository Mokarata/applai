import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import Job
from app.schemas.cover_letter import CoverLetterGenerationResponse


@pytest.mark.parametrize(
    "job_id, generation_options, expected_status",
    [
        (
            1,  # Assuming job with ID 1 exists
            {"style": "professional", "language": "English"},
            200,
        ),
        (
            999,  # Assuming job with ID 999 does not exist
            {"style": "professional", "language": "English"},
            404,
        ),
    ],
)
async def test_generate_cover_letter_only(
    client: TestClient,
    db: Session,
    auth_headers: dict,
    test_job: Job,  # Add the test_job fixture
    job_id: int,
    generation_options: dict,
    expected_status: int,
):  # The `db` fixture is included to ensure the test database is initialized
    """Test generating a cover letter without saving it."""
    response = await client.post(
        f"{settings.API_V1_STR}/cover-letters/generate?job_id={job_id}",
        headers=auth_headers,
        json={"generation_options": generation_options},
    )

    assert response.status_code == expected_status

    if expected_status == 200:
        data = response.json()
        assert "text" in data
        assert "title" in data
        assert "id" not in data  # Should not have an ID as it's not saved
        assert "time_created" not in data  # Should not have a timestamp

        # Validate the response against the new schema
        parsed_response = CoverLetterGenerationResponse.model_validate(data)
        assert parsed_response.job_id == job_id
