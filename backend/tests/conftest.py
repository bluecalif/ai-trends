"""Pytest configuration and fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.app.core.database import get_db
from backend.app.models.base import Base
from backend.app.main import app
from fastapi.testclient import TestClient
from backend.app.core.config import get_settings

# Clear cache to ensure fresh settings load
get_settings.cache_clear()
settings = get_settings()

# Use actual database URL for tests
TEST_DATABASE_URL = settings.DATABASE_URL


@pytest.fixture(scope="function")
def test_db():
    """Test database session."""
    from backend.app.models import (
        Source,
        Item,
        Person,
        PersonTimeline,
        WatchRule,
        Bookmark,
        Entity,
    )
    
    # Create test database engine
    engine = create_engine(
        TEST_DATABASE_URL,
        pool_pre_ping=True,
        echo=False,
    )
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    except Exception:
        db.rollback()  # Rollback on failure
        raise
    finally:
        # Clean up test data (delete in reverse dependency order)
        from backend.app.models.item_entity import item_entities
        from sqlalchemy import delete
        
        try:
            # Delete relationships first
            db.execute(delete(item_entities))
            # Delete main tables
            db.query(Bookmark).delete()
            db.query(PersonTimeline).delete()
            db.query(WatchRule).delete()
            db.query(Item).delete()
            db.query(Entity).delete()
            db.query(Source).delete()
            db.query(Person).delete()
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()
            engine.dispose()


@pytest.fixture
def client(test_db):
    """Test client with database override."""
    app.dependency_overrides[get_db] = lambda: test_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

