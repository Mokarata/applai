import pytest
from app.db.models import User
from fastapi import status

def test_create_user(client):
    # Test data
    user_data = {
        "name": "Test",
        "surname": "User",
        "email": "test@example.com",
        "password": "password123",
        "cv_text": "Test CV"
    }
    
    # Send request to create user
    response = client.post("/api/users/", json=user_data)
    
    # Check response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data
    
    # Password should not be returned
    assert "password" not in data

def test_get_user(client, test_user):
    # Send request to get the user
    response = client.get(f"/api/users/{test_user.id}")
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == test_user.name
    assert data["surname"] == test_user.surname
    assert data["email"] == test_user.email
    assert data["cv_text"] == test_user.cv_text
    
    # Password should not be returned
    assert "password" not in data

def test_get_users(client, test_users):
    # Send request to get all users
    response = client.get("/api/users/")
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2  # At least our 2 users should be there
    
    # Verify user emails are in the response
    user_emails = [user["email"] for user in data]
    assert "test1@example.com" in user_emails
    assert "test2@example.com" in user_emails
    
    # Verify passwords are not included in the response
    for user in data:
        assert "password" not in user

def test_delete_user(client, test_user, db):
    # Store user_id for later verification
    user_id = test_user.id
    
    # Send request to delete the user
    response = client.delete(f"/api/users/{user_id}")
    
    # Check response
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Check that user is deleted
    deleted_user = db.query(User).filter(User.id == user_id).first()
    assert deleted_user is None