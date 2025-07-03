# AI Cover Letter Generator (Backend)

This project is a backend application designed to streamline the job application process by automatically generating personalized cover letters. It features a provider-agnostic AI service layer, allowing it to integrate with multiple Large Language Models (LLMs) like Google Gemini, OpenAI's GPT, and Groq.

This project was developed as a learning exercise to explore modern backend technologies, API design, and the practical application of a modular, protocol-driven architecture for AI services.

## Key Features & Architecture

This project is built on a clean, layered architecture that emphasizes separation of concerns and modularity, making it both scalable and maintainable.

-   **Distinct API and Service Layers**: The application is clearly divided into two main layers:
    -   The **API Layer**, built with **FastAPI**, is responsible for handling all incoming HTTP requests, routing, and data validation.
    -   The **Service Layer** contains all the core business logic. It orchestrates database operations, manages user and job data, and interacts with the AI models. This separation ensures that the API layer remains lean and focused on communication, while the complex logic is encapsulated within the services.

-   **Protocol-Driven LLM Services**: At the heart of the AI integration is the `LLMServiceProtocol`. This powerful design pattern defines a standard interface for all AI providers (like Gemini, OpenAI, or Groq). It allows the application to switch between different LLMs via a single configuration change, without altering any code. This makes the system incredibly flexible and easy to extend with new AI models in the future.

-   **Structured Output Handling**: A key challenge with LLMs is getting reliable, structured data. This project solves that by using **Pydantic** models to define the exact output structure required from the AI. This ensures that the data extracted from documents is always consistent, validated, and ready to be used by the application, eliminating unpredictable results.

-   **Core Technologies**: The backend is built with a modern stack including **Python 3.12**, **FastAPI** for the API, **SQLAlchemy** and **Alembic** for database management, and **LangChain** for orchestrating LLM interactions.

## Tech Stack

-   **Backend**: FastAPI, Python 3.12
-   **Database**: SQLAlchemy, Alembic, SQLite
-   **AI & LLM Integration**: LangChain, LangChain-Community, LangChain-Google-Genai, LangChain-OpenAI, LangChain-Groq
-   **Authentication**: Python-JOSE (JWT), Passlib (Bcrypt)
-   **Data Validation & Configuration**: Pydantic, Pydantic-Settings
-   **Dependency Management**: `uv`
-   **Testing**: Pytest, Pytest-Asyncio

## Project Structure

```
.
├── alembic/              # Database migration scripts
│   └── versions/
├── app/
│   ├── api/              # API endpoints and routing
│   ├── core/             # Core configuration, settings, and logging
│   ├── db/               # SQLAlchemy models, session management, and base
│   ├── schemas/          # Pydantic data validation schemas
│   └── services/         # Business logic (user, job, AI services)
├── resources/
│   └── prompts/          # Prompt templates for the LLM
│   └── cover_letters/    # Cover letter templates
│   └── jobs/             # Job templates
│   └── cvs/              # CV templates
├── scripts/              # Utility scripts
├── tests/                # Unit and integration tests
├── .env.example          # Example environment variables file
├── alembic.ini           # Alembic configuration
├── main.py               # Main application entry point
├── pyproject.toml        # Project metadata and dependencies (for UV)
└── README.md             # This file
```

## Endpoints

The full, interactive API documentation (Swagger UI) is available at `http://localhost:8000/docs` when the application is running.

-   **Auth**: 
    `/api/auth/token` 
-   **Users**: 
    `/api/users/` (POST, GET)
    `/api/users/me` (GET, PUT)
    `/api/users/{user_id}` (GET)
    `/api/users/{user_id}` (PUT)
    `/api/users/{user_id}` (DELETE)
-   **Jobs**: 
    `/api/jobs/` (POST, GET)
    `/api/jobs/{job_id}` (GET)
    `/api/jobs/{job_id}` (PUT)
    `/api/jobs/{job_id}` (DELETE)
-   **Cover Letters**: 
    `/api/cover-letters/generate` (POST)
    `/api/cover-letters/{cover_letter_id}` (GET)
    `/api/cover-letters/{cover_letter_id}` (PUT)
    `/api/cover-letters/{cover_letter_id}` (DELETE)

## Getting Started with `uv`

This project uses `uv` as an all-in-one package and environment manager. The following steps outline the correct, `uv`-native workflow.

### 1. Prerequisites

-   Python 3.12+
-   `uv` (can be installed with `pip install uv`)
-   An API key for at least one supported LLM provider (Google, OpenAI, or Groq).

### 2. Environment Setup

1.  **Clone the Repository**
    ```bash
    git clone <your-repository-url>
    cd ai-cover-letter
    ```

2.  **Create the Virtual Environment**
    This command creates a standard Python virtual environment in a `.venv` directory.
    ```bash
    uv venv
    ```

3.  **Activate the Environment**
    Activating the environment configures your shell to use the Python interpreter and tools from within `.venv`. This is standard practice and makes development easier.
    ```bash
    source .venv/bin/activate
    ```
    *After activation, you can run commands like `python`, `pytest`, and `uvicorn` directly.* 

### 3. Dependency Installation

With the environment active, install all project dependencies listed in `pyproject.toml`.
```bash
uv pip install -e ".[all]"
```
*This command installs the project in editable mode (`-e`) along with all optional dependency groups (`[all]`). It is used for the initial setup.* 

**Note on `uv add`**: To add a *new* package to the project later, you would use `uv add <package-name>`.

### 4. Application Configuration

1.  **Create your `.env` file** from the example:
    ```bash
    cp .env.example .env
    ```

2.  **Edit the `.env` file**, setting `ACTIVE_LLM_SERVICE` and providing the corresponding API key and a unique `JWT_SECRET_KEY`.

### 5. Database Migration

Apply the database schema using Alembic. Since the environment is active, you can call `alembic` directly.
```bash
alembic upgrade head
```

### 6. Run the Application

Start the FastAPI server with hot-reloading.
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

## Running Tests

To run the complete test suite, simply run `pytest` from the root directory (while the environment is active).
```bash
pytest
```
*Alternatively, without activating the environment, you could use `uv run pytest`.*
