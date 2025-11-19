"""Show actual duplicate groups that exist in the database.
Groups items by dup_group_id and shows their details.
"""

import sys
import io
from collections import defaultdict

# Fix Windows PowerShell encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from backend.app.core.database import SessionLocal
from backend.app.models.item import Item
from backend.app.models.dup_group_meta import DupGroupMeta


def main():
    db = SessionLocal()
    try:
        # Get all items with dup_group_id set
        grouped_items = (
            db.query(Item)
            .filter(Item.dup_group_id != None)  # noqa: E711
            .order_by(Item.dup_group_id, Item.published_at.asc())
            .all()
        )

        # Group by dup_group_id
        groups = defaultdict(list)
        for item in grouped_items:
            groups[item.dup_group_id].append(item)

        # Filter groups with multiple members
        multi_groups = {gid: items for gid, items in groups.items() if len(items) > 1}

        print(f"\n[Actual Groups] Found {len(multi_groups)} groups with multiple members")
        print(f"  Total grouped items: {len(grouped_items)}")
        print(f"  Total groups (including singles): {len(groups)}")
        print("=" * 100)

        # Sort by member count
        sorted_groups = sorted(multi_groups.items(), key=lambda x: len(x[1]), reverse=True)

        for group_id, items in sorted_groups:
            meta = db.query(DupGroupMeta).filter(DupGroupMeta.dup_group_id == group_id).first()

            print(f"\n[Group {group_id}] {len(items)} members")
            if meta:
                print(
                    f"  Meta: first_seen={meta.first_seen_at}, last_updated={meta.last_updated_at}, count={meta.member_count}"
                )
            else:
                print(f"  WARNING: No meta found for group {group_id}")

            print(f"\n  Timeline:")
            for idx, item in enumerate(items, 1):
                pub_time = (
                    item.published_at.strftime("%Y-%m-%d %H:%M") if item.published_at else "N/A"
                )
                print(f"\n  {idx}. [{pub_time}] ID: {item.id}")
                print(f"     Title: {item.title}")
                print(f"     Source: {item.source.title if item.source else 'N/A'}")
                if item.summary_short:
                    summary = (
                        item.summary_short[:200] + "..."
                        if len(item.summary_short) > 200
                        else item.summary_short
                    )
                    print(f"     Summary: {summary}")
                if item.custom_tags and isinstance(item.custom_tags, list) and item.custom_tags:
                    print(f"     Tags: {', '.join(item.custom_tags)}")
                print(f"     Link: {item.link}")

            print("\n" + "-" * 100)

        # Summary
        print(f"\n[Summary]")
        print(f"  Groups with 2+ members: {len(multi_groups)}")
        total_members = sum(len(items) for items in multi_groups.values())
        print(f"  Total items in multi-member groups: {total_members}")

        # Show group size distribution
        size_dist = defaultdict(int)
        for items in multi_groups.values():
            size_dist[len(items)] += 1

        print(f"\n  Group size distribution:")
        for size in sorted(size_dist.keys(), reverse=True):
            print(f"    {size} members: {size_dist[size]} groups")

    finally:
        db.close()


if __name__ == "__main__":
    main()
