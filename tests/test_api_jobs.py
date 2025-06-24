import pytest
from unittest.mock import MagicMock, patch
from io import BytesIO

from fastapi import status
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import User, Job

@pytest.mark.asyncio
async def test_create_job_from_text(
    client: AsyncClient, 
    auth_headers: dict, 
    mock_background_tasks: MagicMock
):
    """ Test creating a job by providing raw text."""
    job_text = "Software Engineer at TestCo. Location: Remote."
    response = await client.post(
        "/api/jobs/",
        data={"source_text": job_text},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "processing"
    assert data["source_data"]["type"] == "text"
    assert data["source_data"]["original_value"] == job_text
    mock_background_tasks.add_task.assert_called_once()

@pytest.mark.asyncio
async def test_create_job_from_url(
    client: AsyncClient, 
    auth_headers: dict, 
    mock_background_tasks: MagicMock
):
    """ Test creating a job by providing a URL."""
    job_url = "https://example.com/job/123"
    # Mock the external call to fetch URL content
    with patch('app.utils.text_processing.url_to_text', return_value="Job content from URL") as mock_url_fetch:
        response = await client.post(
            "/api/jobs/",
            data={"source_url": job_url},
            headers=auth_headers
        )
        assert response.status_code == 201
        mock_url_fetch.assert_called_once_with(job_url)
    
    data = response.json()
    assert data["status"] == "processing"
    assert data["source_data"]["type"] == "url"
    assert data["source_data"]["original_value"] == job_url
    mock_background_tasks.add_task.assert_called_once()

@pytest.mark.asyncio
async def test_create_job_from_file(
    client: AsyncClient, 
    auth_headers: dict, 
    mock_background_tasks: MagicMock
):
    """ Test creating a job by uploading a file."""
    file_content = b"This is a plain text job description."
    file_name = "job.txt"
    response = await client.post(
        "/api/jobs/",
        files={"source_files": (file_name, BytesIO(file_content), "text/plain")},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "processing"
    assert data["source_data"]["type"] == "file"
    assert data["source_data"]["filename"] == file_name
    assert data["source_data"]["mime_type"] == "text/plain"
    mock_background_tasks.add_task.assert_called_once()

@pytest.mark.asyncio
async def test_create_job_multiple_sources_fail(client: AsyncClient, auth_headers: dict):
    """ Test that providing multiple sources results in a 400 error."""
    response = await client.post(
        "/api/jobs/",
        data={"source_text": "some text", "source_url": "some_url"},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "Exactly one of" in response.json()["detail"]

@pytest.mark.asyncio
async def test_create_job_no_source_fail(client: AsyncClient, auth_headers: dict):
    """ Test that providing no source results in a 400 error."""
    response = await client.post("/api/jobs/", headers=auth_headers)
    assert response.status_code == 400
    assert "Exactly one of" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_job(client: AsyncClient, auth_headers, test_job):
    # Send request to get the job by ID
    response = await client.get(f"/api/jobs/{test_job.id}", headers=auth_headers)
    
    # Verify response status and job details
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Assuming test_job fixture creates a job with some extracted_data or it's populated by service
    # Adjust assertions based on actual structure of test_job and JobResponse
    if data.get("extracted_data") and data["extracted_data"].get("title"):
        assert data["extracted_data"]["title"] == test_job.extracted_data.get("title", None) 
    assert data["user_id"] == test_job.user_id

@pytest.mark.asyncio
async def test_get_jobs(client: AsyncClient, auth_headers, test_jobs):
    # Send request to list all jobs for the authenticated user
    response = await client.get("/api/jobs/", headers=auth_headers)
    
    # Verify response status and job count
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # test_jobs fixture should create jobs for the current test_user
    # Ensure the length check is appropriate for how test_jobs is defined
    assert len(data) >= 2 # Assuming test_jobs creates at least 2 jobs for the user
    
    # Verify job details, e.g., user_id consistency
    for job_item in data:
        assert job_item["user_id"] == test_jobs[0].user_id # Assuming all jobs in test_jobs belong to same user

@pytest.mark.asyncio
async def test_delete_job(client: AsyncClient, auth_headers, test_job, db):
    # Store job_id for later verification
    job_id = test_job.id
    
    # Send request to delete the job
    response = await client.delete(f"/api/jobs/{job_id}", headers=auth_headers)
    
    # Verify response status
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify job was deleted from database
    deleted_job = db.query(Job).filter(Job.id == job_id).first()
    assert deleted_job is None

@pytest.mark.asyncio
async def test_delete_job_not_found(client: AsyncClient, auth_headers):
    # Try to delete a job with a non-existent ID
    non_existent_id = 9999
    
    # Send request to delete the job
    response = await client.delete(f"/api/jobs/{non_existent_id}", headers=auth_headers)
    
    # Verify response status (should be 404)
    # The service layer's get_job_by_id_or_fail should raise 404 before auth on delete target
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_update_job_self(client: AsyncClient, auth_headers, test_job, db, test_user):
    update_payload = {
        "extracted_data": {"title": "Updated Job Title by Owner"},
        "status": "Manually Reviewed"
    }
    response = await client.put(f"/api/jobs/{test_job.id}", json=update_payload, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["extracted_data"]["title"] == "Updated Job Title by Owner"
    assert data["status"] == "Manually Reviewed"

    db.refresh(test_job)
    assert test_job.extracted_data["title"] == "Updated Job Title by Owner"
    assert test_job.status == "Manually Reviewed"

@pytest.mark.asyncio
async def test_update_job_other_forbidden(client: AsyncClient, auth_headers, test_job, db, test_user):
    # Create another user and their auth headers
    other_user_data = {
        "name": "OtherJob", "surname": "Updater", 
        "user_name": "otherjobupdater",
        "email": "otherjobupdater@example.com", "password": "password123"
    }
    # Assuming direct user creation for simplicity; ideally use UserService or a fixture
    create_user_response = await client.post("/api/users/", json=other_user_data) # No auth for user creation itself
    assert create_user_response.status_code == status.HTTP_201_CREATED
    other_user_email = other_user_data["email"]

    other_login_data = {"username": other_user_email, "password": "password123"}
    token_response = await client.post("/api/auth/token", data=other_login_data)
    assert token_response.status_code == status.HTTP_200_OK
    other_access_token = token_response.json()["access_token"]
    other_auth_headers = {"Authorization": f"Bearer {other_access_token}"}

    update_payload = {"status": "Attempted Update by Other"}
    # other_user tries to update test_job (owned by test_user)
    response = await client.put(f"/api/jobs/{test_job.id}", json=update_payload, headers=other_auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN