"""Verify items in 21-day window directly from DB."""
import sys
import io
from datetime import datetime, timezone, timedelta, date

# Fix Windows PowerShell encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from backend.app.core.database import SessionLocal
from backend.app.models.item import Item
from backend.app.models.source import Source
from sqlalchemy import func


def main():
    db = SessionLocal()
    try:
        # Calculate 21-day window
        ref_date = date.today()
        start_dt = datetime(ref_date.year, ref_date.month, ref_date.day, tzinfo=timezone.utc) - timedelta(days=21)
        end_dt = datetime(ref_date.year, ref_date.month, ref_date.day, tzinfo=timezone.utc)
        
        print(f"\n[Verify] Window: {start_dt.date()} to {end_dt.date()} (21 days)")
        
        # Count items in window
        total_count = (
            db.query(Item)
            .filter(Item.published_at != None)  # noqa: E711
            .filter(Item.published_at >= start_dt)
            .filter(Item.published_at <= end_dt)
            .count()
        )
        
        print(f"[Verify] Total items in window: {total_count}")
        
        # Count by source
        source_counts = (
            db.query(Source.title, func.count(Item.id).label('count'))
            .join(Item, Source.id == Item.source_id)
            .filter(Item.published_at != None)  # noqa: E711
            .filter(Item.published_at >= start_dt)
            .filter(Item.published_at <= end_dt)
            .group_by(Source.title)
            .order_by(func.count(Item.id).desc())
            .all()
        )
        
        print(f"\n[Verify] Items by source:")
        for source_title, count in source_counts:
            print(f"  {source_title}: {count}")
        
        # Date distribution
        date_dist = (
            db.query(
                func.date(Item.published_at).label('pub_date'),
                func.count(Item.id).label('count')
            )
            .filter(Item.published_at != None)  # noqa: E711
            .filter(Item.published_at >= start_dt)
            .filter(Item.published_at <= end_dt)
            .group_by(func.date(Item.published_at))
            .order_by(func.date(Item.published_at).desc())
            .all()
        )
        
        print(f"\n[Verify] Items by date (last 5 days):")
        for pub_date, count in date_dist[:5]:
            print(f"  {pub_date}: {count}")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()



