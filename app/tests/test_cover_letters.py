import pytest
from app.db.models import User, Job, CoverLetter
from fastapi import status

def test_create_cover_letter(client, test_user, test_job):
    # Prepare cover letter data
    cover_letter_data = {
        "template_name": "Test Template",
        "cover_letter_text": "Dear Hiring Manager..."
    }
    
    # Send request to create cover letter
    response = client.post(f"/api/cover-letters/?user_id={test_user.id}&job_id={test_job.id}", 
                          json=cover_letter_data)
    
    # Verify response status and content
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["template_name"] == cover_letter_data["template_name"]
    assert data["user_id"] == test_user.id
    assert data["job_id"] == test_job.id

def test_get_cover_letter(client, test_cover_letter):
    # Send request to get cover letter by ID
    response = client.get(f"/api/cover-letters/{test_cover_letter.id}")
    
    # Verify response status and content
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["template_name"] == test_cover_letter.template_name
    assert data["user_id"] == test_cover_letter.user_id
    assert data["job_id"] == test_cover_letter.job_id

def test_get_user_cover_letters(client, test_user, test_cover_letters):
    # Send request to get all cover letters for the user
    response = client.get(f"/api/cover-letters/user/{test_user.id}")
    
    # Verify response status and content
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    
    # Verify all cover letters belong to the test user
    for cover_letter in data:
        assert cover_letter["user_id"] == test_user.id

def test_get_cover_letters(client, test_cover_letters):
    # Send request to get all cover letters
    response = client.get(f"/api/cover-letters/")
    
    # Verify response status and content
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2
    
    # Verify template names are in the response
    template_names = [cl["template_name"] for cl in data]
    assert "Template 1" in template_names
    assert "Template 2" in template_names

def test_delete_cover_letter(client, test_cover_letter, db):
    # Store cover_letter_id for later verification
    cover_letter_id = test_cover_letter.id
    
    # Send request to delete the cover letter
    response = client.delete(f"/api/cover-letters/{cover_letter_id}")
    
    # Check response
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Check that cover letter is deleted
    deleted_cover_letter = db.query(CoverLetter).filter(CoverLetter.id == cover_letter_id).first()
    assert deleted_cover_letter is None
    