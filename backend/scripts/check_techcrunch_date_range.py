"""Check TechCrunch date range in database."""
from datetime import datetime, timezone

from backend.app.core.database import SessionLocal
from backend.app.models.item import Item
from backend.app.models.source import Source


def main():
    db = SessionLocal()
    try:
        src = db.query(Source).filter(Source.feed_url == "https://techcrunch.com/feed/").first()
        if not src:
            print("TechCrunch source not found")
            return

        # Latest item
        latest = db.query(Item).filter(Item.source_id == src.id).order_by(Item.published_at.desc()).first()
        # Oldest item
        oldest = db.query(Item).filter(Item.source_id == src.id).order_by(Item.published_at.asc()).first()
        # Total count
        total = db.query(Item).filter(Item.source_id == src.id).count()

        now = datetime.now(timezone.utc)

        print(f"Source: {src.title}")
        print(f"Total items: {total}")
        if latest:
            days_ago_latest = (now - latest.published_at).days
            print(f"Latest item: {latest.published_at} ({days_ago_latest} days ago)")
            print(f"  Title: {latest.title[:80]}...")
        else:
            print("No items found")

        if oldest:
            days_ago_oldest = (now - oldest.published_at).days
            print(f"Oldest item: {oldest.published_at} ({days_ago_oldest} days ago)")
            print(f"  Title: {oldest.title[:80]}...")
            if latest and oldest:
                date_range = (latest.published_at - oldest.published_at).days
                print(f"Date range: {date_range} days")
    finally:
        db.close()


if __name__ == "__main__":
    main()

