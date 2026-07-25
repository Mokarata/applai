from datetime import datetime

from app.schemas.cover_letter import (CoverLetterBase, CoverLetterCreate,
                                      CoverLetterResponse)
from app.schemas.job import JobBase, JobResponse
from app.schemas.user import UserBase, UserCreate, UserResponse


def test_user_schemas():
    """Tests validation for User schemas."""
    user_data = {
        "name": "John",
        "surname": "Doe",
        "user_name": "johndoe",
        "email": "john.doe@example.com",
        "cv_text": "Experienced developer",
    }
    user = UserBase(**user_data)
    assert user.email == "john.doe@example.com"

    user_create = UserCreate(**{**user_data, "password": "securepassword"})
    assert user_create.password == "securepassword"

    user_response = UserResponse(
        **{**user_data, "id": 1, "is_active": True, "is_admin": False}
    )
    assert user_response.id == 1


def test_job_schemas():
    """Tests validation for the refactored Job schemas."""
    # Test JobBase with the new source-agnostic structure
    job_base_data = {
        "source_data": {"source": "http://example.com", "filename": "job.html"},
        "raw_text": "Job description text",
        "status": "pending",
    }
    job = JobBase(**job_base_data)
    assert job.status == "pending"
    assert job.source_data is not None
    assert job.source_data["source"] == "http://example.com"

    # Test JobResponse
    job_response_data = {
        **job_base_data,
        "id": 1,
        "user_id": 1,
        "time_created": datetime.now(),
        "time_updated": datetime.now(),
    }
    job_response = JobResponse(**job_response_data)
    assert job_response.id == 1
    assert job_response.raw_text == "Job description text"


def test_cover_letter_schemas():
    """Tests validation for CoverLetter schemas."""
    # Test CoverLetterBase
    base_data = {"title": "My Title", "text": "Dear Hiring Manager..."}
    cover_letter_base = CoverLetterBase(**base_data)
    assert cover_letter_base.title == "My Title"
    assert cover_letter_base.text == "Dear Hiring Manager..."

    # Test CoverLetterCreate
    create_data = {"generation_options": {"style": "creative"}}
    cover_letter_create = CoverLetterCreate(**create_data)
    assert cover_letter_create.generation_options.style == "creative"

    # Test CoverLetterResponse
    response_data = {
        **base_data,
        "id": 1,
        "user_id": 1,
        "job_id": 1,
        "time_created": datetime.now(),
    }
    cover_letter_response = CoverLetterResponse(**response_data)
    assert cover_letter_response.id == 1
    assert cover_letter_response.title == "My Title"
