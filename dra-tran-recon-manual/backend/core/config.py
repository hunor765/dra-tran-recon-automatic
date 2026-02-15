from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "DRA Platform API"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/dra_platform"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "production"
    ENCRYPTION_KEY: str = ""

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
