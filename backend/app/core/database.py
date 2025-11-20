"""Database session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from functools import lru_cache
import logging

from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Log DATABASE_URL (masked for security)
db_url_masked = settings.DATABASE_URL
if "@" in db_url_masked:
    # Mask password in URL
    parts = db_url_masked.split("@")
    if len(parts) == 2:
        user_pass = parts[0].split("://")[1] if "://" in parts[0] else parts[0]
        if ":" in user_pass:
            user = user_pass.split(":")[0]
            db_url_masked = f"{parts[0].split('://')[0]}://{user}:***@{parts[1]}"
        else:
            db_url_masked = f"{parts[0]}:***@{parts[1]}"
logger.info(f"Database URL (masked): {db_url_masked}")

try:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        echo=settings.DEBUG,
    )
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    logger.error(f"DATABASE_URL length: {len(settings.DATABASE_URL)}")
    logger.error(f"DATABASE_URL starts with: {settings.DATABASE_URL[:50]}...")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@lru_cache()
def get_engine():
    """Get cached database engine."""
    return engine

