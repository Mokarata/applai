import pytest
from app.db.models import User, Job

def test_create_job(client, db):
    # Create a test user first
    user = User(
        name="Test",
        surname="User",
        email="test@example.com",
        password="hashed_password",
        cv_text="Test CV"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Store user_id for later use
    user_id = user.id
    
    # Test data for job
    job_data = {
        "title": "Test Job",
        "description": "Test Description",
        "company": "Test Company",
        "location": "Test Location",
        "user_id": user_id
    }
    
    # Send request to create job
    response = client.post("/api/jobs/", json=job_data)
    
    # Check response
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == job_data["title"]
    assert data["user_id"] == user_id

def test_get_job(client, db):
    # Create a test user
    user = User(
        name="Test",
        surname="User",
        email="test@example.com",
        password="hashed_password",
        cv_text="Test CV"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Store user_id for later use
    user_id = user.id
    
    # Create a test job directly in the database
    job = Job(
        title="Test Job",
        description="Test Description",
        company="Test Company",
        location="Test Location",
        user_id=user_id
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Store job_id for later use
    job_id = job.id
    
    # Send request to get the job
    response = client.get(f"/api/jobs/{job_id}")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == job.title
    assert data["description"] == job.description
    assert data["company"] == job.company
    assert data["location"] == job.location
    assert data["user_id"] == user_id