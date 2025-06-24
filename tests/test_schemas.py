from app.schemas.user import UserBase, UserCreate, UserResponse
from app.schemas.job import JobBase, JobCreate, JobResponse
from app.schemas.cover_letter import CoverLetterBase, CoverLetterCreate, CoverLetterResponse
from datetime import datetime
from app.db.models import JobSourceType

def test_user_schemas():
    # Test UserBase
    user_data = {
        "name": "John",
        "surname": "Doe",
        "user_name": "johndoe",
        "email": "john.doe@example.com",
        "cv_text": "Experienced developer"
    }
    user = UserBase(**user_data)
    print(f"UserBase validated: {user.model_dump()}")
    
    # Test UserCreate
    user_create_data = {**user_data, "password": "securepassword"}
    user_create = UserCreate(**user_create_data)
    print(f"UserCreate validated: {user_create.model_dump()}")
    
    # Test UserResponse
    user_response_data = {**user_data, "id": 1, "is_active": True, "is_admin": False}
    user_response = UserResponse(**user_response_data)
    print(f"UserResponse validated: {user_response.model_dump()}")

def test_job_schemas():
    # Test JobBase
    job_base_data = {
        "source_data": {
            "type": JobSourceType.text,
            "original_value": "Software Engineer at Google"
        },
        "status": "pending"
    }
    job = JobBase(**job_base_data)
    print(f"JobBase validated: {job.model_dump()}")

    # Test JobCreate
    job_create_data = {
        "source_type": JobSourceType.text,
        "source_value": "Software Engineer at Google"
    }
    job_create = JobCreate(**job_create_data)
    print(f"JobCreate validated: {job_create.model_dump()}")

    # Test JobResponse
    job_response_data = {
        **job_base_data,
        "id": 1,
        "user_id": 1,
        "time_created": datetime.now(),
        "time_updated": datetime.now()
    }
    job_response = JobResponse(**job_response_data)
    print(f"JobResponse validated: {job_response.model_dump()}")

def test_cover_letter_schemas():
    # Test CoverLetterBase
    cover_letter_data = {
        "template_name": "Standard",
        "cover_letter_text": "Dear Hiring Manager..."
    }
    cover_letter = CoverLetterBase(**cover_letter_data)
    print(f"CoverLetterBase validated: {cover_letter.model_dump()}")
    
    # Test CoverLetterCreate
    cover_letter_create = CoverLetterCreate(**cover_letter_data)
    print(f"CoverLetterCreate validated: {cover_letter_create.model_dump()}")
    
    # Test CoverLetterResponse
    cover_letter_response_data = {
        **cover_letter_data, 
        "id": 1, 
        "user_id": 1, 
        "job_id": 1,
        "time_created": datetime.now()
    }
    cover_letter_response = CoverLetterResponse(**cover_letter_response_data)
    print(f"CoverLetterResponse validated: {cover_letter_response.model_dump()}")

if __name__ == "__main__":
    print("Testing User Schemas...")
    test_user_schemas()
    print("\nTesting Job Schemas...")
    test_job_schemas()
    print("\nTesting Cover Letter Schemas...")
    test_cover_letter_schemas()
    print("\nAll schemas validated successfully!")