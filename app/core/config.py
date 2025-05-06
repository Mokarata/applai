import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Core Application Settings"""
    PROJECT_NAME: str = "AI Cover Letter Generator"
    API_V1_STR: str = "/api" # API prefix
    
    # --- Database Settings ---
    # pydantic-settings will automatically look for DATABASE_URL
    DATABASE_URL: str = "sqlite:///./app.db" # Default if not found

    # --- Gemini Settings ---
    # pydantic-settings will automatically look for GOOGLE_API_KEY
    GOOGLE_API_KEY: Optional[str] = None

    # --- OpenAI Settings ---
    # pydantic-settings will automatically look for OPENAI_API_KEY
    OPENAI_API_KEY: Optional[str] = None

    # --- Security Settings ---
    # pydantic-settings will automatically look for SECRET_KEY
    SECRET_KEY: Optional[str] = None
    # ALGORITHM: str = "HS256"
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    

    class Config:
        # If you use a .env file, this ensures variables are loaded
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Allow case-insensitive environment variable access
        case_sensitive = True # Ensure env var names match field names exactly
        extra = 'ignore' # Ignore extra fields in the .env file

# Singleton instance to import elsewhere
settings = Settings()

# Function to easily get settings (Optional, but can be usefull)
def get_settings() -> Settings:
    return settings