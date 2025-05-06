# SQLAlchemy - Database ORM components
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# Python standard library - Core language functionality
import enum

# Local application imports - Database connection
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    surname = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    cv_text = Column(String)
    is_active = Column(Boolean, default=True)

    # Relationships
    jobs = relationship("Job", back_populates="user")
    cover_letters = relationship("CoverLetter", back_populates="user")

# Define an Enum for the source type
class JobSourceType(enum.Enum):
    url = "url"
    file = "file",
    text = "text",
    manual = "manual"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # --- Source Information ---
    source_type = Column(Enum(JobSourceType), nullable=False, index=True)
    source_value = Column(Text, nullable=False) # URL, file path, or text content
    source_filename = Column(String, nullable=True) # filename if file source
    source_mime_type = Column(String, nullable=True) # MIME type if file source

    # --- Extracted/Structured Information (Populated after Gemini processing) ---
    title = Column(String, index=True, nullable=True)
    company = Column(String, index=True, nullable=True)
    location = Column(String, nullable=True)
    job_url = Column(String, nullable=True) # Extracted/provided
    date_posted = Column(DateTime(timezone=True), nullable=True)
    submission_deadline = Column(DateTime(timezone=True), nullable=True)
    hiring_manager = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending", index=True)
    full_description = Column(Text, nullable=True) # Extracted full text

     # --- Timestamps ---
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) # Added server_default
    
    # --- Relationships ---
    user = relationship("User", back_populates="jobs")
    cover_letters = relationship("CoverLetter", back_populates="job", cascade="all, delete-orphan")

    # Removed the redundant 'job_data' column definition from the Job model.

class CoverLetter(Base):
    __tablename__ = "cover_letters"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True, index=True)
    generation_options = Column(JSON, nullable=True) 
    sections = Column(JSON, nullable=True) # Keep this for structured data
    # Add this column for the assembled text
    cover_letter_text = Column(Text, nullable=True) 
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))

    # Relationships
    user = relationship("User", back_populates="cover_letters")
    job = relationship("Job", back_populates="cover_letters")