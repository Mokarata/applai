# SQLAlchemy - Database ORM components
# Python standard library - Core language functionality
import enum

from sqlalchemy import (JSON, Boolean, Column, DateTime, Enum, ForeignKey,
                        Integer, String, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Local application imports - Database connection
from .database import Base


# --- User Model ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    surname = Column(String, index=True, nullable=False)
    user_name = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    cv_text = Column(String, nullable=True)
    cv_source_metadata = Column(JSON, nullable=True)
    structured_cv_data = Column(JSON, nullable=True)
    contact_info = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, server_default="true", nullable=False)
    is_admin = Column(Boolean, default=False, server_default="false", nullable=False)

    # Relationships
    jobs = relationship("Job", back_populates="user")
    cover_letters = relationship("CoverLetter", back_populates="user")


# --- Job Model ---
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    status = Column(String, nullable=False, default="pending", index=True)

    # --- Source Information ---
    source_data = Column(JSON, nullable=False)
    raw_text = Column(Text, nullable=True)  # Dedicated column for processed text

    # --- Extracted/Structured Information (Populated after Gemini processing) ---
    extracted_data = Column(JSON, nullable=True)

    # --- Timestamps ---
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )  # Added server_default

    # --- Relationships ---
    company = relationship("Company", back_populates="jobs")
    user = relationship("User", back_populates="jobs")
    cover_letters = relationship(
        "CoverLetter", back_populates="job", cascade="all, delete-orphan"
    )


# --- Company Model ---
class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    contact_info = Column(JSON, nullable=True)
    analytics = Column(JSON, nullable=True)
    status = Column(String, nullable=False, default="pending", index=True)

    # --- Timestamps ---
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # --- Relationships ---
    jobs = relationship("Job", back_populates="company")


# --- CoverLetter Model ---
class CoverLetter(Base):
    __tablename__ = "cover_letters"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True, index=True)
    generation_options = Column(JSON, nullable=True)
    llm_service_used = Column(String, nullable=True)
    sections = Column(JSON, nullable=True)
    text = Column(Text, nullable=True)

    # --- Timestamps ---
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # --- Relationships ---
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    user = relationship("User", back_populates="cover_letters")
    job = relationship("Job", back_populates="cover_letters")
