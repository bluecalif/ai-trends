"""Investigate group mismatch between meta and actual items.
Checks why member_count doesn't match actual items.
"""

import sys
import io

# Fix Windows PowerShell encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

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

        print(f"\n[Investigation] Checking {len(multi_groups)} groups with multiple members\n")
        print("=" * 100)

        for meta in multi_groups:
            # Check items with this dup_group_id
            items_by_group_id = db.query(Item).filter(Item.dup_group_id == meta.dup_group_id).all()

            # Check seed item
            seed = db.query(Item).filter(Item.id == meta.dup_group_id).first()

            # Check if seed has different dup_group_id
            seed_group_id = seed.dup_group_id if seed else None

            print(f"\n[Group {meta.dup_group_id}]")
            print(f"  Meta member_count: {meta.member_count}")
            print(f"  Items with dup_group_id={meta.dup_group_id}: {len(items_by_group_id)}")

            if seed:
                print(f"  Seed item ID: {seed.id}")
                print(f"  Seed dup_group_id: {seed_group_id}")
                print(f"  Seed title: {seed.title[:70]}")

                # If seed has different group_id, find items with that group_id
                if seed_group_id and seed_group_id != meta.dup_group_id:
                    items_by_seed_group = (
                        db.query(Item).filter(Item.dup_group_id == seed_group_id).all()
                    )
                    print(
                        f"  Items with seed's dup_group_id={seed_group_id}: {len(items_by_seed_group)}"
                    )
                    if items_by_seed_group:
                        print(f"  Actual group members:")
                        for it in items_by_seed_group[:5]:
                            print(f"    - ID {it.id}: {it.title[:60]}")
            else:
                print(f"  WARNING: Seed item {meta.dup_group_id} not found!")

            # Show items found
            if items_by_group_id:
                print(f"  Items with this group_id:")
                for it in items_by_group_id[:5]:
                    print(f"    - ID {it.id}: {it.title[:60]}")

            print("-" * 100)

        # Also check all items with dup_group_id set
        all_grouped_items = db.query(Item).filter(Item.dup_group_id != None).count()  # noqa: E711
        print(f"\n[Summary]")
        print(f"  Total items with dup_group_id set: {all_grouped_items}")
        print(f"  Total groups in meta: {db.query(DupGroupMeta).count()}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
