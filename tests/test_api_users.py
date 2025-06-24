import pytest
from app.db.models import User
from sqlalchemy.orm import Session
from fastapi import status

@pytest.mark.asyncio
async def test_create_user(client):
    # Test data
    user_data = {
        "name": "Test",
        "surname": "User",
        "user_name": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "cv_text": "Test CV"
    }
    
    # Send request to create user
    response = await client.post("/api/users/", json=user_data)
    
    # Check response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data
    
    # Password should not be returned
    assert "password" not in data

@pytest.mark.asyncio
async def test_get_user(client, auth_headers, test_user):
    # Send request to get the user
    response = await client.get(f"/api/users/{test_user.id}", headers=auth_headers)
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == test_user.name
    assert data["surname"] == test_user.surname
    assert data["email"] == test_user.email
    assert data["cv_text"] == test_user.cv_text
    
    # Password should not be returned
    assert "password" not in data

@pytest.mark.asyncio
async def test_get_users(client, admin_auth_headers, db: Session, test_users):
    # Send request to get all users
    response = await client.get("/api/users/", headers=admin_auth_headers)
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2  # At least our 2 users should be there
    
    # Verify user emails are in the response
    user_emails = [user["email"] for user in data]
    assert "testuser1@example.com" in user_emails
    assert "testuser2@example.com" in user_emails
    
    # Verify passwords are not included in the response
    for user in data:
        assert "password" not in user

@pytest.mark.asyncio
async def test_delete_user(client, auth_headers, db: Session, test_user):
    # Store user_id for later verification
    user_id = test_user.id
    
    # Send request to delete the user
    response = await client.delete(f"/api/users/{user_id}", headers=auth_headers)
    
    # Check response
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Check that user is deleted
    deleted_user = db.query(User).filter(User.id == user_id).first()
    assert deleted_user is None

@pytest.mark.asyncio
async def test_get_current_user_me(client, auth_headers, test_user):
    response = await client.get("/api/users/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email
    assert data["id"] == test_user.id

@pytest.mark.asyncio
async def test_update_user_self(client, auth_headers, db: Session, test_user):
    update_data = {"name": "Updated Name", "surname": "Updated Surname"}
    response = await client.put(f"/api/users/{test_user.id}", json=update_data, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["surname"] == "Updated Surname"

    db.refresh(test_user)
    assert test_user.name == "Updated Name"

@pytest.mark.asyncio
async def test_update_user_other_forbidden(client, auth_headers, db: Session, test_user):
    # Create another user
    other_user_data = {
        "name": "Other",
        "surname": "User",
        "user_name": "otheruser",
        "email": "other@example.com",
        "password": "password123"
    }
    create_response = await client.post("/api/users/", json=other_user_data) # No auth for creation
    assert create_response.status_code == status.HTTP_201_CREATED
    other_user_id = create_response.json()["id"]

    update_data = {"name": "Attempted Update"}
    # test_user (non-admin) tries to update other_user
    response = await client.put(f"/api/users/{other_user_id}", json=update_data, headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

# To test admin updating another user, you'd need a fixture for an admin user and their auth_headers
# For example:
# @pytest.mark.asyncio
# async def test_update_user_other_by_admin(client, admin_auth_headers, test_user, db):
#     update_data = {"name": "Admin Updated Name"}
#     response = await client.put(f"/api/users/{test_user.id}", json=update_data, headers=admin_auth_headers)
#     assert response.status_code == status.HTTP_200_OK
#     data = response.json()
#     assert data["name"] == "Admin Updated Name"