"""DRA Transaction Reconciliation Platform - Main Application.

This module initializes the FastAPI application with all necessary
configurations, middleware, and routes.
"""
import logging
import os

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.database import engine
from core.logging_config import setup_logging
from core.monitoring import init_sentry, configure_structured_logging
from core.rate_limiter import limiter, setup_rate_limiting, RateLimits
from core.scheduler import start_scheduler, shutdown_scheduler
from models import client, user_client, schedule

# Initialize structured logging
configure_structured_logging()

# Initialize logging
setup_logging(
    level="DEBUG" if settings.ENVIRONMENT == "development" else "INFO",
    environment=settings.ENVIRONMENT,
)

# Initialize Sentry for error tracking
sentry_initialized = init_sentry()

logger = logging.getLogger(__name__)

# Parse CORS origins from settings
def parse_cors_origins():
    """Parse CORS origins from environment variable."""
    # Debug: Check environment variables directly
    cors_from_env = os.environ.get('CORS_ORIGINS', 'NOT_SET')
    logger.info(f"CORS_ORIGINS from os.environ: {cors_from_env!r}")
    
    # Check if we should allow all origins (for debugging)
    if getattr(settings, 'CORS_ALLOW_ALL', False):
        logger.warning("CORS_ALLOW_ALL is enabled - allowing all origins (not recommended for production)")
        return ["*"]
    
    # Try to get from settings (pydantic)
    origins_str = getattr(settings, 'CORS_ORIGINS', '')
    logger.info(f"CORS_ORIGINS from pydantic settings: {origins_str!r}")
    
    # Use direct env var if available, otherwise fall back to pydantic settings
    if cors_from_env != 'NOT_SET':
        origins_str = cors_from_env
    
    if origins_str and origins_str != "http://localhost:3000,http://localhost:3001,http://localhost:4000":
        origins = [origin.strip() for origin in origins_str.split(',') if origin.strip()]
        logger.info(f"CORS origins configured: {origins}")
        return origins
    
    # Default origins for development
    logger.warning("Using default CORS origins (localhost only). Set CORS_ORIGINS env var for production.")
    return [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:4000",
    ]

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="E-commerce transaction reconciliation platform for GA4 and backend systems",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
)

# CORS middleware - MUST be added before rate limiting to handle preflight requests
origins = parse_cors_origins()
logger.info(f"Configuring CORS with origins: {origins}")

# Check if we need to allow all origins (for debugging or when env var isn't working)
if origins == ["*"] or os.environ.get('CORS_ALLOW_ALL', '').lower() == 'true':
    logger.warning("Allowing all CORS origins with credentials disabled")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # Must be False when using ["*"]
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=600,
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=600,
    )

# Middleware to handle X-Forwarded-Proto header from Railway
@app.middleware("http")
async def handle_forwarded_proto(request: Request, call_next):
    """Handle X-Forwarded-Proto header for proper HTTPS detection."""
    # Railway sets X-Forwarded-Proto to 'https' when the request comes via HTTPS
    forwarded_proto = request.headers.get('X-Forwarded-Proto')
    if forwarded_proto:
        request.scope['scheme'] = forwarded_proto
    response = await call_next(request)
    return response

# Set up rate limiting
setup_rate_limiting(app)


@app.on_event("startup")
async def startup_event():
    """Application startup handler."""
    logger.info(
        "Starting DRA Platform",
        extra={
            "environment": settings.ENVIRONMENT,
            "version": settings.VERSION,
            "sentry_enabled": sentry_initialized,
        },
    )
    
    # In production, migrations are handled by Alembic, NOT automatically here
    # This prevents accidental schema changes and data loss
    if settings.ENVIRONMENT == "development":
        logger.warning(
            "Development mode: Ensure database migrations are applied. "
            "Run: alembic upgrade head"
        )
    
    # Log configuration status
    logger.info(
        "Configuration status",
        extra={
            "email_enabled": bool(getattr(settings, 'RESEND_API_KEY', None)),
            "redis_enabled": bool(getattr(settings, 'REDIS_URL', None)),
            "sentry_enabled": sentry_initialized,
        }
    )
    
    # Start the job scheduler
    try:
        await start_scheduler()
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}", exc_info=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown handler."""
    logger.info("Shutting down DRA Platform")
    shutdown_scheduler()
    await engine.dispose()


@app.get("/", tags=["root"])
@limiter.limit(RateLimits.HEALTH)
def read_root(request: Request):
    """Root endpoint returning basic API info."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "operational",
        "features": {
            "sentry": sentry_initialized,
            "email": bool(getattr(settings, 'RESEND_API_KEY', None)),
            "redis": bool(getattr(settings, 'REDIS_URL', None)),
        }
    }


@app.get("/health", tags=["health"], status_code=status.HTTP_200_OK)
@limiter.limit(RateLimits.HEALTH)
async def health_check(request: Request):
    """Health check endpoint for monitoring and load balancers.
    
    Returns:
        dict: Health status including database connectivity
    """
    health_status = {
        "status": "healthy",
        "checks": {
            "api": "pass",
            "database": "unknown",
        },
    }
    
    try:
        # Test database connection
        from sqlalchemy import text
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            await result.scalar()
        health_status["checks"]["database"] = "pass"
        logger.debug("Health check passed")
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = "fail"
        logger.error("Health check failed: database error", exc_info=e)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status,
        )
    
    return health_status


# Import and include routers
from api.v1.endpoints import clients, jobs, connectors, admin, users, schedules, webhooks, exports

app.include_router(clients.router, prefix="/api/v1/clients", tags=["clients"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(
    connectors.router,
    prefix="/api/v1/clients/{client_id}/connectors",
    tags=["connectors"],
)
app.include_router(
    connectors.single_router,
    prefix="/api/v1/connectors",
    tags=["connectors"],
)
app.include_router(
    webhooks.router,
    prefix="/api/v1/clients/{client_id}/webhooks",
    tags=["webhooks"],
)
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(schedules.router, prefix="/api/v1", tags=["schedules"])
app.include_router(exports.router, prefix="/api/v1", tags=["exports"])

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.ENVIRONMENT == "development",
        log_config=None,  # Use our custom logging
    )
