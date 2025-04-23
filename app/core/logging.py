import os
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

# Create log directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Configure different log files
ERROR_LOG = LOG_DIR / "error.log"
INFO_LOG = LOG_DIR / "info.log"
DEBUG_LOG = LOG_DIR / "debug.log"

class CozyFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }
    LEVEL_EMOJI = {
        logging.DEBUG: "🔵",
        logging.INFO: "🟢",
        logging.WARNING: "🟡",
        logging.ERROR: "🔴",
        logging.CRITICAL: "❗",
    }
    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, "")
        emoji = self.LEVEL_EMOJI.get(record.levelno, "")
        level = f"{color}{record.levelname:<7}{Style.RESET_ALL}"
        time = self.formatTime(record, "%H:%M:%S")
        module = f"{record.name}"
        msg = f"{emoji} {level} [{time}] [{module}] {record.getMessage()}"
        return msg

# Standard file formatter (no color/emoji)
FILE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def get_logger(name):
    """
    Get a logger with the specified name.
    
    Args:
        name: Usually __name__ of the calling module
        
    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)

    # Set the logging level
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create handlers for different log levels
    
    # Console handler (INFO level) with CozyFormatter
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(CozyFormatter())
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        ERROR_LOG, maxBytes=10485760, backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(FILE_FORMAT))
    
    # Info file handler
    info_handler = logging.handlers.RotatingFileHandler(
        INFO_LOG, maxBytes=10485760, backupCount=5
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(logging.Formatter(FILE_FORMAT))
    
    # Debug file handler (all messages)
    debug_handler = logging.handlers.RotatingFileHandler(
        DEBUG_LOG, maxBytes=10485760, backupCount=5
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(logging.Formatter(FILE_FORMAT))
    
    # Add all handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(error_handler)
    logger.addHandler(info_handler)
    logger.addHandler(debug_handler)
    
    return logger
