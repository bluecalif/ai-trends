"""Unit tests for RSS collector service."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
import uuid

from backend.app.services.rss_collector import RSSCollector
from backend.app.models.source import Source
from backend.app.models.item import Item


def get_unique_string(prefix: str = "") -> str:
    """Generate unique string for test data."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestRSSCollectorParseFeed:
    """Test RSS feed parsing."""
    
    @patch('backend.app.services.rss_collector.feedparser')
    def test_parse_feed_success(self, mock_feedparser, test_db):
        """Test successful feed parsing."""
        # Mock feedparser response
        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.entries = [
            MagicMock(
                get=MagicMock(side_effect=lambda key, default="": {
                    "title": "Test Article 1",
                    "link": "https://example.com/article1",
                    "description": "Test description 1"
                }.get(key, default)),
                published_parsed=None
            ),
            MagicMock(
                get=MagicMock(side_effect=lambda key, default="": {
                    "title": "Test Article 2",
                    "link": "https://example.com/article2",
                    "description": "Test description 2"
                }.get(key, default)),
                published_parsed=None
            )
        ]
        mock_feedparser.parse.return_value = mock_feed
        
        collector = RSSCollector(test_db)
        result = collector.parse_feed("https://example.com/feed.xml")
        
        assert len(result) == 2
        assert result[0]["title"] == "Test Article 1"
        assert result[0]["link"] == "https://example.com/article1"
        assert result[1]["title"] == "Test Article 2"
    
    @patch('backend.app.services.rss_collector.feedparser')
    def test_parse_feed_error(self, mock_feedparser, test_db):
        """Test feed parsing error."""
        mock_feed = MagicMock()
        mock_feed.bozo = True
        mock_feed.bozo_exception = "Invalid feed format"
        mock_feedparser.parse.return_value = mock_feed
        
        collector = RSSCollector(test_db)
        
        with pytest.raises(ValueError, match="Feed parsing error"):
            collector.parse_feed("https://example.com/invalid-feed.xml")
    
    @patch('backend.app.services.rss_collector.feedparser')
    def test_parse_feed_with_date(self, mock_feedparser, test_db):
        """Test feed parsing with published date."""
        import time
        
        # Mock struct_time
        struct_time = time.struct_time((2024, 1, 15, 12, 0, 0, 0, 15, 0))
        
        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_entry = MagicMock()
        mock_entry.get = MagicMock(side_effect=lambda key, default="": {
            "title": "Test Article",
            "link": "https://example.com/article",
            "description": "Test description"
        }.get(key, default))
        mock_entry.published_parsed = struct_time
        mock_feed.entries = [mock_entry]
        mock_feedparser.parse.return_value = mock_feed
        
        collector = RSSCollector(test_db)
        result = collector.parse_feed("https://example.com/feed.xml")
        
        assert len(result) == 1
        assert isinstance(result[0]["published_at"], datetime)
        assert result[0]["published_at"].tzinfo == timezone.utc


class TestRSSCollectorCheckDuplicate:
    """Test duplicate checking."""
    
    def test_check_duplicate_not_exists(self, test_db):
        """Test duplicate check when item doesn't exist."""
        collector = RSSCollector(test_db)
        result = collector.check_duplicate("https://example.com/new-article")
        assert result is False
    
    def test_check_duplicate_exists(self, test_db):
        """Test duplicate check when item exists."""
        unique_id = get_unique_string()
        source = Source(
            title=f"Test Source {unique_id}",
            feed_url=f"https://example.com/feed_{unique_id}.xml"
        )
        test_db.add(source)
        test_db.flush()
        
        item = Item(
            source_id=source.id,
            title=f"Test Item {unique_id}",
            link="https://example.com/existing-article",
            published_at=datetime.now(timezone.utc)
        )
        test_db.add(item)
        test_db.commit()
        
        collector = RSSCollector(test_db)
        result = collector.check_duplicate("https://example.com/existing-article")
        assert result is True


