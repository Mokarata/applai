# AI Cover Letter Generator

## Project Overview

The AI Cover Letter Generator is a FastAPI application designed to help users create personalized and effective cover letters for job applications. The system leverages the power of Google's Gemini large language model to analyze company information, understand job requirements, and generate tailored cover letters based on a user's profile and resume.

This project serves as a comprehensive portfolio piece demonstrating skills in backend development, AI integration, database management, and API design.

### Key Features

- **User Profile Management**: Users can create accounts, manage their personal information, and upload their resume text.
- **Secure Authentication**: JWT-based authentication ensures that user data is secure and accessible only to the authorized user.
- **Dynamic Job & Company Management**: Users can add new job applications, which automatically triggers an AI-powered analysis of the target company.
- **AI-Powered Company Analysis**: The system uses Google Gemini to research the company's website, extracting its core business, vision, and contact information to enrich the data.
- **Automated Cover Letter Generation**: Generates a personalized cover letter by combining the user's profile, the job description, and the AI-analyzed company data.
- **Interactive Frontend**: A simple and intuitive frontend allows users to interact with all the core features of the application.

## Tech Stack

- **Backend**: FastAPI, Python 3.12
- **Database**: SQLAlchemy ORM, Alembic for migrations, SQLite (for development)
- **AI & Machine Learning**: Google Gemini, LangChain
- **Data Validation**: Pydantic
- **Testing**: Pytest, HTTPX
- **API Documentation**: OpenAPI (via FastAPI's /docs)

## Project Structure

```
.
├── alembic/              # Database migration scripts
├── app/
│   ├── api/              # API endpoints and routing
│   ├── core/             # Core configuration and settings
│   ├── db/               # Database models and session management
│   ├── schemas/          # Pydantic data validation schemas
│   └── services/         # Business logic (user, company, AI services)
├── resources/
│   └── prompts/          # Prompt templates for the LLM
├── static/               # Frontend HTML, CSS, and JavaScript files
├── tests/                # Application tests
├── .env.example          # Example environment variables file
├── main.py               # Main application entry point
└── README.md             # Project documentation
```

## API Endpoints

The application provides a RESTful API for all its core functionalities. The full, interactive API documentation is available at `/docs` when the application is running.

- `POST /token`: Authenticate and receive a JWT access token.
- `POST /users/`: Create a new user.
- `GET /users/me`: Retrieve the current authenticated user's profile.
- `PUT /users/me`: Update the current user's profile.
- `POST /jobs/`: Create a new job application, which triggers company analysis.
- `POST /cover-letters/`: Generate a new cover letter for a user and job.

## Getting Started

Follow these instructions to set up and run the project locally.

### 1. Prerequisites

- Python 3.10+
- An active Google AI Studio API key.

### 2. Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd ai-cover-letter
    ```

2.  **Create a virtual environment using `uv`:**
    ```bash
    uv venv
    ```
    This will create a `.venv` directory in your project folder.

3.  **Install dependencies from `pyproject.toml`:**
    ```bash
    uv pip install -e ".[all]"
    ```
    This command installs the project in editable mode along with all optional dependencies defined in `pyproject.toml`.

### 3. Configuration

1.  **Create an environment file:**
    Copy the example `.env.example` file to a new `.env` file.
    ```bash
    cp .env.example .env
    ```

2.  **Set your environment variables:**
    Open the `.env` file and add your Google API key:
    ```env
    DATABASE_URL="sqlite:///./app.db"
    GOOGLE_API_KEY="your_google_api_key_here"
    SECRET_KEY="your_super_secret_key_for_jwt"
    ALGORITHM="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

### 4. Database Migration

Run the Alembic migrations to set up your database schema:
```bash
uv run alembic upgrade head
```

### 5. Running the Application

Start the FastAPI server using `uv run`:
```bash
uv run uvicorn main:app --reload
```
`uv run` automatically executes the command within the project's virtual environment, so you don't need to activate it manually.

The application will be available at `http://127.0.0.1:8000`.

## Testing

To run the complete test suite, use `uv run`:
```bash
uv run pytest
```
