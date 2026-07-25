# Project Structure

This document describes the professional FastAPI + React project structure following industry best practices.

## Overview

```
ai_cover_letter/
├── backend/                    # FastAPI backend application
│   ├── app/                    # Main application package
│   │   ├── api/                # API routes and endpoints
│   │   │   ├── endpoints/      # Individual endpoint modules
│   │   │   ├── api.py          # API router configuration
│   │   │   └── dependencies.py # Dependency injection
│   │   ├── core/               # Core functionality
│   │   │   ├── config.py       # Settings and configuration
│   │   │   ├── security.py     # Authentication & security
│   │   │   ├── logging.py      # Logging configuration
│   │   │   └── dependencies.py # Core dependencies
│   │   ├── db/                 # Database layer
│   │   │   ├── models.py       # SQLAlchemy models
│   │   │   └── database.py     # Database connection
│   │   ├── schemas/            # Pydantic models
│   │   │   └── *.py            # Request/response schemas
│   │   ├── services/           # Business logic layer
│   │   │   ├── company_service.py
│   │   │   ├── cover_letter_service.py
│   │   │   ├── job_service.py
│   │   │   ├── user_service.py
│   │   │   ├── gemini_service.py
│   │   │   ├── openai_service.py
│   │   │   ├── groq_service.py
│   │   │   └── llm_service_protocol.py
│   │   ├── utils/              # Utility functions
│   │   ├── resources/          # Static resources
│   │   │   └── prompts/        # LLM prompts
│   │   ├── alembic/            # Database migrations
│   │   │   └── versions/       # Migration scripts
│   │   └── main.py             # FastAPI application entry point
│   ├── tests/                  # Test suite
│   │   ├── api/                # API endpoint tests
│   │   ├── utils/              # Test utilities
│   │   ├── conftest.py         # Pytest configuration
│   │   └── test_*.py           # Test modules
│   ├── scripts/                # Backend utility scripts
│   │   └── promote_admin.py    # Admin promotion script
│   ├── alembic.ini             # Alembic configuration
│   ├── pyproject.toml          # Python dependencies
│   └── uv.lock                 # Dependency lock file
│
├── frontend/                   # React frontend application
│   ├── public/                 # Static assets
│   ├── src/                    # Source code
│   │   ├── components/         # React components
│   │   ├── services/           # API client services
│   │   ├── App.js              # Root component
│   │   └── index.js            # Entry point
│   ├── package.json            # Node dependencies
│   └── ...
│
├── data/                       # Runtime data (gitignored)
│   ├── app.db                  # SQLite database
│   ├── test.db                 # Test database
│   └── logs/                   # Application logs
│
├── docs/                       # Documentation
│   ├── WARP.md                 # Warp AI assistant guide
│   ├── PROJECT_STRUCTURE.md    # This file
│   ├── PROJECT_STATUS.md       # Current project status
│   └── *.md                    # Other documentation
│
├── scripts/                    # Deployment scripts (future use)
│
├── .env                        # Environment variables (gitignored)
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── .python-version             # Python version specification
├── README.md                   # Main project README
└── mcp.config.json             # MCP configuration

```

## Architecture Principles

### 1. **Separation of Concerns**
- **Backend** and **frontend** are completely separated at the root level
- Each has its own dependencies, configuration, and deployment strategy
- Clear API boundaries between frontend and backend

### 2. **Backend Structure**
Following the official FastAPI full-stack template structure:

- **`backend/app/`**: Contains all application code
  - **`api/`**: HTTP layer - thin controllers that delegate to services
  - **`services/`**: Business logic layer - the core application logic
  - **`db/`**: Data persistence layer - models and database config
  - **`schemas/`**: Data validation - Pydantic models
  - **`core/`**: Cross-cutting concerns - config, security, logging
  - **`utils/`**: Shared utilities
  - **`resources/`**: Static resources like prompts

- **`backend/tests/`**: All tests live with the backend code
- **`backend/scripts/`**: Backend-specific scripts

### 3. **Service Layer Pattern**
The application uses a **service layer** architecture:
- API endpoints are thin wrappers that handle HTTP concerns
- Services contain all business logic
- Services are injected via FastAPI's dependency injection
- This makes the code testable and maintainable

### 4. **LLM Integration Architecture**
The app supports multiple LLM providers through a Protocol-based design:
- `LLMServiceProtocol` defines the interface
- Concrete implementations for Gemini, OpenAI, and Groq
- Configuration-based provider selection
- Centralized prompt management in `resources/prompts/`

### 5. **Database Management**
- Alembic for migrations lives in `backend/app/alembic/`
- Database files are stored in `data/` directory (gitignored)
- SQLite for development, PostgreSQL for production (configurable)

### 6. **Testing Strategy**
- Tests mirror the application structure
- Fixtures in `conftest.py` provide mocked services
- In-memory SQLite for test isolation
- Dependency overrides for testing

### 7. **Documentation**
- All documentation lives in `docs/` directory
- `WARP.md` provides context for AI assistants
- Technical documentation in separate files
- README.md at root provides quick start guide

## Running the Application

### Backend
```bash
cd backend
uv pip install -e "."
uv run uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm start
```

### Database Migrations
```bash
cd backend
uv run alembic upgrade head
```

### Tests
```bash
cd backend
uv run pytest
```

## Benefits of This Structure

1. **Industry Standard**: Follows patterns used by major projects and the official FastAPI template
2. **Scalability**: Clear separation allows independent scaling of frontend/backend
3. **Maintainability**: Logical organization makes code easy to find and modify
4. **Testability**: Service layer and dependency injection enable comprehensive testing
5. **Deployment Ready**: Structure supports containerization and modern deployment practices
6. **Developer Experience**: Clear conventions reduce cognitive load
7. **AI-Friendly**: Well-organized structure works better with AI coding assistants

## Migration Notes

This structure was migrated from a flat `src/` layout to follow production best practices based on:
- FastAPI's official full-stack template (38k+ stars)
- BCG-X's AgentKit for AI applications
- Industry standards for full-stack Python applications

The migration maintains 100% functionality while improving organization and maintainability.
