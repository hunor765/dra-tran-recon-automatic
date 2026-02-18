"""Rate limiting configuration for API endpoints.

Uses SlowAPI for rate limiting with Redis backend in production
and memory backend in development.
"""
import logging
from typing import Optional

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, FastAPI

from core.config import settings

logger = logging.getLogger(__name__)


def get_limiter_key(request: Request) -> str:
    """Get the rate limit key for a request.
    
    Uses user ID from auth if available, otherwise falls back to IP address.
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: The rate limit key
    """
    # Try to get user ID from auth
    user = getattr(request.state, "user", None)
    if user and isinstance(user, dict) and "id" in user:
        return f"user:{user['id']}"
    
    # Fall back to IP address
    return get_remote_address(request)


# Initialize limiter
# In production, use Redis storage for distributed rate limiting
# In development, use memory storage
storage_uri = None  # Default to memory storage
if settings.ENVIRONMENT == "production":
    # Check for Redis URL (could be from environment)
    redis_url = getattr(settings, "REDIS_URL", None)
    if redis_url:
        storage_uri = redis_url
        logger.info("Using Redis for rate limiting storage")

limiter = Limiter(
    key_func=get_limiter_key,
    storage_uri=storage_uri,
    default_limits=["100/minute"],  # Global default
    strategy="fixed-window",  # Use fixed window for simplicity
)


def setup_rate_limiting(app: FastAPI) -> None:
    """Set up rate limiting on the FastAPI application.
    
    Args:
        app: The FastAPI application instance
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    logger.info("Rate limiting configured")


# Rate limit configurations for different endpoint types
class RateLimits:
    """Predefined rate limits for different endpoint categories."""
    
    # Public/health endpoints - generous limits
    HEALTH = ["60/minute"]
    
    # Read operations - standard limits
    LIST = ["100/minute"]
    GET = ["100/minute"]
    
    # Write operations - stricter limits
    CREATE = ["30/minute"]
    UPDATE = ["30/minute"]
    DELETE = ["10/minute"]
    
    # Expensive operations - very strict limits
    JOB_RUN = ["10/minute"]  # Running reconciliation jobs
    CONNECTOR_TEST = ["20/minute"]  # Testing connector configurations
    
    # Admin operations - moderate limits (admins should have higher limits in general)
    ADMIN_READ = ["200/minute"]
    ADMIN_WRITE = ["50/minute"]


def get_user_tier_limits(
    request: Request,
    base_limits: list,
    authenticated_limits: Optional[list] = None,
    admin_limits: Optional[list] = None
) -> list:
    """Get rate limits based on user authentication tier.
    
    Args:
        request: FastAPI request
        base_limits: Limits for unauthenticated users
        authenticated_limits: Limits for authenticated users (defaults to base * 2)
        admin_limits: Limits for admin users (defaults to authenticated * 2)
        
    Returns:
        list: Rate limit strings
    """
    user = getattr(request.state, "user", None)
    
    if not user:
        return base_limits
    
    role = user.get("role", "")
    
    if role == "admin" and admin_limits:
        return admin_limits
    
    if authenticated_limits:
        return authenticated_limits
    
    return base_limits
