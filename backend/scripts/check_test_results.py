"""Script to check test results - collected RSS items and summaries."""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import get_settings
from backend.app.models.source import Source
from backend.app.models.item import Item

settings = get_settings()

# Create database session
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Get TechCrunch source
    techcrunch = db.query(Source).filter(Source.feed_url == "https://techcrunch.com/feed/").first()
    
    if not techcrunch:
        print("TechCrunch source not found in database.")
        sys.exit(0)
    
    print(f"\n=== Source: {techcrunch.title} ===")
    print(f"Feed URL: {techcrunch.feed_url}")
    print(f"Active: {techcrunch.is_active}")
    
    # Get recent items (last 10)
    items = db.query(Item).filter(
        Item.source_id == techcrunch.id
    ).order_by(Item.published_at.desc()).limit(10).all()
    
    print(f"\n=== Recent Items (Total: {len(items)}) ===")
    
    for i, item in enumerate(items, 1):
        print(f"\n--- Item {i} ---")
        print(f"ID: {item.id}")
        print(f"Title: {item.title}")
        print(f"Link: {item.link}")
        print(f"Published: {item.published_at}")
        print(f"Author: {item.author or 'N/A'}")
        
        if item.summary_short:
            summary_preview = item.summary_short[:200] + "..." if len(item.summary_short) > 200 else item.summary_short
            print(f"Summary ({len(item.summary_short)} chars): {summary_preview}")
        else:
            print("Summary: None (not summarized yet)")
        
        print(f"Created: {item.created_at}")
    
    # Statistics
    total_items = db.query(Item).filter(Item.source_id == techcrunch.id).count()
    items_with_summary = db.query(Item).filter(
        Item.source_id == techcrunch.id,
        Item.summary_short.isnot(None)
    ).count()
    
    print(f"\n=== Statistics ===")
    print(f"Total items: {total_items}")
    print(f"Items with summary: {items_with_summary}")
    print(f"Items without summary: {total_items - items_with_summary}")
    
finally:
    db.close()
    engine.dispose()

