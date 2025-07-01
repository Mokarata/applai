"""API router for all endpoints."""

# FastAPI - API routing components
from fastapi import APIRouter

# Application-specific imports - Endpoint modules
from .endpoints import auth, companies, cover_letters, jobs, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(
    cover_letters.router, prefix="/cover-letters", tags=["cover-letters"]
)
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
