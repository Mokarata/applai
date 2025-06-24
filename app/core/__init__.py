"""
Core module for application configuration and settings.
"""
from .config import settings
from .logging import get_logger

__all__ = [
    "settings",
    "get_logger"
]
