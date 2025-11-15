"""Application configuration from environment variables."""
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database (Supabase PostgreSQL)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ai_trend"
    
    # Supabase Configuration
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # OpenAI API
    OPENAI_API_KEY: str = ""

    # Application
    APP_NAME: str = "AI Trend Monitor"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # CORS (comma-separated string, will be split into list)
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    # RSS Collection
    RSS_COLLECTION_INTERVAL_MINUTES: int = 20

    # Grouping reference date (UTC midnight) in YYYY-MM-DD, empty means use today's UTC date
    REF_DATE: str = ""

    class Config:
        # Find .env file relative to project root
        # This file is at backend/app/core/config.py, so go up 2 levels to project root
        _project_root = Path(__file__).parent.parent.parent.parent
        _env_file = _project_root / "backend" / ".env"
        env_file = str(_env_file) if _env_file.exists() else ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    # Convert CORS_ORIGINS string to list
    if isinstance(settings.CORS_ORIGINS, str):
        settings.CORS_ORIGINS = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
    return settings

