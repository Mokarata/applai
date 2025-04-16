from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from app.db.database import Base, get_db
from app.db.models import User, Job, CoverLetter
from main import app

# Use an in-memory SQLite database for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session for each test
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
    # Drop all tables after the test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    # Override the get_db dependency
    def override_get_db():
        try:
            yield db
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear the dependency override after the test
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db):
    """Create a test user that remains bound to the session"""
    user = User(
        name="Test",
        surname="User",
        email="test@example.com",
        password="hashed_password",
        cv_text="Test CV"
    )
    db.add(user)
    db.commit()
    
    # Important: Get a fresh instance from the database
    # This ensures the object is bound to the session
    user_id = user.id
    fresh_user = db.query(User).filter(User.id == user_id).first()
    return fresh_user

@pytest.fixture
def test_job(db, test_user):
    """Create a test job that remains bound to the session"""
    job = Job(
        title="Test Job",
        job_data="Test job raw data",
        company="Test Company",
        location="Test Location",
        user_id=test_user.id
    )
    db.add(job)
    db.commit()
    
    # Get a fresh instance
    job_id = job.id
    fresh_job = db.query(Job).filter(Job.id == job_id).first()
    return fresh_job

@pytest.fixture
def test_cover_letter(db, test_user, test_job):
    """Create a test cover letter that remains bound to the session"""
    cover_letter = CoverLetter(
        template_name="Test Template",
        cover_letter_text="Dear Hiring Manager...",
        user_id=test_user.id,
        job_id=test_job.id
    )
    db.add(cover_letter)
    db.commit()
    
    # Get a fresh instance
    cover_letter_id = cover_letter.id
    fresh_cover_letter = db.query(CoverLetter).filter(CoverLetter.id == cover_letter_id).first()
    return fresh_cover_letter

@pytest.fixture
def test_users(db):
    """Create multiple test users that remain bound to the session"""
    user1 = User(
        name="Test1",
        surname="User1",
        email="test1@example.com",
        password="hashed_password1",
        cv_text="Test CV 1"
    )
    
    user2 = User(
        name="Test2",
        surname="User2",
        email="test2@example.com",
        password="hashed_password2",
        cv_text="Test CV 2"
    )
    
    db.add(user1)
    db.add(user2)
    db.commit()
    
    # Return fresh instances
    users = db.query(User).filter(
        User.name.in_(['Test1', 'Test2'])
    ).all()
    return users
    
@pytest.fixture
def test_jobs(db, test_user):
    """Create multiple test jobs for the same user"""
    job1 = Job(
        title="Test Job 1",
        job_data="Job 1 raw data",
        company="Test Company 1",
        location="Test Location 1",
        user_id=test_user.id
    )
    
    job2 = Job(
        title="Test Job 2",
        job_data="Job 2 raw data",
        company="Test Company 2",
        location="Test Location 2",
        user_id=test_user.id
    )
    
    db.add(job1)
    db.add(job2)
    db.commit()
    
    # Return fresh instances
    jobs = db.query(Job).filter(
        Job.title.in_(["Test Job 1", "Test Job 2"])
    ).all()
    return jobs

@pytest.fixture
def test_cover_letters(db, test_user, test_job):
    """Create multiple test cover letters"""
    cover_letter1 = CoverLetter(
        template_name="Template 1",
        cover_letter_text="Dear Hiring Manager 1...",
        user_id=test_user.id,
        job_id=test_job.id
    )
    
    cover_letter2 = CoverLetter(
        template_name="Template 2",
        cover_letter_text="Dear Hiring Manager 2...",
        user_id=test_user.id,
        job_id=test_job.id
    )
    
    db.add(cover_letter1)
    db.add(cover_letter2)
    db.commit()
    
    # Return fresh instances
    cover_letters = db.query(CoverLetter).filter(
        CoverLetter.template_name.in_(["Template 1", "Template 2"])
    ).all()
    return cover_letters