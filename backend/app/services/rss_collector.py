"""RSS/Atom feed collection service."""
import feedparser
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from backend.app.models.source import Source
from backend.app.models.item import Item


class RSSCollector:
    """RSS/Atom feed collector."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def parse_feed(self, feed_url: str) -> List[Dict]:
        """Parse RSS/Atom feed and return entries.
        
        Args:
            feed_url: RSS/Atom feed URL
            
        Returns:
            List of entry dictionaries with title, link, published_at, author, description
            
        Raises:
            ValueError: If feed parsing fails
        """
        feed = feedparser.parse(feed_url)
        
        if feed.bozo:
            error_msg = str(feed.bozo_exception) if feed.bozo_exception else "Unknown error"
            raise ValueError(f"Feed parsing error: {error_msg}")
        
        items = []
        for entry in feed.entries:
            item = {
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published_at": self._parse_date(entry),
                "author": self._extract_author(entry),
                "description": entry.get("description", ""),
                "thumbnail_url": self._extract_thumbnail(entry),  # Extract from entry object
            }
            items.append(item)
        
        return items
    
    def normalize_item(self, entry: Dict, source: Source) -> Dict:
        """Normalize entry metadata for Item model.
        
        Args:
            entry: Entry dictionary from parse_feed
            source: Source model instance
            
        Returns:
            Normalized dictionary for Item creation
        """
        # Handle None values for author and description
        author = entry.get("author")
        author_str = (author or "").strip() or None
        
        description = entry.get("description")
        description_str = (description or "").strip()[:500] or None if description else None
        
        return {
            "source_id": source.id,
            "title": entry["title"].strip(),
            "link": entry["link"].strip(),
            "published_at": entry["published_at"],
            "author": author_str,
            "summary_short": description_str,
            "thumbnail_url": entry.get("thumbnail_url"),  # Get from dictionary
        }
    
    def check_duplicate(self, link: str) -> bool:
        """Check if item with given link already exists.
        
        Args:
            link: Item link URL
            
        Returns:
            True if duplicate exists, False otherwise
        """
        existing = self.db.query(Item).filter(Item.link == link).first()
        return existing is not None
    
    def collect_source(self, source: Source) -> int:
        """Collect items from a source.
        
        Args:
            source: Source model instance
            
        Returns:
            Number of new items collected
            
        Raises:
            Exception: If collection fails (transaction rolled back)
        """
        try:
            entries = self.parse_feed(source.feed_url)
            count = 0
            
            for entry in entries:
                if self.check_duplicate(entry["link"]):
                    continue
                
                normalized = self.normalize_item(entry, source)
                item = Item(**normalized)
                self.db.add(item)
                count += 1
            
            self.db.commit()
            return count
        except Exception as e:
            self.db.rollback()
            raise
    
    def _parse_date(self, entry) -> datetime:
        """Parse published date from entry.
        
        Uses feedparser's parsed time structure if available,
        otherwise falls back to UTC now.
        
        Args:
            entry: Feedparser entry object
            
        Returns:
            Parsed datetime in UTC
        """
        # Use feedparser's parsed time structure (struct_time)
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            # Check if it's actually a struct_time (not MagicMock)
            try:
                import time
                timestamp = time.mktime(entry.published_parsed)
                return datetime.fromtimestamp(timestamp, tz=timezone.utc)
            except (TypeError, AttributeError):
                # Not a valid struct_time, fall through to default
                pass
        
        # Fallback to UTC now
        return datetime.now(timezone.utc)
    
    def _extract_author(self, entry) -> Optional[str]:
        """Extract author from entry.
        
        Args:
            entry: Feedparser entry object
            
        Returns:
            Author name or None
        """
        if hasattr(entry, "author"):
            return entry.author
        if hasattr(entry, "authors") and entry.authors:
            return entry.authors[0].get("name", "")
        return None
    
    def _extract_thumbnail(self, entry) -> Optional[str]:
        """Extract thumbnail URL from entry.
        
        Args:
            entry: Feedparser entry object
            
        Returns:
            Thumbnail URL or None
        """
        # Check media_thumbnail (common in RSS feeds)
        if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
            return entry.media_thumbnail[0].get("url", "")
        
        # Check enclosures (may contain images)
        if hasattr(entry, "enclosures") and entry.enclosures:
            for enc in entry.enclosures:
                if enc.get("type", "").startswith("image/"):
                    return enc.get("href", "")
        
        # Check media_content (Atom feeds)
        if hasattr(entry, "media_content") and entry.media_content:
            for media in entry.media_content:
                if media.get("type", "").startswith("image/"):
                    return media.get("url", "")
        
        return None

