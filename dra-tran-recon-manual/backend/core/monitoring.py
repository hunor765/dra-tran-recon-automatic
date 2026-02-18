"""Monitoring and error tracking configuration.

Integrates with Sentry for error tracking and provides utilities for
structured logging and performance monitoring.
"""
import logging
from typing import Optional, Any, Dict
from contextvars import ContextVar

from core.config import settings

# Context variable for request correlation ID
request_id_var: ContextVar[str] = ContextVar('request_id', default='')

# Sentry SDK handle (initialized lazily)
_sentry_initialized = False


def init_sentry() -> bool:
    """Initialize Sentry SDK for error tracking.
    
    Returns:
        True if Sentry was initialized successfully
    """
    global _sentry_initialized
    
    if _sentry_initialized:
        return True
    
    dsn = getattr(settings, 'SENTRY_DSN', None)
    if not dsn:
        logging.getLogger(__name__).info(
            "Sentry not configured. Set SENTRY_DSN to enable error tracking."
        )
        return False
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        
        sentry_logging = LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR
        )
        
        sentry_sdk.init(
            dsn=dsn,
            environment=getattr(settings, 'ENVIRONMENT', 'development'),
            release=getattr(settings, 'VERSION', 'unknown'),
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
                sentry_logging,
            ],
            traces_sample_rate=0.1,  # Sample 10% of transactions for performance monitoring
            profiles_sample_rate=0.1,  # Sample 10% of profiles
            before_send=before_send_event,
        )
        
        _sentry_initialized = True
        logging.getLogger(__name__).info("Sentry initialized successfully")
        return True
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to initialize Sentry: {e}")
        return False


def before_send_event(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Filter events before sending to Sentry.
    
    Args:
        event: The event dictionary
        hint: Additional context
        
    Returns:
        Modified event or None to drop the event
    """
    # Add request ID to event if available
    request_id = request_id_var.get()
    if request_id:
        if 'extra' not in event:
            event['extra'] = {}
        event['extra']['request_id'] = request_id
    
    # Don't send events in development (too noisy)
    if getattr(settings, 'ENVIRONMENT', 'development') == 'development':
        # Still log it locally
        logging.getLogger(__name__).debug(f"Sentry event (dev mode): {event.get('message', 'no message')}")
        return None
    
    return event


def capture_exception(error: Exception, extra: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Capture an exception in Sentry.
    
    Args:
        error: The exception to capture
        extra: Additional context data
        
    Returns:
        Event ID if captured, None otherwise
    """
    if not _sentry_initialized:
        # Log locally if Sentry not available
        logging.getLogger(__name__).error(
            f"Exception (Sentry not configured): {error}",
            extra=extra,
            exc_info=error
        )
        return None
    
    try:
        import sentry_sdk
        
        with sentry_sdk.push_scope() as scope:
            # Add extra context
            if extra:
                for key, value in extra.items():
                    scope.set_extra(key, value)
            
            # Add request ID
            request_id = request_id_var.get()
            if request_id:
                scope.set_tag('request_id', request_id)
            
            event_id = sentry_sdk.capture_exception(error)
            return event_id
            
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to capture exception in Sentry: {e}")
        return None


def capture_message(message: str, level: str = 'info', extra: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Capture a message in Sentry.
    
    Args:
        message: The message to capture
        level: Log level ('debug', 'info', 'warning', 'error', 'fatal')
        extra: Additional context data
        
    Returns:
        Event ID if captured, None otherwise
    """
    if not _sentry_initialized:
        logging.getLogger(__name__).log(
            getattr(logging, level.upper(), logging.INFO),
            f"Message (Sentry not configured): {message}"
        )
        return None
    
    try:
        import sentry_sdk
        
        with sentry_sdk.push_scope() as scope:
            if extra:
                for key, value in extra.items():
                    scope.set_extra(key, value)
            
            event_id = sentry_sdk.capture_message(message, level=level)
            return event_id
            
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to capture message in Sentry: {e}")
        return None


def set_user_context(user_id: str, email: Optional[str] = None, **kwargs) -> None:
    """Set user context for Sentry events.
    
    Args:
        user_id: User identifier
        email: User email (optional)
        **kwargs: Additional user attributes
    """
    if not _sentry_initialized:
        return
    
    try:
        import sentry_sdk
        
        sentry_sdk.set_user({
            'id': user_id,
            'email': email,
            **kwargs
        })
    except Exception:
        pass


def clear_user_context() -> None:
    """Clear user context from Sentry."""
    if not _sentry_initialized:
        return
    
    try:
        import sentry_sdk
        sentry_sdk.set_user(None)
    except Exception:
        pass


class PerformanceMonitor:
    """Context manager for monitoring performance of operations."""
    
    def __init__(self, operation: str, tags: Optional[Dict[str, str]] = None):
        self.operation = operation
        self.tags = tags or {}
        self.start_time: Optional[float] = None
        self.span = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        
        if _sentry_initialized:
            try:
                import sentry_sdk
                self.span = sentry_sdk.start_span(op=self.operation)
                for key, value in self.tags.items():
                    self.span.set_tag(key, value)
            except Exception:
                pass
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        duration = time.time() - self.start_time if self.start_time else 0
        
        if self.span:
            try:
                self.span.finish()
            except Exception:
                pass
        
        # Log slow operations
        if duration > 5:  # 5 seconds
            logging.getLogger(__name__).warning(
                f"Slow operation detected: {self.operation} took {duration:.2f}s",
                extra={
                    'operation': self.operation,
                    'duration': duration,
                    'tags': self.tags
                }
            )


def configure_structured_logging() -> None:
    """Configure structured JSON logging for production."""
    import sys
    import json
    import logging
    
    class JSONFormatter(logging.Formatter):
        """JSON log formatter for structured logging."""
        
        def format(self, record: logging.LogRecord) -> str:
            log_data = {
                'timestamp': self.formatTime(record),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
            }
            
            # Add request ID if available
            request_id = request_id_var.get()
            if request_id:
                log_data['request_id'] = request_id
            
            # Add extra fields
            if hasattr(record, 'extra'):
                log_data.update(record.extra)
            
            # Add exception info if present
            if record.exc_info:
                log_data['exception'] = self.formatException(record.exc_info)
            
            return json.dumps(log_data)
    
    # Configure root logger
    root_logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    
    # Use JSON format in production, simple format in development
    if getattr(settings, 'ENVIRONMENT', 'development') == 'production':
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
    
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(settings, 'LOG_LEVEL', 'INFO'))


# Initialize on module load
if getattr(settings, 'SENTRY_DSN', None):
    init_sentry()
