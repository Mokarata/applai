from fastapi import APIRouter
from app.api.endpoints import users, jobs, cover_letters

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(cover_letters.router, prefix="/cover-letters", tags=["cover-letters"])