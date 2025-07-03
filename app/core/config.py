import logging
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Core Application Settings"""

    # --- General Settings ---
    PROJECT_NAME: str = "AI Cover Letter Generator"
    API_V1_STR: str = "/api"  # API prefix

    # --- Database Settings ---
    DATABASE_URL: str = "sqlite:///./app.db"  # Default if not found

    # --- Background Settings ---
    BACKGROUND_TASKS: bool = True

    # --- LLM Settings ---
    # ACTIVE_LLM_SERVICE: str = "GEMINI"
    ACTIVE_LLM_SERVICE: str = "OPENAI"
    # ACTIVE_LLM_SERVICE: str = "GROQ"

    # --- Gemini Settings ---
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_MODEL: Optional[str] = "gemini-1.5-flash"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_OUTPUT_TOKENS: int = 1024

    # --- OpenAI Settings ---
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: Optional[str] = "gpt-4o"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 1024

    # --- Groq Settings ---
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL_NAME: Optional[str] = "llama-3.1-8b-instant"
    GROQ_TEMPERATURE: float = 0.7
    GROQ_MAX_TOKENS: int = 1024

    # --- Security Settings ---
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- Cover Letter Generation Settings ---
    DEFAULT_LANGUAGE: str = "German"
    DEFAULT_STYLE: str = "standard"
    DEFAULT_TONE: str = "professional"
    DEFAULT_LENGTH: str = "standard"
    MAX_GENERATION_ATTEMPTS: int = 3
    GENERATION_TIMEOUT: int = 60

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


# Singleton instance to import elsewhere
settings = Settings()


def validate_settings():
    """Validate settings and raise exceptions if invalid."""
    required_settings = [
        "PROJECT_NAME",
        "API_V1_STR",
        "DATABASE_URL",
        "DEFAULT_LANGUAGE",
        "DEFAULT_STYLE",
        "DEFAULT_TONE",
        "MAX_GENERATION_ATTEMPTS",
        "GENERATION_TIMEOUT",
        "ACTIVE_LLM_SERVICE",
        "BACKGROUND_TASKS",
        "JWT_SECRET_KEY",
    ]

    # Check for active LLM service API key
    if settings.ACTIVE_LLM_SERVICE == "GEMINI":
        required_settings.append("GOOGLE_API_KEY")
        required_settings.append("GEMINI_MODEL")
    elif settings.ACTIVE_LLM_SERVICE == "OPENAI":
        required_settings.append("OPENAI_API_KEY")
        required_settings.append("OPENAI_MODEL")
    elif settings.ACTIVE_LLM_SERVICE == "GROQ":
        required_settings.append("GROQ_API_KEY")
        required_settings.append("GROQ_MODEL_NAME")
    else:
        # Invalid active LLM service specified
        raise ValueError(
            f"Invalid active LLM service specified: {settings.ACTIVE_LLM_SERVICE}"
        )

    # Check for required settings
    missing_settings = [
        setting for setting in required_settings if not getattr(settings, setting, None)
    ]
    if missing_settings:
        raise ValueError(f"Missing required settings: {', '.join(missing_settings)}")

    logger.info("Settings validation successful")
