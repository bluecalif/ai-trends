"""Update field for existing items using ClassifierService."""
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal
from backend.app.models.item import Item
from backend.app.services.classifier import ClassifierService


def classify_single_item(item: Item, classifier: ClassifierService) -> Dict:
    """Classify a single item (runs in thread pool).
    
    Args:
        item: Item to classify
        classifier: ClassifierService instance
        
    Returns:
        Dictionary with item_id and classification result
    """
    try:
        result = classifier.classify(
            item.title,
            item.summary_short or ""
        )
        return {
            "item_id": item.id,
            "success": True,
            "result": result
        }
    except Exception as e:
        # Return default classification on error
        return {
            "item_id": item.id,
            "success": False,
            "error": str(e),
            "result": {"field": "research", "iptc_topics": [], "iab_categories": [], "custom_tags": []}
        }


def update_items_field(
    batch_size: int = 100, 
    limit: int = None, 
    update_tags: bool = True,
    parallel: bool = True,
    max_workers: int = 15
):
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
        print(f"[UpdateField] Mode: {'Parallel' if parallel else 'Sequential'} (workers: {max_workers if parallel else 1})")
        
        classifier = ClassifierService()
        updated = 0
        failed = 0
        
        if parallel:
            # Parallel processing with ThreadPoolExecutor
            item_dict = {item.id: item for item in items}
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all classification tasks
                future_to_item = {
                    executor.submit(classify_single_item, item, classifier): item.id
                    for item in items
                }
                
                # Process results as they complete
                results = {}
                completed = 0
                
                for future in as_completed(future_to_item):
                    completed += 1
                    item_id = future_to_item[future]
                    
                    try:
                        classification_result = future.result()
                        results[item_id] = classification_result
                        
                        # Log progress every 50 items
                        if completed % 50 == 0:
                            print(f"[UpdateField] Classified {completed}/{total} items...")
                    except Exception as e:
                        print(f"[UpdateField] Error classifying item {item_id}: {e}")
                        results[item_id] = {
                            "item_id": item_id,
                            "success": False,
                            "error": str(e),
                            "result": {"field": "research", "iptc_topics": [], "iab_categories": [], "custom_tags": []}
                        }
                
                # Update items with classification results
                print(f"[UpdateField] Updating database with classification results...")
                for idx, (item_id, classification_result) in enumerate(results.items(), 1):
                    item = item_dict[item_id]
                    result = classification_result["result"]
                    
                    item.field = result.get("field")
                    item.iptc_topics = result.get("iptc_topics", [])
                    item.iab_categories = result.get("iab_categories", [])
                    item.custom_tags = result.get("custom_tags", [])
                    
                    if classification_result["success"]:
                        updated += 1
                    else:
                        failed += 1
                    
                    # Commit in batches
                    if idx % batch_size == 0:
                        db.commit()
                        print(f"[UpdateField] Updated {idx}/{total} items (success: {updated}, failed: {failed})")
                
                # Final commit
                db.commit()
                print(f"[UpdateField] Completed: {updated}/{total} items updated successfully, {failed} failed")
        else:
            # Sequential processing (original method)
            for idx, item in enumerate(items, 1):
                try:
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
                except Exception as e:
                    print(f"[UpdateField] Error classifying item {item.id}: {e}")
                    # Set default field on error
                    item.field = "research"
                    failed += 1
                
                # Commit in batches
                if idx % batch_size == 0:
                    db.commit()
                    print(f"[UpdateField] Updated {idx}/{total} items (success: {updated}, failed: {failed})")
            
            # Final commit
            db.commit()
            print(f"[UpdateField] Completed: {updated}/{total} items updated successfully, {failed} failed")
        
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
    parser.add_argument("--no-parallel", action="store_true", help="Disable parallel processing (use sequential)")
    parser.add_argument("--max-workers", type=int, default=15, help="Number of parallel workers (default: 15)")
    
    args = parser.parse_args()
    update_items_field(
        batch_size=args.batch_size, 
        limit=args.limit, 
        update_tags=not args.no_tags,
        parallel=not args.no_parallel,
        max_workers=args.max_workers
    )

