# AI Cover Letter Generator - Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [API Reference](#api-reference)
4. [Database Schema](#database-schema)
5. [Authentication](#authentication)
6. [AI Integration](#ai-integration)
7. [Development Setup](#development-setup)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Future Enhancements](#future-enhancements)

## Project Overview

The AI Cover Letter Generator is a FastAPI application that helps users create personalized cover letters for job applications using AI. The system stores user profiles, job descriptions, and generates tailored cover letters based on the user's CV and the job requirements.

### Key Features

- User management (create, retrieve, update, delete)
- Job management (create, retrieve, update, delete)
- Cover letter management (create, retrieve, update, delete)
- AI-powered job data extraction (planned)
- AI-powered cover letter generation (planned)

## Development Roadmap

### Phase 1: Core API (Completed)
- Basic CRUD operations
- Database models
- API endpoints

### Phase 2: AI Integration (In Progress)
- Job data extraction
- Cover letter generation
- Prompt engineering

### Phase 3: User Experience
- Authentication system
- Multiple templates
- PDF export

## System Architecture

The application follows a modern API architecture with clear separation of concerns:

```
app/
├── api/                # API endpoints
│   ├── endpoints/      # Endpoint modules by resource
│   │   ├── users.py
│   │   ├── jobs.py
│   │   └── cover_letters.py
├── core/               # Core application components
├── db/                 # Database models and connection
│   ├── database.py     # Database connection
│   ├── models.py       # SQLAlchemy models
│   └── init_db.py      # Database initialization
├── schemas/            # Pydantic schemas for validation
│   ├── user.py
│   ├── job.py
│   └── cover_letter.py
├── services/           # Business logic services (planned)
│   └── ai_service.py   # AI integration service (planned)
└── tests/              # Test modules
```

## API Reference

### Users API

#### Create User
- **Endpoint**: `POST /api/users/`
- **Description**: Creates a new user
- **Request Body**: UserCreate schema
- **Response**: UserResponse schema
- **Status Codes**: 201 (Created), 400 (Bad Request)

#### Get All Users
- **Endpoint**: `GET /api/users/`
- **Description**: Retrieves all users
- **Response**: List of UserResponse schemas
- **Status Codes**: 200 (OK)

#### Get User by ID
- **Endpoint**: `GET /api/users/{user_id}`
- **Description**: Retrieves a specific user by ID
- **Parameters**: user_id (path)
- **Response**: UserResponse schema
- **Status Codes**: 200 (OK), 404 (Not Found)

#### Delete User
- **Endpoint**: `DELETE /api/users/{user_id}`
- **Description**: Deletes a user by ID
- **Parameters**: user_id (path)
- **Status Codes**: 204 (No Content), 404 (Not Found)

### Jobs API

#### Create Job
- **Endpoint**: `POST /api/jobs/`
- **Description**: Creates a new job
- **Request Body**: JobCreate schema
- **Response**: JobResponse schema
- **Status Codes**: 201 (Created), 404 (Not Found)

#### Get All Jobs
- **Endpoint**: `GET /api/jobs/`
- **Description**: Retrieves all jobs
- **Response**: List of JobResponse schemas
- **Status Codes**: 200 (OK)

#### Get Job by ID
- **Endpoint**: `GET /api/jobs/{job_id}`
- **Description**: Retrieves a specific job by ID
- **Parameters**: job_id (path)
- **Response**: JobResponse schema
- **Status Codes**: 200 (OK), 404 (Not Found)

#### Delete Job
- **Endpoint**: `DELETE /api/jobs/{job_id}`
- **Description**: Deletes a job by ID
- **Parameters**: job_id (path)
- **Status Codes**: 204 (No Content), 404 (Not Found)

### Cover Letters API

#### Create Cover Letter
- **Endpoint**: `POST /api/cover-letters/`
- **Description**: Creates a new cover letter
- **Request Body**: CoverLetterCreate schema
- **Query Parameters**: user_id, job_id
- **Response**: CoverLetterResponse schema
- **Status Codes**: 201 (Created), 404 (Not Found)

#### Get All Cover Letters
- **Endpoint**: `GET /api/cover-letters/`
- **Description**: Retrieves all cover letters
- **Response**: List of CoverLetterResponse schemas
- **Status Codes**: 200 (OK)

#### Get Cover Letter by ID
- **Endpoint**: `GET /api/cover-letters/{cover_letter_id}`
- **Description**: Retrieves a specific cover letter by ID
- **Parameters**: cover_letter_id (path)
- **Response**: CoverLetterResponse schema
- **Status Codes**: 200 (OK), 404 (Not Found)

#### Get User Cover Letters
- **Endpoint**: `GET /api/cover-letters/user/{user_id}`
- **Description**: Retrieves all cover letters for a specific user
- **Parameters**: user_id (path)
- **Response**: List of CoverLetterResponse schemas
- **Status Codes**: 200 (OK), 404 (Not Found)

#### Get Job Cover Letters
- **Endpoint**: `GET /api/cover-letters/job/{job_id}`
- **Description**: Retrieves all cover letters for a specific job
- **Parameters**: job_id (path)
- **Response**: List of CoverLetterResponse schemas
- **Status Codes**: 200 (OK), 404 (Not Found)

#### Delete Cover Letter
- **Endpoint**: `DELETE /api/cover-letters/{cover_letter_id}`
- **Description**: Deletes a cover letter by ID
- **Parameters**: cover_letter_id (path)
- **Status Codes**: 204 (No Content), 404 (Not Found)

## Database Schema

### User Model
- **id**: Integer (Primary Key)
- **name**: String
- **surname**: String
- **email**: String (Unique)
- **password**: String (Hashed)
- **cv_text**: String
- **is_active**: Boolean

### Job Model
- **id**: Integer (Primary Key)
- **title**: String
- **description**: String
- **company**: String
- **location**: String
- **user_id**: Integer (Foreign Key to User)

### Cover Letter Model
- **id**: Integer (Primary Key)
- **template_name**: String
- **cover_letter_text**: String
- **time_created**: DateTime
- **user_id**: Integer (Foreign Key to User)
- **job_id**: Integer (Foreign Key to Job)

## Authentication

The application currently uses password hashing for user security:

- Passwords are hashed using bcrypt before storage
- Authentication system uses CryptContext from passlib
- JWT authentication planned for future implementation

## AI Integration

### Planned AI Features

#### Job Data Extraction (Planned)
- Extract job title, company, and location from job descriptions
- Use Google's Gemini model via LangChain
- Return structured data in JSON format

#### Cover Letter Generation (Planned)
- Generate personalized cover letters based on user CV and job description
- Customize tone and style
- Use LangChain with Google's Gemini model

### AI Implementation Plan

1. Create services directory structure
2. Implement AI service using LangChain with Google's models
3. Add new schema for AI cover letter generation
4. Create new endpoint for generating cover letters with AI
5. Set up environment variables for API keys
6. Add error handling for API failures

## Development Setup

### Prerequisites
- Python 3.8+
- SQLite (development) / PostgreSQL (production)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-cover-letter.git
   cd ai-cover-letter
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   # Create .env file
   touch .env
   
   # Add the following variables
   DATABASE_URL=sqlite:///./app.db
   GOOGLE_API_KEY=your_api_key_here
   ```

5. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

6. Access the API documentation:
   ```
   http://localhost:8000/docs
   ```

## Testing

### Test Structure
- Unit tests for schemas
- Integration tests for endpoints
- Test fixtures for database setup and teardown

### Running Tests
```bash
pytest
```

### Test Coverage
```bash
pytest --cov=app
```

## Deployment

### Production Setup
1. Update environment variables for production
2. Configure database connection for PostgreSQL
3. Set up HTTPS with SSL certificate
4. Configure CORS settings

### Docker Deployment (Planned)
```bash
docker build -t ai-cover-letter .
docker run -p 8000:8000 ai-cover-letter
```

## Future Enhancements

1. **AI Integration**
   - Job data extraction from descriptions
   - Cover letter generation with customizable parameters

2. **Authentication & Security**
   - JWT authentication
   - Role-based access control
   - Rate limiting

3. **User Experience**
   - Multiple cover letter templates
   - PDF export functionality
   - User feedback mechanism

4. **Performance**
   - Caching for frequent requests
   - Asynchronous processing for AI operations

5. **Infrastructure**
   - Containerization with Docker
   - CI/CD pipeline
   - Monitoring and logging