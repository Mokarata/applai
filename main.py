# Python standard library - Core language functionality
from contextlib import asynccontextmanager

# FastAPI framework - Web application components
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

# Application-specific imports - Local modules
from app.api import api_router
from app.core.config import settings
from app.core.logging import get_logger

# Get a logger for the main module
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Application starting up")
    yield
    # Shutdown logic
    logger.info("Application shutting down")


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Global handler for any unhandled exceptions.
    Logs the error and returns a generic 500 response.
    """
    logger.error(
        f"Unhandled exception for request: {request.method} {request.url}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred."},
    )

# Include API router
app.include_router(api_router, prefix="/api")
