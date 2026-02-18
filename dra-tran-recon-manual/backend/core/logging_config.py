"""Structured logging configuration for the DRA Platform.

Provides JSON-formatted logs suitable for production log aggregation.
"""
import logging
import logging.config
import json
import sys
from typing import Any, Dict
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "source": {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            },
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "extra"):
            log_data["extra"] = record.extra
        
        # Add job_id if present (for job tracking)
        if hasattr(record, "job_id"):
            log_data["job_id"] = record.job_id
        
        # Add client_id if present (for multi-tenant tracking)
        if hasattr(record, "client_id"):
            log_data["client_id"] = record.client_id
        
        # Add user_id if present
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
            
        return json.dumps(log_data, default=str)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for development console output."""
    
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
        "RESET": "\033[0m",       # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]
        
        formatted = f"{color}[{record.levelname}]{reset} {record.name}: {record.getMessage()}"
        
        if record.exc_info:
            formatted += "\n" + self.formatException(record.exc_info)
            
        return formatted


def setup_logging(
    level: str = "INFO",
    environment: str = "production",
    log_to_file: bool = False,
    log_file_path: str = "/var/log/dra-platform/app.log"
) -> None:
    """Configure logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        environment: 'development' or 'production'
        log_to_file: Whether to also log to file
        log_file_path: Path for log file (if log_to_file is True)
    """
    handlers: Dict[str, Any] = {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "level": level,
        }
    }
    
    # Use colored formatter for development, JSON for production
    if environment == "development":
        handlers["console"]["formatter"] = "colored"
    else:
        handlers["console"]["formatter"] = "json"
    
    # Add file handler if requested
    if log_to_file:
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": log_file_path,
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,
            "level": level,
            "formatter": "json",
        }
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JSONFormatter,
            },
            "colored": {
                "()": ColoredFormatter,
            },
        },
        "handlers": handlers,
        "loggers": {
            "": {  # Root logger
                "handlers": list(handlers.keys()),
                "level": level,
                "propagate": False,
            },
            # Reduce noise from third-party libraries
            "sqlalchemy.engine": {
                "handlers": list(handlers.keys()),
                "level": "WARNING",
                "propagate": False,
            },
            "apscheduler": {
                "handlers": list(handlers.keys()),
                "level": "WARNING",
                "propagate": False,
            },
        },
    }
    
    logging.config.dictConfig(config)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured",
        extra={"extra": {"environment": environment, "level": level, "handlers": list(handlers.keys())}}
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.
    
    Args:
        name: The logger name (typically __name__)
        
    Returns:
        logging.Logger: Configured logger
    """
    return logging.getLogger(name)
