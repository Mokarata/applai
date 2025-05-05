# AI Cover Letter Generator - Development Checklist

## 1. Project Setup & Basic Structure

- [x] Initialize FastAPI application
- [x] Set up database models (User, Job, CoverLetter in `app/db/models.py`)
- [x] Create Pydantic schemas (`app/schemas/` - User, Job, CoverLetter)
- [x] Implement basic CRUD endpoints (User, Job, CoverLetter in `app/api/endpoints/`)
- [x] Add dependency injection for database (`get_db` in `app/db/database.py`)
- [x] Set up testing framework (Basic structure exists in `app/tests/`, `conftest.py`)
- [ ] Add code quality tools (pylint, prettier - Setup needed)
- [x] Add python-multipart to requirements.txt (Required for `/jobs/upload`)

## 2. Core API Implementation

- [x] User management endpoints (`/users/`, includes CRUD)
- [x] Job management endpoints (`/jobs/`, includes CRUD, extraction logic, `/upload`)
- [x] Cover letter management endpoints (`/cover-letters/`, includes CRUD, generation logic)
- [x] API path/parameter fixes applied (Confirmed via memories)
- [x] Basic Input validation (via Pydantic schemas)
- [x] Basic Error handling (HTTPExceptions in endpoints, try/except in service)
- [ ] Implement robust Authentication system (Currently only password hashing in User CRUD)
- [ ] Set up comprehensive Python logging and FastAPI exception handlers (Basic logging in place)
- [ ] Implement FastAPI dependency injection for services (e.g., `Depends(get_ai_service)`)

## 3. Frontend Implementation (static/js/main.js - Based on Memories)

- [x] Basic HTML Structure & CSS Styling
- [x] Add Job Modal (Multi-panel: URL, Text, File, Manual)
- [x] User Profile Management (Load, Display, Update, Save, Resume Upload)
- [x] Chat Interface (Send/Receive Messages)
- [x] Formatted Cover Letter Display (`addFormattedBotMessage`)
- [x] NotebookLM-style UI Enhancements (Quick Options, Suggested Prompts)
- [x] API Integration (Users, Jobs, Cover Letters - paths fixed)
- [x] Close Job Modal Error Handling (Safely reset fields)
- [ ] Add loading indicators during API calls
- [ ] Implement frontend testing framework/tests
- [ ] Refine UI/UX based on further testing/feedback

## 4. AI Integration - Phase 1: Job Data Extraction (`app/services/gemini_service.py`)

- [ ] Research and select LLM (Gemini chosen, but formally document comparison/decision)
  - [ ] Create comparison table (e.g., Gemini vs OpenAI vs Groq based on `Info.md` template)
  - [ ] Document final LLM recommendation/choice
- [x] Create AI service structure (`GeminiService` class)
- [x] Use LangChain for prompt templating (`ChatPromptTemplate` etc.)
- [x] Implement job data extraction logic using Gemini (`extract_job_data` method)
- [x] Separate System/User prompts (`resources/prompts/`)
- [x] Return data in structured JSON format (with cleaning and parsing)
- [x] Basic error handling in AI service (try/except, logging, fallbacks)
- [ ] Store extracted data robustly in database (Currently done within `create_job` endpoint logic)
- [ ] Test edge cases in job extraction (missing info, multiple locations etc.)
- [ ] *Note: `app/schemas/job_extraction.py` exists but doesn't seem used in primary `/jobs` endpoint.*

## 5. AI Integration - Phase 2: Cover Letter Generation (`app/services/gemini_service.py`)

- [ ] Decide on AI Service Connection Method (e.g., `google-generativeai` SDK, `litellm`, etc.)
- [x] Create cover letter generation endpoint (`/cover-letters/`)
- [x] Implement AI service using Google Gemini (`generate_cover_letter` method)
- [x] Use LangChain for prompt templating
- [x] Design modular prompts (System/User separation in `resources/prompts/`)
  - [x] Create system prompt defining AI's role
  - [x] User prompt uses job details and user profile
