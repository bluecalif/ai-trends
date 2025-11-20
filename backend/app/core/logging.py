"""Logging configuration for development and production environments.

This module provides structured logging configuration:
- Development: Console output with readable format
- Production: JSON format for log aggregation services
"""

import json
import logging
import sys
from typing import Any, Dict

from backend.app.core.config import get_settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging in production."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging() -> None:
    """Configure logging based on environment.

    Development (DEBUG=True): Console output with readable format
    Production (DEBUG=False): JSON format for log aggregation
    """
    settings = get_settings()

    # Get log format from environment or use default
    # Note: LOG_FORMAT and LOG_LEVEL are not in Settings yet, so we use getattr with default
    log_format = getattr(settings, "LOG_FORMAT", None)
    if log_format is None:
        # Default: use JSON in production, console in development
        log_format = "json" if not settings.DEBUG else "console"

    # Get log level from environment or use default
    log_level_str = getattr(settings, "LOG_LEVEL", None)
    if log_level_str is None:
        log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    else:
        log_level = getattr(logging, str(log_level_str).upper(), logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Set formatter based on environment
    if log_format == "json":
        formatter = JSONFormatter()
    else:
        # Console format for development
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Set levels for third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)

