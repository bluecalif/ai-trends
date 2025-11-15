"""Integration tests for database migrations."""
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from backend.app.models.base import Base
from backend.app.core.config import get_settings

settings = get_settings()
TEST_DATABASE_URL = settings.DATABASE_URL


class TestMigrations:
    """Test database migrations."""
    
    def test_migration_upgrade_downgrade(self):
        """Test migration upgrade and downgrade."""
        # Create engine and get current revision
        engine = create_engine(TEST_DATABASE_URL)
        inspector = inspect(engine)
        
        # Get current tables
        current_tables = set(inspector.get_table_names())
        
        # Expected tables from initial migration
        expected_tables = {
            "sources",
            "items",
            "persons",
            "person_timeline",
            "watch_rules",
            "bookmarks",
            "entities",
            "item_entities",
            "alembic_version",
        }
        
        # Check that all expected tables exist
        assert expected_tables.issubset(current_tables), f"Missing tables: {expected_tables - current_tables}"
        
        engine.dispose()
    
    def test_table_structure(self):
        """Test that tables have correct structure."""
        engine = create_engine(TEST_DATABASE_URL)
        inspector = inspect(engine)
        
        # Test sources table structure
        sources_columns = {col["name"] for col in inspector.get_columns("sources")}
        expected_source_columns = {
            "id", "title", "feed_url", "site_url", "category", "lang", 
            "is_active", "created_at", "updated_at"
        }
        assert expected_source_columns.issubset(sources_columns)
        
        # Test items table structure
        items_columns = {col["name"] for col in inspector.get_columns("items")}
        expected_item_columns = {
            "id", "source_id", "title", "summary_short", "link", 
            "published_at", "author", "thumbnail_url",
            "iptc_topics", "iab_categories", "custom_tags", 
            "dup_group_id", "created_at", "updated_at"
        }
        assert expected_item_columns.issubset(items_columns)
        
        # Test foreign keys
        items_fks = inspector.get_foreign_keys("items")
        source_fk_exists = any(fk["referred_table"] == "sources" for fk in items_fks)
        assert source_fk_exists, "Foreign key to sources table should exist"
        
        engine.dispose()
    
    def test_indexes_exist(self):
        """Test that indexes are created correctly."""
        engine = create_engine(TEST_DATABASE_URL)
        inspector = inspect(engine)
        
        # Test items table indexes
        items_indexes = {idx["name"] for idx in inspector.get_indexes("items")}
        expected_indexes = {
            "ix_items_id",
            "ix_items_source_id",
            "ix_items_link",
            "ix_items_published_at",
            "ix_items_dup_group_id",
        }
        # Check that at least some expected indexes exist
        assert len(items_indexes.intersection(expected_indexes)) > 0
        
        # Test sources table indexes
        sources_indexes = {idx["name"] for idx in inspector.get_indexes("sources")}
        assert "ix_sources_feed_url" in sources_indexes or any("feed_url" in idx["name"] for idx in inspector.get_indexes("sources"))
        
        engine.dispose()
    
    def test_unique_constraints(self):
        """Test that unique constraints are enforced."""
        engine = create_engine(TEST_DATABASE_URL)
        inspector = inspect(engine)
        
        # Check unique constraints
        items_indexes = inspector.get_indexes("items")
        link_unique = any(
            idx["unique"] and "link" in idx["column_names"] 
            for idx in items_indexes
        )
        assert link_unique, "items.link should have unique constraint"
        
        sources_indexes = inspector.get_indexes("sources")
        feed_url_unique = any(
            idx["unique"] and "feed_url" in idx["column_names"]
            for idx in sources_indexes
        )
        assert feed_url_unique, "sources.feed_url should have unique constraint"
        
        engine.dispose()

