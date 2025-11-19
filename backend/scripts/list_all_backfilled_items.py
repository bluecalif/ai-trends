"""List all items in the backfill window with full details.
Shows all items in the 21-day window and their grouping status.
"""
import sys
import io
import json
from datetime import datetime, timezone, timedelta, date
from pathlib import Path

# Fix Windows PowerShell encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from backend.app.core.database import SessionLocal
from backend.app.models.item import Item
from backend.app.models.dup_group_meta import DupGroupMeta


def main():
    db = SessionLocal()
    results_dir = Path(__file__).parent.parent / "tests" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    
    try:
        # Calculate backfill window
        ref_date = date.today()
        start_dt = datetime(ref_date.year, ref_date.month, ref_date.day, tzinfo=timezone.utc) - timedelta(days=21)
        end_dt = datetime(ref_date.year, ref_date.month, ref_date.day, tzinfo=timezone.utc)
        
        print(f"\n[Backfill Items] Querying items in window: {start_dt.date()} to {end_dt.date()}")
        
        # Get all items in window
        items = (
            db.query(Item)
            .filter(Item.published_at != None)  # noqa: E711
            .filter(Item.published_at >= start_dt)
            .filter(Item.published_at <= end_dt)
            .order_by(Item.published_at.asc())
            .all()
        )
        
        print(f"[Backfill Items] Found {len(items)} items in window")
        
        # Group by dup_group_id
        grouped_by_id = {}
        ungrouped = []
        
        for item in items:
            if item.dup_group_id:
                if item.dup_group_id not in grouped_by_id:
                    grouped_by_id[item.dup_group_id] = []
                grouped_by_id[item.dup_group_id].append(item)
            else:
                ungrouped.append(item)
        
        print(f"[Backfill Items] Items with dup_group_id: {len(items) - len(ungrouped)}")
        print(f"[Backfill Items] Items without dup_group_id: {len(ungrouped)}")
        print(f"[Backfill Items] Unique group IDs: {len(grouped_by_id)}")
        
        # Prepare output
        output = {
            "timestamp": ts,
            "window": {
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat(),
                "days": 21
            },
            "summary": {
                "total_items": len(items),
                "grouped_items": len(items) - len(ungrouped),
                "ungrouped_items": len(ungrouped),
                "unique_groups": len(grouped_by_id),
                "groups_with_multiple": sum(1 for gid, items_list in grouped_by_id.items() if len(items_list) > 1)
            },
            "items": []
        }
        
        # Add all items with full details
        for item in items:
            item_data = {
                "id": item.id,
                "source_id": item.source_id,
                "source_title": item.source.title if item.source else None,
                "title": item.title,
                "summary_short": item.summary_short,
                "link": item.link,
                "published_at": item.published_at.isoformat() if item.published_at else None,
                "author": item.author,
                "dup_group_id": item.dup_group_id,
                "iptc_topics": item.iptc_topics if isinstance(item.iptc_topics, list) else [],
                "iab_categories": item.iab_categories if isinstance(item.iab_categories, list) else [],
                "custom_tags": item.custom_tags if isinstance(item.custom_tags, list) else [],
            }
            output["items"].append(item_data)
        
        # Add group details
        output["groups"] = {}
        for group_id, items_list in sorted(grouped_by_id.items()):
            meta = db.query(DupGroupMeta).filter(DupGroupMeta.dup_group_id == group_id).first()
            output["groups"][str(group_id)] = {
                "member_count": len(items_list),
                "meta_member_count": meta.member_count if meta else None,
                "first_seen_at": meta.first_seen_at.isoformat() if meta and meta.first_seen_at else None,
                "last_updated_at": meta.last_updated_at.isoformat() if meta and meta.last_updated_at else None,
                "item_ids": [it.id for it in items_list],
                "items": [
                    {
                        "id": it.id,
                        "title": it.title,
                        "published_at": it.published_at.isoformat() if it.published_at else None,
                        "source": it.source.title if it.source else None,
                    }
                    for it in items_list
                ]
            }
        
        # Save to JSON
        out_file = results_dir / f"backfill_all_items_{ts}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n[Backfill Items] Full list saved to: {out_file}")
        
        # Print summary to console
        print(f"\n[Summary]")
        print(f"  Total items: {len(items)}")
        print(f"  Grouped: {len(items) - len(ungrouped)}")
        print(f"  Ungrouped: {len(ungrouped)}")
        print(f"  Groups: {len(grouped_by_id)}")
        print(f"  Groups with 2+ members: {sum(1 for gid, items_list in grouped_by_id.items() if len(items_list) > 1)}")
        
        # Show groups with multiple members
        multi_groups = {gid: items_list for gid, items_list in grouped_by_id.items() if len(items_list) > 1}
        if multi_groups:
            print(f"\n[Groups with multiple members]")
            for group_id, items_list in sorted(multi_groups.items(), key=lambda x: len(x[1]), reverse=True):
                print(f"\n  Group {group_id}: {len(items_list)} members")
                for it in items_list:
                    print(f"    - ID {it.id}: {it.title[:70]}")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()



