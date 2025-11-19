"""Update field for existing items using ClassifierService."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal
from backend.app.models.item import Item
from backend.app.services.classifier import ClassifierService


def update_items_field(batch_size: int = 100, limit: int = None, update_tags: bool = True):
    """Update field and tags for items.
    
    Args:
        batch_size: Number of items to commit at once
        limit: Maximum number of items to update (None = all)
        update_tags: If True, also update tags for items that have field but no tags
    """
    db: Session = SessionLocal()
    try:
        # Query items without field OR items with field but empty custom_tags (if update_tags=True)
        if update_tags:
            from sqlalchemy import or_, func, cast
            from sqlalchemy.dialects.postgresql import JSONB
            # Check for empty array using JSONB length
            query = db.query(Item).filter(
                or_(
                    Item.field.is_(None),
                    func.jsonb_array_length(cast(Item.custom_tags, JSONB)) == 0
                )
            )
        else:
            query = db.query(Item).filter(Item.field.is_(None))
        
        if limit:
            query = query.limit(limit)
        
        items = query.all()
        total = len(items)
        
        if total == 0:
            print("[UpdateField] No items to update")
            return
        
        print(f"[UpdateField] Found {total} items to update")
        
        classifier = ClassifierService()
        updated = 0
        
        for idx, item in enumerate(items, 1):
            # Classify to get field and tags
            result = classifier.classify(
                item.title,
                item.summary_short or ""
            )
            
            # Update field and tags
            item.field = result.get("field")
            item.iptc_topics = result.get("iptc_topics", [])
            item.iab_categories = result.get("iab_categories", [])
            item.custom_tags = result.get("custom_tags", [])
            updated += 1
            
            # Commit in batches
            if idx % batch_size == 0:
                db.commit()
                print(f"[UpdateField] Updated {idx}/{total} items")
        
        # Final commit
        db.commit()
        print(f"[UpdateField] Completed: {updated}/{total} items updated")
        
    except Exception as e:
        db.rollback()
        print(f"[UpdateField] Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Update field and tags for existing items")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size for commits")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of items to update")
    parser.add_argument("--no-tags", action="store_true", help="Don't update tags, only field")
    
    args = parser.parse_args()
    update_items_field(batch_size=args.batch_size, limit=args.limit, update_tags=not args.no_tags)

