"""Delete OpenAI items older than 21 days."""
from datetime import datetime, timezone, timedelta
from sqlalchemy import and_, delete
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.models.source import Source
from backend.app.models.item import Item
from backend.app.models.bookmark import Bookmark
from backend.app.models.person_timeline import PersonTimeline
from backend.app.models.dup_group_meta import DupGroupMeta
from backend.app.models.item_entity import item_entities


def delete_old_openai_items(days: int = 21, dry_run: bool = True):
    """Delete OpenAI items older than specified days.
    
    Args:
        days: Number of days to keep (default: 21)
        dry_run: If True, only show what would be deleted without actually deleting
    """
    db: Session = SessionLocal()
    
    try:
        # 1. Find OpenAI source
        openai_source = db.query(Source).filter(
            Source.feed_url == "https://openai.com/blog/rss.xml"
        ).first()
        
        if not openai_source:
            print("[ERROR] OpenAI source not found")
            return
        
        print(f"[INFO] Found OpenAI source: {openai_source.title} (ID: {openai_source.id})")
        
        # 2. Calculate cutoff date
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        print(f"[INFO] Cutoff date: {cutoff_date.isoformat()} (keeping items from last {days} days)")
        
        # 3. Find old items
        old_items = db.query(Item).filter(
            and_(
                Item.source_id == openai_source.id,
                Item.published_at < cutoff_date
            )
        ).all()
        
        if not old_items:
            print("[INFO] No old items to delete")
            return
        
        print(f"[INFO] Found {len(old_items)} items to delete")
        
        if dry_run:
            print("\n[DRY RUN] Would delete the following:")
            for item in old_items[:10]:  # Show first 10
                print(f"  - Item {item.id}: {item.title[:50]}... (published: {item.published_at})")
            if len(old_items) > 10:
                print(f"  ... and {len(old_items) - 10} more items")
            
            # Count related data
            item_ids = [item.id for item in old_items]
            bookmarks_count = db.query(Bookmark).filter(Bookmark.item_id.in_(item_ids)).count()
            timeline_count = db.query(PersonTimeline).filter(PersonTimeline.item_id.in_(item_ids)).count()
            dup_meta_count = db.query(DupGroupMeta).filter(DupGroupMeta.dup_group_id.in_(item_ids)).count()
            
            print(f"\n[DRY RUN] Related data to delete:")
            print(f"  - Bookmarks: {bookmarks_count}")
            print(f"  - Person timeline events: {timeline_count}")
            print(f"  - Dup group meta: {dup_meta_count}")
            print(f"\n[DRY RUN] Total items to delete: {len(old_items)}")
            print("\n[DRY RUN] To actually delete, run with --apply flag")
            return
        
        # 4. Delete related data
        item_ids = [item.id for item in old_items]
        
        # Delete bookmarks
        bookmarks_deleted = db.query(Bookmark).filter(
            Bookmark.item_id.in_(item_ids)
        ).delete(synchronize_session=False)
        print(f"[INFO] Deleted {bookmarks_deleted} bookmarks")
        
        # Delete person timeline events
        timeline_deleted = db.query(PersonTimeline).filter(
            PersonTimeline.item_id.in_(item_ids)
        ).delete(synchronize_session=False)
        print(f"[INFO] Deleted {timeline_deleted} person timeline events")
        
        # Delete dup_group_meta (if dup_group_id matches)
        dup_meta_deleted = db.query(DupGroupMeta).filter(
            DupGroupMeta.dup_group_id.in_(item_ids)
        ).delete(synchronize_session=False)
        print(f"[INFO] Deleted {dup_meta_deleted} dup_group_meta entries")
        
        # Delete item_entities (many-to-many)
        item_entities_deleted = db.execute(
            delete(item_entities).where(item_entities.c.item_id.in_(item_ids))
        ).rowcount
        print(f"[INFO] Deleted {item_entities_deleted} item_entity relationships")
        
        # 5. Delete items
        items_deleted = db.query(Item).filter(
            Item.id.in_(item_ids)
        ).delete(synchronize_session=False)
        print(f"[INFO] Deleted {items_deleted} items")
        
        # Commit
        db.commit()
        print(f"\n[SUCCESS] Deleted {items_deleted} OpenAI items older than {days} days")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to delete items: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Delete old OpenAI items")
    parser.add_argument("--days", type=int, default=21, help="Number of days to keep (default: 21)")
    parser.add_argument("--apply", action="store_true", help="Actually delete (default: dry-run)")
    
    args = parser.parse_args()
    
    delete_old_openai_items(days=args.days, dry_run=not args.apply)

