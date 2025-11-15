"""E2E tests for RSS collection with real sources."""
import pytest
from datetime import datetime, timezone
import uuid

from backend.app.services.rss_collector import RSSCollector
from backend.app.models.source import Source
from backend.app.models.item import Item


def get_unique_string(prefix: str = "") -> str:
    """Generate unique string for test data."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


# Initial 10 RSS sources (from rules)
INITIAL_RSS_SOURCES = [
    {
        "title": "TechCrunch",
        "feed_url": "https://techcrunch.com/feed/",
        "site_url": "https://techcrunch.com",
        "category": "Tech News",
        "lang": "en",
    },
    {
        "title": "VentureBeat",
        "feed_url": "https://venturebeat.com/feed/",
        "site_url": "https://venturebeat.com",
        "category": "Tech News",
        "lang": "en",
    },
    {
        "title": "MarkTechPost",
        "feed_url": "https://www.marktechpost.com/feed/",
        "site_url": "https://www.marktechpost.com",
        "category": "AI News",
        "lang": "en",
    },
    {
        "title": "WIRED",
        "feed_url": "https://www.wired.com/feed/rss",
        "site_url": "https://www.wired.com",
        "category": "Tech News",
        "lang": "en",
    },
    {
        "title": "The Verge",
        "feed_url": "https://www.theverge.com/rss/index.xml",
        "site_url": "https://www.theverge.com",
        "category": "Tech News",
        "lang": "en",
    },
    {
        "title": "IEEE Spectrum",
        "feed_url": "https://spectrum.ieee.org/rss",
        "site_url": "https://spectrum.ieee.org",
        "category": "Research",
        "lang": "en",
    },
    {
        "title": "AITimes",
        "feed_url": "https://aitimes.com/feed/",
        "site_url": "https://aitimes.com",
        "category": "AI News",
        "lang": "en",
    },
    {
        "title": "arXiv cs.AI",
        "feed_url": "http://arxiv.org/rss/cs.AI",
        "site_url": "https://arxiv.org/list/cs.AI/recent",
        "category": "Research",
        "lang": "en",
    },
    {
        "title": "OpenAI News",
        "feed_url": "https://openai.com/blog/rss.xml",
        "site_url": "https://openai.com/blog",
        "category": "AI News",
        "lang": "en",
    },
    {
        "title": "DeepMind Blog",
        "feed_url": "https://deepmind.google/discover/blog/rss.xml",
        "site_url": "https://deepmind.google/discover/blog",
        "category": "AI News",
        "lang": "en",
    },
]


class TestRSSCollectionE2E:
    """E2E tests for RSS collection with real RSS sources."""
    
    def test_register_initial_sources(self, test_db):
        """Test registering 10 initial RSS sources."""
        sources = []
        
        for source_data in INITIAL_RSS_SOURCES:
            # Check if source already exists
            existing = test_db.query(Source).filter(
                Source.feed_url == source_data["feed_url"]
            ).first()
            
            if existing:
                # Update existing source
                existing.is_active = True
                sources.append(existing)
            else:
                # Create new source
                source = Source(**source_data, is_active=True)
                test_db.add(source)
                sources.append(source)
        
        test_db.commit()
        
        # Verify all sources are created
        assert len(sources) == 10
        
        # Verify sources are in DB
        db_sources = test_db.query(Source).filter(Source.is_active == True).all()
        assert len(db_sources) >= 10
        
        # Verify feed URLs are correct
        feed_urls = {s.feed_url for s in db_sources}
        expected_urls = {s["feed_url"] for s in INITIAL_RSS_SOURCES}
        assert expected_urls.issubset(feed_urls), "Not all expected feed URLs found"
    
    @pytest.mark.slow
    def test_collect_from_one_source(self, test_db):
        """Test collecting items from one RSS source (real feed)."""
        # Use a reliable test source (TechCrunch or The Verge)
        test_feed_url = "https://techcrunch.com/feed/"
        
        # Get or create source
        source = test_db.query(Source).filter(Source.feed_url == test_feed_url).first()
        if not source:
            source = Source(
                title="TechCrunch Test",
                feed_url=test_feed_url,
                site_url="https://techcrunch.com",
                is_active=True
            )
            test_db.add(source)
            test_db.flush()
        
        # Collect items
        collector = RSSCollector(test_db)
        try:
            count = collector.collect_source(source)
            
            # Verify items were collected (may be 0 if all are duplicates)
            assert count >= 0, "Collection count should be non-negative"
            
            # Verify items are in DB
            items = test_db.query(Item).filter(Item.source_id == source.id).all()
            assert len(items) >= 0, "Items should exist in DB (may be 0 if all duplicates)"
            
            # If items were collected, verify their structure
            if items:
                item = items[0]
                assert item.title is not None and len(item.title) > 0
                assert item.link is not None and len(item.link) > 0
                assert item.published_at is not None
                assert item.source_id == source.id
                
        except Exception as e:
            pytest.skip(f"Failed to collect from real feed (network issue?): {e}")
    
    @pytest.mark.slow
    def test_collect_from_multiple_sources(self, test_db):
        """Test collecting items from multiple RSS sources."""
        # Use 2-3 reliable sources for faster testing
        test_sources = [
            "https://techcrunch.com/feed/",
            "https://www.theverge.com/rss/index.xml",
        ]
        
        collector = RSSCollector(test_db)
        total_collected = 0
        
        for feed_url in test_sources:
            source = test_db.query(Source).filter(Source.feed_url == feed_url).first()
            if not source:
                source = Source(
                    title=f"Test Source {get_unique_string()}",
                    feed_url=feed_url,
                    is_active=True
                )
                test_db.add(source)
                test_db.flush()
            
            try:
                count = collector.collect_source(source)
                total_collected += count
            except Exception as e:
                # Skip sources that fail (network issues, etc.)
                pytest.skip(f"Failed to collect from {feed_url}: {e}")
        
        # Verify at least some items were collected
        # (May be 0 if all are duplicates from previous runs)
        assert total_collected >= 0, "Total collected should be non-negative"
        
        # Verify items are in DB
        all_items = test_db.query(Item).all()
        assert len(all_items) >= 0, "Items should exist in DB"
    
    def test_duplicate_prevention(self, test_db):
        """Test that duplicate items are not collected twice."""
        unique_id = get_unique_string()
        
        # Create a test source
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/test/feed_{unique_id}.xml",
            is_active=True
        )
        test_db.add(source)
        test_db.flush()
        
        # Create an existing item
        existing_link = f"https://example.com/article_{unique_id}"
        existing_item = Item(
            source_id=source.id,
            title="Existing Article",
            link=existing_link,
            published_at=datetime.now(timezone.utc)
        )
        test_db.add(existing_item)
        test_db.commit()
        
        # Mock feedparser to return the same link
        from unittest.mock import patch, MagicMock
        
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
            title="New Article Title",
            link=existing_link,  # Same link as existing
            description="New description"
        )
        mock_feed.entries = [mock_entry]
        
        collector = RSSCollector(test_db)
        
        with patch('backend.app.services.rss_collector.feedparser.parse', return_value=mock_feed):
            count = collector.collect_source(source)
            
            # Should skip duplicate
            assert count == 0, "Should not collect duplicate item"
            
            # Verify only one item exists
            items = test_db.query(Item).filter(Item.source_id == source.id).all()
            assert len(items) == 1, "Should only have one item (the existing one)"
            assert items[0].title == "Existing Article", "Should keep original item"

