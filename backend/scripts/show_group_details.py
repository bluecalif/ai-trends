"""Show detailed information about duplicate groups.
Shows all items in groups with multiple members.
"""
import sys
import io

# Fix Windows PowerShell encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from backend.app.core.database import SessionLocal
from backend.app.models.item import Item
from backend.app.models.dup_group_meta import DupGroupMeta


def main():
    db = SessionLocal()
    try:
        # Get all groups with multiple members
        multi_groups = (
            db.query(DupGroupMeta)
            .filter(DupGroupMeta.member_count > 1)
            .order_by(DupGroupMeta.member_count.desc())
            .all()
        )
        
        print(f"\n[Group Details] Found {len(multi_groups)} groups with multiple members\n")
        print("=" * 100)
        
        for meta in multi_groups:
            # Query items by dup_group_id
            items = (
                db.query(Item)
                .filter(Item.dup_group_id == meta.dup_group_id)
                .order_by(Item.published_at.asc())
                .all()
            )
            
            # Also check if seed item exists
            seed = db.query(Item).filter(Item.id == meta.dup_group_id).first()
            
            print(f"\n[Group {meta.dup_group_id}] {meta.member_count} members")
            print(f"  First seen: {meta.first_seen_at}")
            print(f"  Last updated: {meta.last_updated_at}")
            print(f"  Items found: {len(items)}")
            
            if seed:
                print(f"  Seed item: {seed.id} - {seed.title[:70]}")
            
            if items:
                print(f"\n  Timeline:")
                for idx, item in enumerate(items, 1):
                    pub_time = item.published_at.strftime('%Y-%m-%d %H:%M') if item.published_at else 'N/A'
                    print(f"\n  {idx}. [{pub_time}] ID: {item.id}")
                    print(f"     Title: {item.title}")
                    print(f"     Source: {item.source.title if item.source else 'N/A'}")
                    if item.summary_short:
                        summary = item.summary_short[:200] + "..." if len(item.summary_short) > 200 else item.summary_short
                        print(f"     Summary: {summary}")
                    if item.custom_tags and isinstance(item.custom_tags, list) and item.custom_tags:
                        print(f"     Tags: {', '.join(item.custom_tags)}")
                    print(f"     Link: {item.link}")
            else:
                print(f"  WARNING: No items found with dup_group_id={meta.dup_group_id}")
                # Check if seed exists
                if seed:
                    print(f"  Seed item exists: {seed.id} - {seed.title[:70]}")
                    print(f"  Seed dup_group_id: {seed.dup_group_id}")
            
            print("\n" + "-" * 100)
        
        # Summary
        print(f"\n[Summary]")
        print(f"  Total groups with multiple members: {len(multi_groups)}")
        total_items_in_groups = sum(
            db.query(Item).filter(Item.dup_group_id == m.dup_group_id).count()
            for m in multi_groups
        )
        print(f"  Total items in these groups: {total_items_in_groups}")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()


