import logging
from logging.config import dictConfig

# Define logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    # Define formatters
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },

    # Define handlers
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
        },
    },

    # Define loggers
    "loggers": {
        "app": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },

    # Define root logger
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
} 

def setup_logging():
    """Setup logging configuration."""
    dictConfig(LOGGING_CONFIG)