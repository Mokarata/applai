from fastapi import FastAPI
from app.api import api_router
from app.core.logging import get_logger
from contextlib import asynccontextmanager

# Get a logger for the main module
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Application starting up")
    yield
    # Shutdown logic
    logger.info("Application shutting down")

app = FastAPI(title="AI Cover Letter Generator", lifespan=lifespan)

# Include API router
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to AI Letter Generator API"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server via __main__")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
