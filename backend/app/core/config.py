"""Application configuration from environment variables."""
from pydantic_settings import BaseSettings
from functools import lru_cache


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

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    # Convert CORS_ORIGINS string to list
    if isinstance(settings.CORS_ORIGINS, str):
        settings.CORS_ORIGINS = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
    return settings

