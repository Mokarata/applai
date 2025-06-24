# Python standard library - Core language functionality
from contextlib import asynccontextmanager
from pathlib import Path

# FastAPI framework - Web application components
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Application-specific imports - Local modules
from app.api import api_router
from app.core.logging import get_logger
from app.core.config import settings

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
    return HTMLResponse('<html><head><meta http-equiv="refresh" content="0;url=/ui"></head></html>')

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server via __main__")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
