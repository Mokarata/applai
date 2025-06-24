"""
Database configuration and session management
"""
# SQLAlchemy components - Database toolkit
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Application configuration - Central settings
from app.core.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {} 
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class
Base = declarative_base()

# Database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()