class TestRSSCollectorNormalizeItem:
    """Test item normalization."""
    
    def test_normalize_item(self):
        """Test item normalization."""
        # Mock source (doesn't need DB)
        source = Mock()
        source.id = 1
        
        entry = {
            "title": "  Test Article  ",
            "link": "  https://example.com/article  ",
            "published_at": datetime.now(timezone.utc),
            "author": "  Test Author  ",
            "description": "Test description" * 100  # Long description
        }
        
        # Create collector with mock DB (normalize_item doesn't use DB)
        mock_db = Mock()
        collector = RSSCollector(mock_db)
        result = collector.normalize_item(entry, source)
        
        assert result["source_id"] == 1
        assert result["title"] == "Test Article"
        assert result["link"] == "https://example.com/article"
        assert result["author"] == "Test Author"
        assert len(result["summary_short"]) == 500  # Truncated to 500 chars
        assert result["published_at"] == entry["published_at"]
    
    def test_normalize_item_empty_author(self):
        """Test normalization with empty author."""
        # Mock source (doesn't need DB)
        source = Mock()
        source.id = 1
        
        entry = {
            "title": "Test Article",
            "link": "https://example.com/article",
            "published_at": datetime.now(timezone.utc),
            "author": "",
            "description": "Test description"
        }
        
        # Create collector with mock DB (normalize_item doesn't use DB)
        mock_db = Mock()
        collector = RSSCollector(mock_db)
        result = collector.normalize_item(entry, source)
        
        assert result["author"] is None


class TestRSSCollectorExtractAuthor:
    """Test author extraction."""
    
    def test_extract_author_from_author_field(self, test_db):
        """Test author extraction from author field."""
        mock_entry = MagicMock()
        mock_entry.author = "Test Author"
        mock_entry.authors = None
        
        collector = RSSCollector(test_db)
        result = collector._extract_author(mock_entry)
        
        assert result == "Test Author"
    
    def test_extract_author_from_authors_list(self, test_db):
        """Test author extraction from authors list."""
        mock_entry = MagicMock()
        del mock_entry.author
        mock_entry.authors = [{"name": "Test Author"}]
        
        collector = RSSCollector(test_db)
        result = collector._extract_author(mock_entry)
        
        assert result == "Test Author"
    
    def test_extract_author_none(self, test_db):
        """Test author extraction when not available."""
        mock_entry = MagicMock()
        del mock_entry.author
        mock_entry.authors = None
        
        collector = RSSCollector(test_db)
        result = collector._extract_author(mock_entry)
        
        assert result is None


class TestRSSCollectorExtractThumbnail:
    """Test thumbnail extraction."""
    
    def test_extract_thumbnail_from_media_thumbnail(self, test_db):
        """Test thumbnail extraction from media_thumbnail."""
        mock_entry = MagicMock()
        mock_entry.media_thumbnail = [{"url": "https://example.com/thumb.jpg"}]
        mock_entry.enclosures = None
        del mock_entry.media_content
        
        collector = RSSCollector(test_db)
        result = collector._extract_thumbnail(mock_entry)
        
        assert result == "https://example.com/thumb.jpg"
    
    def test_extract_thumbnail_from_enclosures(self, test_db):
        """Test thumbnail extraction from enclosures."""
        mock_entry = MagicMock()
        mock_entry.media_thumbnail = None
        mock_entry.enclosures = [
            {"type": "image/jpeg", "href": "https://example.com/image.jpg"}
        ]
        del mock_entry.media_content
        
        collector = RSSCollector(test_db)
        result = collector._extract_thumbnail(mock_entry)
        
        assert result == "https://example.com/image.jpg"
    
    def test_extract_thumbnail_none(self, test_db):
        """Test thumbnail extraction when not available."""
        mock_entry = MagicMock()
        mock_entry.media_thumbnail = None
        mock_entry.enclosures = []
        del mock_entry.media_content
        
        collector = RSSCollector(test_db)
        result = collector._extract_thumbnail(mock_entry)
        
        assert result is None

