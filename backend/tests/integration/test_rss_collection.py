"""Integration tests for RSS collection service."""
import pytest
from datetime import datetime, timezone
import uuid

from backend.app.services.rss_collector import RSSCollector
from backend.app.models.source import Source
from backend.app.models.item import Item


def get_unique_string(prefix: str = "") -> str:
    """Generate unique string for test data."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestRSSCollectorIntegration:
    """Integration tests for RSS collector with database."""
    
    def test_normalize_item_db_compatibility(self, test_db):
        """Test normalize_item output is compatible with Item model."""
        unique_id = get_unique_string()
        
        # Create source in DB
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml"
        )
        test_db.add(source)
        test_db.flush()
        
        # Test normalize_item
        link_url = f"https://example.com/article_{unique_id}"
        entry = {
            "title": "  Test Article  ",
            "link": f"  {link_url}  ",
            "published_at": datetime.now(timezone.utc),
            "author": "  Test Author  ",
            "description": "Test description" * 100  # Long description
        }
        
        collector = RSSCollector(test_db)
        normalized = collector.normalize_item(entry, source)
        
        # Verify normalized data can create Item model
        item = Item(**normalized)
        test_db.add(item)
        test_db.flush()
        
        # Verify all fields are correctly set
        assert item.source_id == source.id
        assert item.title == "Test Article"
        assert item.link == link_url  # Should be normalized (trimmed)
        assert item.author == "Test Author"
        assert len(item.summary_short) == 500  # Truncated
        assert item.published_at == entry["published_at"]
        assert item.id is not None  # DB generated ID
    
    def test_collect_source_full_flow(self, test_db):
        """Test full RSS collection flow with database."""
        unique_id = get_unique_string()
        
        # Create source
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml",
            is_active=True
        )
        test_db.add(source)
        test_db.commit()
        
        # Mock feedparser for integration test
        from unittest.mock import patch, MagicMock
        
        # Create a simple object-like mock that doesn't leak MagicMock
        class MockEntry:
            def __init__(self, title, link, description):
                self.title = title
                self.link = link
                self.description = description
                self.published_parsed = None
                self.media_thumbnail = None
                self.enclosures = None
                self.media_content = None
            
            def get(self, key, default=""):
                return getattr(self, key, default)
        
        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_entry = MockEntry(
            title=f"Test Article {unique_id}",
            link=f"https://example.com/article_{unique_id}",
            description="Test description"
        )
        mock_feed.entries = [mock_entry]
        
        with patch('backend.app.services.rss_collector.feedparser.parse', return_value=mock_feed):
            collector = RSSCollector(test_db)
            count = collector.collect_source(source)
            
            # Verify item was created
            assert count == 1
            
            # Verify item in DB
            item = test_db.query(Item).filter(Item.source_id == source.id).first()
            assert item is not None
            assert item.title == f"Test Article {unique_id}"
            assert item.link == f"https://example.com/article_{unique_id}"
            assert item.source_id == source.id
    
    def test_collect_source_duplicate_handling(self, test_db):
        """Test that duplicate items are not collected twice."""
        unique_id = get_unique_string()
        
        # Create source
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml",
            is_active=True
        )
        test_db.add(source)
        test_db.flush()
        
        # Create existing item
        existing_item = Item(
            source_id=source.id,
            title="Existing Article",
            link=f"https://example.com/article_{unique_id}",
            published_at=datetime.now(timezone.utc)
        )
        test_db.add(existing_item)
        test_db.commit()
        
        # Mock feedparser with same link
        from unittest.mock import patch, MagicMock
        
        # Create a simple object-like mock that doesn't leak MagicMock
        class MockEntry:
            def __init__(self, title, link, description):
                self.title = title
                self.link = link
                self.description = description
                self.published_parsed = None
                self.media_thumbnail = None
                self.enclosures = None
                self.media_content = None
            
            def get(self, key, default=""):
                return getattr(self, key, default)
        
        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_entry = MockEntry(
            title="New Article",
            link=f"https://example.com/article_{unique_id}",  # Same link
            description="New description"
        )
        mock_feed.entries = [mock_entry]
        
        with patch('backend.app.services.rss_collector.feedparser.parse', return_value=mock_feed):
            collector = RSSCollector(test_db)
            count = collector.collect_source(source)
            
            # Should skip duplicate
            assert count == 0
            
            # Verify only one item exists
            items = test_db.query(Item).filter(Item.source_id == source.id).all()
            assert len(items) == 1
            assert items[0].title == "Existing Article"  # Original item