- [x] Implement basic structured output format (Text generation, basic cleaning)
- [ ] Define explicit structured output schema (e.g., Pydantic model for response validation - see `Info.md` notes)
- [ ] Process and store AI response robustly in database
- [ ] Collect 10-20 sample cover letters as text files (Mentioned as needed in memory/`Info.md`)
- [ ] Add support for different cover letter styles (Formal, Creative, etc.)
- [ ] Test generation with diverse sample cover letters
- [ ] Add customization options (tone, style, length) via API/UI

## 6. Testing & Quality Assurance

- [ ] Unit tests for schemas
- [ ] Integration tests for API endpoints (using TestClient)
- [ ] Test fixtures and helpers (Basic `conftest.py` exists)
- [ ] Measure and improve test coverage
- [ ] Performance testing for API and AI calls
- [ ] Refactor tests to use FastAPI TestClient and pytest; add httpx dependency; use fixtures for test DB and service mocks

## 7. Prompt Engineering & Best Practices

- [x] Document the system/user message separation pattern used (Implicitly done via code structure)
- [ ] Create dedicated prompt documentation (Define prompts formally)
- [ ] Create UML/Diagram illustrating prompt flow
- [ ] Create standardized prompt template library (Current structure is good start)
- [ ] Implement prompt versioning system (if complexity increases)
- [ ] Develop prompt testing framework
- [ ] Create reusable prompt components
- [ ] Optimize prompts for token efficiency and cost
- [ ] Document best-performing prompts and parameters
- [ ] Implement feedback mechanism for continuous improvement

## 8. AI Testing & Quality Assurance

- [ ] Create unit tests for prompt templates
- [ ] Implement evaluation metrics for cover letter quality (e.g., relevance, coherence)
- [ ] Create automated test suite for AI components
- [ ] Set up monitoring for AI service performance and errors
- [ ] Develop regression testing strategy for prompt changes

## 9. AI Model Optimization

- [ ] Benchmark response times for different models/settings
- [ ] Implement caching strategies for common requests (if applicable)
- [ ] Optimize temperature and other generation parameters
- [ ] Add fallback mechanisms for AI API failures
- [ ] Implement rate limiting and quota management for AI calls
- [ ] Create performance dashboard (if needed)

## 10. Environment & Configuration

- [x] Use `.env` file for environment variables (API keys, DB_URL)
- [ ] Implement Pydantic BaseSettings for centralized configuration (`app/core/config.py` - Check if exists/needed, mentioned in `Info.md`)
- [ ] Implement more secure API key handling (e.g., Secret Manager)
- [ ] Add rate limiting protection (e.g., `slowapi`)
- [ ] Configure deployment settings (Dockerfile, server config)
- [ ] Set up Alembic migrations and remove `create_all`/`/recreate-tables` (No migrations seen)

## 11. Documentation & Deployment

- [x] Basic API documentation via FastAPI Swagger/OpenAPI
- [ ] Write comprehensive User Guide
- [ ] Create Deployment Instructions
- [ ] Final testing in production-like environment

## 12. Future Enhancements

- [ ] Support for PDF/DOCX job descriptions
- [ ] Enhanced prompt engineering (e.g., dynamic examples)
- [ ] Multiple template options selectable by user
- [ ] User feedback mechanism on generated letters
- [ ] Performance optimization (frontend/backend)
- [ ] Add ability to edit saved jobs (Endpoint exists, FE wiring?)
- [ ] Resolve `source_data` vs `job_data` schema mismatch (as noted in memory)
- [ ] Implement Cover Letter Ranking Feature (See `Info.md`)
  - [ ] Design ranking criteria/matrix
  - [ ] Create ranking database table
  - [ ] Implement ranking API endpoint(s)
  - [ ] Integrate LLM for ranking evaluation
- [ ] Implement Cover Letter Export Feature (md, pdf - See `Info.md`)
  - [ ] Create export API endpoint
  - [ ] Add file generation logic (e.g., using `markdown-pdf` or similar)

## Resources

- [Structured Output with Gemini API](https://ai.google.dev/gemini-api/docs/structured-output?lang=python)
- [AI Engineering Guide](https://www.notion.so/masterschool/AI-Engineering-Mohamad-1b39418319f380809084f9abfe19d236)
- [LLM Comparison Table](https://www.notion.so/masterschool/Comparison-Table-1b39418319f381a0b860cb64f6c187f1)