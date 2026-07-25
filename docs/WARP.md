# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

AI Cover Letter Generator is a FastAPI application that generates personalized cover letters using LLMs (Gemini, OpenAI, or Groq). It analyzes company information, job requirements, and user profiles to create tailored cover letters.

## Common Commands

### Environment Setup
```bash
# Initialize project and create virtual environment with dependencies (from backend/ directory)
cd backend && uv sync --python 3.12

# This creates:
# - .venv/ with Python 3.12
# - uv.lock for reproducible builds
# - Installs all dependencies from pyproject.toml

# Setup environment variables (from root directory)
cp .env.example .env
# Then edit .env to add your API keys (GOOGLE_API_KEY, OPENAI_API_KEY, or GROQ_API_KEY)

# Add new dependencies (automatically updates uv.lock)
uv add <package-name>

# Add dev dependencies
uv add --dev <package-name>

# Update all dependencies
uv sync --upgrade

# Update specific package
uv add <package-name>@latest
```

### Database
```bash
# Run migrations to latest (from backend/ directory)
cd backend && uv run alembic upgrade head

# Create a new migration after model changes
cd backend && uv run alembic revision --autogenerate -m "description"

# Rollback one migration
cd backend && uv run alembic downgrade -1

# Note: All alembic commands use 'uv run' to execute in the managed environment
```

### Running the Application
```bash
# Start the FastAPI backend server (default port 8000, from backend/ directory)
cd backend && uv run uvicorn app.main:app --reload

# Start with custom port
cd backend && uv run python -m app.main --port 8080

# Run any command in the uv environment
cd backend && uv run <command>

# Start the React frontend (from root directory)
cd frontend && npm start
```

### Testing
```bash
# Run all tests (from backend/ directory)
cd backend && uv run pytest

# Run tests with verbose output
cd backend && uv run pytest -v

# Run specific test file
cd backend && uv run pytest tests/test_api_cover_letters.py

# Run specific test function
cd backend && uv run pytest tests/test_api_cover_letters.py::test_create_cover_letter
```

### Code Quality
```bash
# Format code (from backend/ directory)
cd backend && uv run black .

# Sort imports
cd backend && uv run isort .

# Lint code
cd backend && uv run pylint app/
```

## Architecture

### Service Layer Pattern

The application uses a **Service Layer architecture** that separates business logic from API endpoints:

- **API Endpoints** (`backend/app/api/endpoints/`) - HTTP route handlers, validation, response formatting
- **Services** (`backend/app/services/`) - Core business logic, orchestration
- **Models** (`backend/app/db/models.py`) - SQLAlchemy database models
- **Schemas** (`backend/app/schemas/`) - Pydantic models for request/response validation

**Key principle**: API endpoints should be thin wrappers that delegate to services. All business logic lives in service classes.

### LLM Service Architecture

The app supports **multiple LLM providers** through a Protocol-based design:

1. **`LLMServiceProtocol`** (`backend/app/services/llm_service_protocol.py`) - Defines the interface all LLM services must implement
2. **Concrete implementations**:
   - `GeminiService` - Google Gemini integration
   - `OpenAIService` - OpenAI GPT integration  
   - `GroqService` - Groq integration

3. **Switching LLMs**: Set `ACTIVE_LLM_SERVICE` in `.env` to `GEMINI`, `OPENAI`, or `GROQ`

4. **Dependency injection**: `LLMServiceProvider` in `backend/app/api/dependencies.py` provides a singleton instance based on config

**Key methods**:
- `generate_text_from_prompt()` - For plain text generation
- `generate_structured_output()` - For Pydantic model-structured responses (used for cover letters, job extraction)

### Cover Letter Generation Flow

1. User triggers generation via `/api/cover-letters/generate` endpoint
2. `CoverLetterService.generate_cover_letter_instance()` orchestrates:
   - Fetches user profile and job details from DB
   - Assembles prompts with job/user context
   - Calls `llm_service.generate_structured_output()` with `CoverLetterStructure` schema
   - Returns in-memory instance (not saved)
3. User can then save via `/api/cover-letters/` POST endpoint

**Important**: Generation and saving are separated to allow users to preview before committing.

### Authentication & Authorization

- **JWT-based authentication** (`backend/app/core/security.py`)
- Tokens generated via `/api/auth/token` endpoint
- `get_current_user()` dependency (`backend/app/core/dependencies.py`) validates tokens
- User model includes `is_admin` flag for elevated permissions
- Services perform authorization checks (e.g., `_authorize_cover_letter_access()`)

### Database Models Relationships

```
User (1) ─→ (N) Job ─→ (N) CoverLetter
              ↓
           Company (N:1)
```

- Users can have multiple jobs
- Jobs reference a company (extracted during job creation)
- Cover letters belong to both a user and a job
- Companies are shared across users (deduplicated by name)

### Background Task Processing

Job creation triggers background processing via FastAPI's `BackgroundTasks`:
- Company analysis (fetching company info from website)
- Job detail extraction (parsing job posting)

See `JobService.create_job()` for implementation.

### Prompt Management

LLM prompts are centralized in `backend/app/resources/prompts/`:
- `cover_letter_prompts.py` - Cover letter generation
- `job_prompts.py` - Job detail extraction
- `company_prompts.py` - Company analysis
- `cv_prompts.py` - CV processing

Templates use variable substitution with LangChain's prompt system.

## Configuration

Core settings in `backend/app/core/config.py` using `pydantic-settings`:

**Required environment variables**:
- `DATABASE_URL` - Database connection string (defaults to SQLite)
- `JWT_SECRET_KEY` - Secret for JWT token signing
- At least one LLM API key: `GOOGLE_API_KEY`, `OPENAI_API_KEY`, or `GROQ_API_KEY`
- `ACTIVE_LLM_SERVICE` - Which LLM to use (`GEMINI`, `OPENAI`, or `GROQ`)

**LLM model configuration** is per-service (e.g., `GEMINI_MODEL`, `OPENAI_MODEL`, etc.)

## Testing Philosophy

- **Fixtures in `conftest.py`** provide mock services and test data
- `mock_llm_service` prevents real API calls during tests
- Database uses in-memory SQLite with transaction rollback per test
- `client` fixture provides FastAPI test client with dependency overrides
- Tests verify endpoint behavior, not LLM output quality

## Frontend

React-based SPA in `frontend/`:
- API calls via `services/api.js`
- JWT token stored for authenticated requests
- Development server runs on port 3000
- CORS configured in `backend/app/main.py` to allow frontend origin
