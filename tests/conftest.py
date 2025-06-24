import pytest
from typing import AsyncGenerator, Generator

from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.db.database import Base
from app.core.config import settings
from app.core.dependencies import get_db
from app.api.dependencies import get_db, get_llm_service, get_user_service, get_job_service, get_company_service, get_cover_letter_service
from app.db.models import User, Company, Job, JobSourceType
from app.schemas import UserCreate, CompanyCreate, JobCreate, JobExtractedData
from app.services import UserService, JobService, CompanyService
from app.services import LLMServiceProtocol
from unittest.mock import MagicMock, AsyncMock
from fastapi import BackgroundTasks

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
    extract_return_value = JobExtractedData(
        title="Mock Job Title",
        company_name="Mock Company",
        location="Remote",
    )
    mock.extract_job_details = AsyncMock(return_value=extract_return_value)

    # Default mock for other structured output generation (e.g., company analysis)
    # This simulates the CompanyAnalysis schema
    analysis_return_value = MagicMock()
    analysis_return_value.contact_info = {"website": "mock.com"}
    analysis_return_value.analytics = {"industry": "tech"}
    mock.generate_structured_output = AsyncMock(return_value=analysis_return_value)

    return mock

@pytest.fixture(scope="function")
def mock_company_service() -> MagicMock:
    """Provides a mock for the CompanyService."""
    mock = MagicMock(spec=CompanyService)
    mock.create_company = AsyncMock(return_value=(Company(id=1, name="Mock Company"), True))
    return mock

@pytest.fixture(scope="function")
async def client(
    db: Session,
    mock_llm_service: MagicMock,
    mock_company_service: MagicMock,
    mock_background_tasks: MagicMock
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
            background_tasks=background_tasks
        )

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_llm_service] = _override_get_llm_service
    app.dependency_overrides[get_company_service] = _override_get_company_service
    # We override the entire get_job_service to ensure all mocks are injected correctly
    app.dependency_overrides[get_job_service] = lambda: _override_get_job_service(mock_background_tasks)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
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
    test_company: Company,
) -> list[Job]:
    """Create and return a list of test jobs in the database."""
    job_service = JobService(
        db=db, 
        llm_service=mock_llm_service, 
        company_service=mock_company_service, 
        background_tasks=mock_background_tasks
    )
    jobs_in = [
        JobCreate(
            source_type=JobSourceType.text,
            source_value="Senior Python Developer at MockTech Inc. Focus on API development."
        ),
        JobCreate(
            source_type=JobSourceType.text,
            source_value="Junior Frontend Developer at Another Corp. Focus on React."
        ),
    ]

    created_jobs = []
    for job_in in jobs_in:
        created_job = await job_service.create_job(user_id=test_user.id, job_in=job_in)
        created_jobs.append(created_job)
    
    db.flush()
    return created_jobs


@pytest.fixture(scope="function")
async def test_job(
    db: Session,
    mock_llm_service: MagicMock,
    mock_company_service: MagicMock,
    mock_background_tasks: BackgroundTasks,
    test_user: User,
    test_company: Company,
) -> Job:
    """Create and return a test job in the database."""
    job_service = JobService(
        db=db, 
        llm_service=mock_llm_service, 
        company_service=mock_company_service, 
        background_tasks=mock_background_tasks
    )
    job_in = JobCreate(
        source_type=JobSourceType.text,
        source_value="Senior Python Developer at MockTech Inc. Focus on API development."
    )

    # Mock the LLM extraction since it's an async background task
    mock_llm_service.extract_job_details.return_value = JobExtractedData(
        title="Senior Software Engineer",
        company_name=test_company.name,
        location="Remote, USA"
    )

    created_job = await job_service.create_job(user_id=test_user.id, job_in=job_in)
    db.flush()
    return created_job


@pytest.fixture(scope="function")
def test_user(db: Session) -> User:
    """Create and return a test user in the database."""
    user_service = UserService(db)
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
def test_users(db: Session) -> list[User]:
    """Create and return a list of test users in the database."""
    user_service = UserService(db)
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
def test_admin_user(db: Session) -> User:
    """Create and return a test admin user in the database."""
    user_service = UserService(db)
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
async def admin_auth_headers(client: AsyncClient, test_admin_user: User) -> dict[str, str]:
    """Return authentication headers for the test admin user."""
    login_data = {
        "username": test_admin_user.email,
        "password": "adminpassword",
    }
    response = await client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    response.raise_for_status()
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}

