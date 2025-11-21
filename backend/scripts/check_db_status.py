"""Check database status (sources and items count).

Run from project root:
  poetry run python -m backend.scripts.check_db_status
"""
import sys
import io

# Fix Windows PowerShell encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from backend.app.core.database import SessionLocal
from backend.app.models.source import Source
from backend.app.models.item import Item
from backend.app.core.config import get_settings


def main():
    settings = get_settings()
    db_url = settings.DATABASE_URL
    
    # Mask password in URL for logging
    if "@" in db_url:
        parts = db_url.split("@")
        if len(parts) == 2:
            masked_url = f"{parts[0].split('://')[0]}://***:***@{parts[1]}"
        else:
            masked_url = "***MASKED***"
    else:
        masked_url = db_url
    
    print(f"[CheckDB] DATABASE_URL: {masked_url}")
    print()
    
    db = SessionLocal()
    try:
        # Check sources
        all_sources = db.query(Source).all()
        active_sources = db.query(Source).filter(Source.is_active == True).all()  # noqa: E712
        inactive_sources = db.query(Source).filter(Source.is_active == False).all()  # noqa: E712
        
        print(f"[CheckDB] ===== Sources =====")
        print(f"Total sources: {len(all_sources)}")
        print(f"Active sources: {len(active_sources)}")
        print(f"Inactive sources: {len(inactive_sources)}")
        print()
        
        if active_sources:
            print(f"[CheckDB] Active sources detail:")
            for s in active_sources:
                item_count = db.query(Item).filter(Item.source_id == s.id).count()
                print(f"  [{s.id:3d}] {s.title:<40} | Items: {item_count:4d} | {s.feed_url[:60]}...")
        print()
        
        # Check items
        total_items = db.query(Item).count()
        items_with_summary = db.query(Item).filter(Item.summary_short.isnot(None)).count()
        items_with_group = db.query(Item).filter(Item.dup_group_id.isnot(None)).count()
        
        print(f"[CheckDB] ===== Items =====")
        print(f"Total items: {total_items}")
        print(f"Items with summary: {items_with_summary}")
        print(f"Items with group: {items_with_group}")
        print()
        
        # Source-wise item counts
        if total_items > 0:
            print(f"[CheckDB] ===== Items by Source =====")
            from sqlalchemy import func
            source_stats = (
                db.query(
                    Source.id,
                    Source.title,
                    func.count(Item.id).label('item_count')
                )
                .outerjoin(Item, Source.id == Item.source_id)
                .group_by(Source.id, Source.title)
                .order_by(func.count(Item.id).desc())
                .all()
            )
            for stat in source_stats:
                print(f"  [{stat.id:3d}] {stat.title:<40} | Items: {stat.item_count:4d}")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()




