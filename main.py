# Python standard library - Core language functionality
from contextlib import asynccontextmanager
from pathlib import Path
import nltk

# FastAPI framework - Web application components
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles


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

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows the frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


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

# Define base directory
BASE_DIR = Path(__file__).resolve().parent

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Include API router
app.include_router(api_router, prefix="/api")


# UI route
@app.get("/ui", response_class=HTMLResponse)
async def read_ui(request: Request):
    with open(BASE_DIR / "static" / "index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


# Redirect root to UI
@app.get("/", response_class=HTMLResponse)
async def redirect_to_ui():
    logger.info("Root endpoint accessed - redirecting to UI")
    return HTMLResponse(
        '<html><head><meta http-equiv="refresh" content="0;url=/ui"></head></html>'
    )


if __name__ == "__main__":
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser(description="Run the FastAPI application.")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on.")
    args = parser.parse_args()

    logger.info(f"Starting server via __main__ on port {args.port}")
    uvicorn.run("main:app", host="127.0.0.1", port=args.port, reload=True)
