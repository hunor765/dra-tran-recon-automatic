from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration.
    
    All settings can be overridden via environment variables.
    """
    # Application
    PROJECT_NAME: str = "DRA Platform API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "production"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/dra_platform"
    
    # Security
    ENCRYPTION_KEY: str = ""  # Required - 32-byte base64-encoded Fernet key
    
    # Supabase Auth (required for JWT validation)
    SUPABASE_URL: str = ""  # e.g., https://your-project.supabase.co
    SUPABASE_ANON_KEY: str = ""  # Your Supabase anon/public key
    SUPABASE_JWT_SECRET: str = ""  # JWT secret for local validation (optional but recommended)
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_TO_FILE: bool = False
    LOG_FILE_PATH: str = "/var/log/dra-platform/app.log"
    
    # Redis Cache
    REDIS_URL: str = ""  # e.g., redis://localhost:6379/0
    CACHE_TTL_SECONDS: int = 300  # Default 5 minutes
    CACHE_ENABLED: bool = True
    
    # Webhooks
    WEBHOOK_SECRET: str = ""  # Secret for signing webhook payloads
    WEBHOOK_TIMEOUT_SECONDS: int = 30
    WEBHOOK_MAX_RETRIES: int = 3
    
    # Email Service (Resend)
    RESEND_API_KEY: str = ""  # Resend API key for email delivery
    FROM_EMAIL: str = "noreply@datarevolt.agency"  # Sender email address
    FROM_NAME: str = "DRA Reconciliation Platform"  # Sender name
    
    # Frontend URL (for links in emails)
    FRONTEND_URL: str = "http://localhost:3000"  # Production: https://app.yourdomain.com
    
    # Monitoring (Sentry)
    SENTRY_DSN: str = ""  # Sentry DSN for error tracking
    VERSION: str = "2.0.0"  # App version for Sentry releases
    
    # Data Retention
    RETENTION_JOB_RESULTS_DAYS: int = 90
    RETENTION_JOB_LOGS_DAYS: int = 30
    RETENTION_FAILED_JOBS_DAYS: int = 180
    RETENTION_AUDIT_LOGS_DAYS: int = 365
    RETENTION_OLD_JOBS_DAYS: int = 365
    
    # CORS Origins (comma-separated list)
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:4000"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
