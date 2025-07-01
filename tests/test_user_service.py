from unittest.mock import MagicMock


from sqlalchemy.orm import Session

from app.db.models import User
from app.schemas.common import UserAddress, UserContact
from app.schemas.user import UserUpdate

from app.services.user_service import UserService


def test_update_user_partial_with_placeholders(
    db: Session, test_user: User, mock_llm_service: MagicMock
):
    """
    Tests that updating a user with a partial payload containing placeholder 'string' values
    only updates the fields with actual data, preserving the rest.
    """
    # Arrange: Setup initial user data
    user_service = UserService(db, llm_service=mock_llm_service)
    original_contact_info = {
        "address": {"street": "123 Original St", "city": "Old Town"},
        "phone": "555-1234",
        "linkedin_url": "linkedin.com/original",
    }
    test_user.contact_info = original_contact_info
    test_user.surname = "OriginalSurname"
    db.commit()
    db.refresh(test_user)

    # Act: Simulate an update from a UI that sends placeholders for unchanged fields
    update_payload = UserUpdate(
        name="UpdatedName",  # A real change
        surname="string",  # A placeholder, should be ignored
        contact_info=UserContact(
            address=UserAddress(city="New City"),  # A real nested change
            phone="string",  # A nested placeholder, should be ignored
            linkedin_url="linkedin.com/updated",  # A real change
        ),
    )

    updated_user = user_service.update_user(test_user.id, update_payload, test_user)

    # Assert: Verify that only the intended fields were updated
    db.refresh(updated_user)

    # 1. Check top-level fields
    assert updated_user.name == "UpdatedName"  # This should have changed
    assert updated_user.surname == "OriginalSurname"  # This should NOT have changed

    # 2. Check nested fields
    contact_info = updated_user.contact_info
    assert contact_info is not None
    assert contact_info.get("phone") == "555-1234"  # This should NOT have changed
    assert (
        contact_info.get("linkedin_url") == "linkedin.com/updated"
    )  # This should have changed

    # 3. Check deeply nested fields
    address = contact_info.get("address")
    assert address is not None
    assert address.get("city") == "New City"  # This should have changed
    assert address.get("street") == "123 Original St"  # This should NOT have changed
