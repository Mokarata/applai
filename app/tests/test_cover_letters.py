import pytest
from app.db.models import User, Job, CoverLetter

def test_create_cover_letter(client, db):
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
    
    # Create a test job
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
    
    # Test data for cover letter
    cover_letter_data = {
        "template_name": "Test Template",
        "cover_letter_text": "Dear Hiring Manager..."
    }
    
    # Send request to create cover letter
    response = client.post(f"/api/cover-letter/?user_id={user_id}&job_id={job_id}", json=cover_letter_data)
    
    # Check response
    assert response.status_code == 201
    data = response.json()
    assert data["template_name"] == cover_letter_data["template_name"]
    assert data["user_id"] == user_id
    assert data["job_id"] == job_id

def test_get_cover_letter(client, db):
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
    
    # Create a test job
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
    
    # Create a test cover letter
    cover_letter = CoverLetter(
        template_name="Test Template",
        cover_letter_text="Dear Hiring Manager...",
        user_id=user_id,
        job_id=job_id
    )
    db.add(cover_letter)
    db.commit()
    db.refresh(cover_letter)
    
    # Store cover_letter_id for later use
    cover_letter_id = cover_letter.id
    
    # Send request to get cover letter
    response = client.get(f"/api/cover-letter/{cover_letter_id}")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["template_name"] == cover_letter.template_name
    assert data["user_id"] == user_id
    assert data["job_id"] == job_id

def test_get_user_cover_letters(client, db):
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
    
    # Create a test job
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
    
    # Create multiple test cover letters for the same user
    cover_letter1 = CoverLetter(
        template_name="Template 1",
        cover_letter_text="Dear Hiring Manager 1...",
        user_id=user_id,
        job_id=job_id
    )
    
    cover_letter2 = CoverLetter(
        template_name="Template 2",
        cover_letter_text="Dear Hiring Manager 2...",
        user_id=user_id,
        job_id=job_id
    )
    
    db.add(cover_letter1)
    db.add(cover_letter2)
    db.commit()
    
    # Send request to get all cover letters for the user
    response = client.get(f"/api/cover-letter/user/{user_id}")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["user_id"] == user_id
    assert data[1]["user_id"] == user_id