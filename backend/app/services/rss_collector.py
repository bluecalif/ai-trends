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
        # First attempt: direct URL with headers (helps some feeds)
        headers = {
            "User-Agent": "ai-trend-bot/1.0 (+https://example.com)",
            "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, */*;q=0.8",
        }
        feed = feedparser.parse(feed_url, request_headers=headers)

        # Fallback: fetch bytes manually and let feedparser parse content
        if getattr(feed, "bozo", False):
            try:
                from urllib.request import Request, urlopen  # stdlib, no extra dep

                req = Request(feed_url, headers=headers)
                with urlopen(req, timeout=15) as resp:
                    content_bytes = resp.read()
                # Try bytes first; feedparser can sniff encoding
                feed = feedparser.parse(content_bytes)
                if getattr(feed, "bozo", False):
                    # Last resort: decode as utf-8, ignore errors
                    feed = feedparser.parse(content_bytes.decode("utf-8", errors="ignore"))
            except Exception as e:
                error_msg = str(getattr(feed, "bozo_exception", e)) if getattr(feed, "bozo", False) else str(e)
                raise ValueError(f"Feed parsing error: {error_msg}")

        if getattr(feed, "bozo", False):
            error_msg = str(feed.bozo_exception) if feed.bozo_exception else "Unknown error"
            raise ValueError(f"Feed parsing error: {error_msg}")
        
        items = []
        for entry in feed.entries:
            # Categories/tags (if present)
            categories: List[str] = []
            try:
                if hasattr(entry, "tags") and entry.tags:
                    for t in entry.tags:
                        term = t.get("term") if isinstance(t, dict) else getattr(t, "term", None)
                        if term:
                            categories.append(str(term))
            except Exception:
                # best-effort; ignore malformed tags
                pass
            item = {
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published_at": self._parse_date(entry),
                "author": self._extract_author(entry),
                "description": entry.get("description", ""),
                "thumbnail_url": self._extract_thumbnail(entry),  # Extract from entry object
                "categories": categories,
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

            # Optional source-specific filtering: The Keyword → only Google DeepMind items
            if source.feed_url.strip().lower() == "https://blog.google/feed/":
                filtered = []
                for e in entries:
                    cats = [c.lower() for c in (e.get("categories") or [])]
                    title = (e.get("title") or "").lower()
                    desc = (e.get("description") or "").lower()
                    link = (e.get("link") or "").lower()
                    in_category = any("google deepmind" in c for c in cats)
                    backup_match = ("deepmind" in title) or ("deepmind" in desc) or ("/technology/google-deepmind/" in link)
                    if in_category or backup_match:
                        filtered.append(e)
                entries = filtered
            
            # AI-related filtering for WIRED and The Verge
            elif "wired.com" in source.feed_url.lower() or "theverge.com" in source.feed_url.lower():
                ai_keywords = [
                    "ai", "artificial intelligence", "machine learning", "ml", "deep learning",
                    "neural network", "llm", "gpt", "chatgpt", "openai", "anthropic", "claude",
                    "gemini", "transformer", "language model", "computer vision", "nlp",
                    "robotics", "autonomous", "algorithm", "data science", "big data",
                    "neural", "automation", "intelligent", "smart", "cognitive"
                ]
                filtered = []
                for e in entries:
                    title = (e.get("title") or "").lower()
                    desc = (e.get("description") or "").lower()
                    link = (e.get("link") or "").lower()
                    cats = [c.lower() for c in (e.get("categories") or [])]
                    
                    # Check if any AI keyword appears in title, description, link, or categories
                    text_to_check = f"{title} {desc} {link} {' '.join(cats)}"
                    if any(keyword in text_to_check for keyword in ai_keywords):
                        filtered.append(e)
                entries = filtered
            
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

