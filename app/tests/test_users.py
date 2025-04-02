import pytest
from app.db.models import User

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
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data
    
    # Password should not be returned
    assert "password" not in data

def test_get_user(client, db):
    # Create a test user directly in the database
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
    
    # Send request to get the user
    response = client.get(f"/api/users/{user_id}")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == user.name
    assert data["surname"] == user.surname
    assert data["email"] == user.email
    assert data["cv_text"] == user.cv_text
    
    # Password should not be returned
    assert "password" not in data