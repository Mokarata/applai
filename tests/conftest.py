# pylint: disable=redefined-outer-name
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import BackgroundTasks
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import (
    get_company_service,
    get_db,
    get_job_service,
    get_llm_service,
)
from app.core.config import settings
from app.db.database import Base
from app.db.models import Company, Job, User
from app.schemas import CompanyCreate, JobCreate, UserCreate, CoverLetterStructure
from app.services import (
    CompanyService,
    JobService,
    LLMServiceProtocol,
    UserService,
)

# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create tables for the test database once per session
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# --- Fixtures ---
@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Yields a new, clean database session for each test function, managing a transaction."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def mock_llm_service() -> MagicMock:
    """Provides a mock for the LLMServiceProtocol with default return values."""
    mock = MagicMock(spec=LLMServiceProtocol)

    # Default mock for job detail extraction
    extract_return_value = {
        "title": "Mock Job Title",
        "company_name": "Mock Company",
        "location": "Remote",
    }
    mock.extract_job_details = AsyncMock(return_value=extract_return_value)

    # Default mock for structured output generation (cover letters)
    cover_letter_return_value = CoverLetterStructure(
        title="Mock Cover Letter",
        applicant_name="Mock Applicant",
        recipient_name="Hiring Manager",
        recipient_title="Lead Recruiter",
        recipient_company="Mock Company Inc.",
        recipient_address="123 Mockingbird Lane, Mocksville, MC 12345",
        greeting="Dear Hiring Manager,",
        introduction="This is a mock introduction.",
        skills="I have many mock skills.",
        projects="I have worked on many mock projects.",
        company_fit="I am a great fit for this mock company.",
        conclusion="This is a mock conclusion.",
        closing="Sincerely,",
    )
    mock.generate_structured_output = AsyncMock(return_value=cover_letter_return_value)

    return mock


@pytest.fixture(scope="function")
def mock_company_service() -> MagicMock:
    """Provides a mock for the CompanyService."""
    mock = MagicMock(spec=CompanyService)
    mock.create_company = AsyncMock(
        return_value=(Company(id=1, name="Mock Company"), True)
    )
    return mock


@pytest.fixture(scope="function")
async def client(
    db: Session,
    mock_llm_service: MagicMock,
    mock_company_service: MagicMock,
    mock_background_tasks: MagicMock,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Yield an AsyncClient instance for the app, with all service dependencies overridden.
    """
    from main import app  # Import app here to avoid premature loading

    def _override_get_db():
        yield db

    def _override_get_llm_service():
        return mock_llm_service

    def _override_get_company_service():
        return mock_company_service

    def _override_get_job_service(background_tasks: BackgroundTasks):
        return JobService(
            db=db,
            llm_service=mock_llm_service,
            company_service=mock_company_service,
            background_tasks=background_tasks,
        )

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_llm_service] = _override_get_llm_service
    app.dependency_overrides[get_company_service] = _override_get_company_service
    # We override the entire get_job_service to ensure all mocks are injected correctly
    app.dependency_overrides[get_job_service] = lambda: _override_get_job_service(
        mock_background_tasks
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def mock_background_tasks() -> MagicMock:
    """Provides a mock for FastAPI's BackgroundTasks."""
    return MagicMock()


@pytest.fixture(scope="function")
def test_company(db: Session) -> Company:
    """Create and return a test company in the database."""
    company_in = CompanyCreate(name="MockTech Inc.")
    company = Company(**company_in.model_dump())
    db.add(company)
    db.flush()
    return company


@pytest.fixture(scope="function")
async def test_jobs(
    db: Session,
    mock_llm_service: MagicMock,
    mock_company_service: MagicMock,
    mock_background_tasks: BackgroundTasks,
    test_user: User,
) -> list[Job]:
    """Create and return a list of test jobs in the database."""
    job_service = JobService(
        db=db,
        llm_service=mock_llm_service,
        company_service=mock_company_service,
        background_tasks=mock_background_tasks,
    )

    job_data = [
        {
            "raw_text": "Senior Python Developer at MockTech Inc.",
            "source_data": {"source": "text"},
        },
        {
            "raw_text": "Junior Frontend Developer at Another Corp.",
            "source_data": {"source": "text"},
        },
    ]
    created_jobs = []
    for data in job_data:
        job_in = JobCreate(**data)
        job = await job_service.create_job(job_in=job_in, current_user=test_user)
        created_jobs.append(job)

    db.flush()
    return created_jobs


@pytest.fixture(scope="function")
async def test_job(
    db: Session,
    mock_llm_service: MagicMock,
    mock_company_service: MagicMock,
    mock_background_tasks: BackgroundTasks,
    test_user: User,
) -> Job:
    """Create and return a test job in the database."""
    job_service = JobService(
        db=db,
        llm_service=mock_llm_service,
        company_service=mock_company_service,
        background_tasks=mock_background_tasks,
    )
    job_in = JobCreate(
        raw_text="Senior Python Developer at MockTech Inc. Focus on API development.",
        source_data={"source": "text"},
    )

    job = await job_service.create_job(job_in=job_in, current_user=test_user)

    db.flush()
    db.commit()
    db.refresh(job)

    return job


@pytest.fixture(scope="function")
def test_user(db: Session, mock_llm_service: MagicMock) -> User:
    """Create and return a test user in the database."""
    user_service = UserService(db, llm_service=mock_llm_service)
    user_in = UserCreate(
        user_name="testuser",
        email="testuser@example.com",
        password="password123",
        name="Test",
        surname="User",
    )
    db_user = user_service.create_user(user_in=user_in)
    db.flush()
    return db_user


@pytest.fixture(scope="function")
def test_users(db: Session, mock_llm_service: MagicMock) -> list[User]:
    """Create and return a list of test users in the database."""
    user_service = UserService(db, llm_service=mock_llm_service)
    users_in = [
        UserCreate(
            user_name="testuser1",
            email="testuser1@example.com",
            password="password123",
            name="Test",
            surname="UserOne",
        ),
        UserCreate(
            user_name="testuser2",
            email="testuser2@example.com",
            password="password456",
            name="Test",
            surname="UserTwo",
        ),
    ]
    created_users = [user_service.create_user(user_in=user) for user in users_in]
    db.flush()
    return created_users


@pytest.fixture(scope="function")
async def auth_headers(client: AsyncClient, test_user: User) -> dict[str, str]:
    """Return authentication headers for the test user."""
    login_data = {
        "username": test_user.email,
        "password": "password123",
    }
    response = await client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    response.raise_for_status()
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture(scope="function")
def test_admin_user(db: Session, mock_llm_service: MagicMock) -> User:
    """Create and return a test admin user in the database."""
    user_service = UserService(db, llm_service=mock_llm_service)
    user_in = UserCreate(
        user_name="adminuser",
        email="admin@example.com",
        password="adminpassword",
        name="Admin",
        surname="User",
        is_admin=True,
    )
    db_user = user_service.create_user(user_in=user_in)
    db.flush()
    return db_user


@pytest.fixture(scope="function")
async def admin_auth_headers(
    client: AsyncClient, test_admin_user: User
) -> dict[str, str]:
    """Return authentication headers for the test admin user."""
    login_data = {
        "username": test_admin_user.email,
        "password": "adminpassword",
    }
    response = await client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    response.raise_for_status()
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}
