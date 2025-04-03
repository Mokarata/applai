import pytest
from app.db.models import User, Job
from fastapi import status

def test_create_job(client, test_user):
    # Prepare job data with the test user's ID
    job_data = {
        "title": "Test Job",
        "description": "Test Description",
        "company": "Test Company",
        "location": "Test Location",
        "user_id": test_user.id
    }
    
    # Send request to create job
    response = client.post("/api/jobs/", json=job_data)
    
    # Verify response status and content
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == job_data["title"]
    assert data["user_id"] == test_user.id

def test_get_job(client, test_job):
    # Send request to get the job by ID
    response = client.get(f"/api/jobs/{test_job.id}")
    
    # Verify response status and job details
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == test_job.title
    assert data["description"] == test_job.description
    assert data["company"] == test_job.company
    assert data["location"] == test_job.location
    assert data["user_id"] == test_job.user_id

def test_get_jobs(client, test_jobs):
    # Send request to list all jobs
    response = client.get("/api/jobs/")
    
    # Verify response status and job count
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2  # At least our 2 jobs should be there
    
    # Verify job titles are in the response
    job_titles = [job["title"] for job in data]
    assert "Test Job 1" in job_titles
    assert "Test Job 2" in job_titles

def test_delete_job(client, test_job, db):
    # Store job_id for later verification
    job_id = test_job.id
    
    # Send request to delete the job
    response = client.delete(f"/api/jobs/{job_id}")
    
    # Verify response status
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify job was deleted from database
    deleted_job = db.query(Job).filter(Job.id == job_id).first()
    assert deleted_job is None

def test_delete_job_not_found(client):
    # Try to delete a job with a non-existent ID
    non_existent_id = 9999
    
    # Send request to delete the job
    response = client.delete(f"/api/jobs/{non_existent_id}")
    
    # Verify response status (should be 404)
    assert response.status_code == status.HTTP_404_NOT_FOUND