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
from app.db.database import SessionLocal
from app.db.models import User
from app.core.security import get_password_hash

# Get a logger for the main module
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Application starting up")
    # Ensure database tables exist to avoid 'no such table' at runtime
    try:
        from app.db.database import Base, engine
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ensured (create_all)")

        # Seed an admin user if none exists and ADMIN_NEW_PWD provided
        if settings.ADMIN_NEW_PWD:
            db = SessionLocal()
            try:
                admin = db.query(User).filter(User.is_admin == True).first()  # noqa: E712
                if not admin:
                    hashed = get_password_hash(settings.ADMIN_NEW_PWD)
                    admin = User(
                        name=settings.ADMIN_NAME,
                        surname=settings.ADMIN_SURNAME,
                        user_name=settings.ADMIN_USERNAME,
                        email=settings.ADMIN_EMAIL,
                        hashed_password=hashed,
                        is_admin=True,
                        is_active=True,
                    )
                    db.add(admin)
                    db.commit()
                    logger.info("Bootstrapped admin user '%s' (email: %s)", admin.user_name, admin.email)
                else:
                    updated = False
                    if settings.ADMIN_EMAIL and admin.email != settings.ADMIN_EMAIL:
                        admin.email = settings.ADMIN_EMAIL
                        updated = True
                    if settings.ADMIN_USERNAME and admin.user_name != settings.ADMIN_USERNAME:
                        admin.user_name = settings.ADMIN_USERNAME
                        updated = True
                    if updated:
                        db.commit()
                        logger.info("Updated existing admin credentials to email '%s', username '%s'", admin.email, admin.user_name)
            except Exception:
                db.rollback()
                logger.exception("Failed to bootstrap admin user at startup")
            finally:
                db.close()
        else:
            logger.info("ADMIN_NEW_PWD not set; skipping admin bootstrap")
    except Exception:
        logger.exception("Database initialization failed during startup")
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


# Include API router
app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser(description="Run the FastAPI application.")
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to run the server on."
    )
    args = parser.parse_args()

    logger.info(f"Starting server via __main__ on port {args.port}")
    uvicorn.run("main:app", host="127.0.0.1", port=args.port, reload=True)
