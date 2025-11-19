"""Analyze backfill grouping results.
Shows groups with multiple members and sample duplicates.
"""
import sys
import io

# Fix Windows PowerShell encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from datetime import datetime, timezone, timedelta, date

from backend.app.core.database import SessionLocal
from backend.app.models.item import Item
from backend.app.models.dup_group_meta import DupGroupMeta


def main():
    db = SessionLocal()
    try:
        # Count groups
        total_groups = db.query(DupGroupMeta).count()
        groups_with_multiple = (
            db.query(DupGroupMeta).filter(DupGroupMeta.member_count > 1).count()
        )
        
        print(f"\n[Analysis] Total groups: {total_groups}")
        print(f"[Analysis] Groups with multiple members: {groups_with_multiple}")
        
        # Get groups with multiple members
        multi_groups = (
            db.query(DupGroupMeta)
            .filter(DupGroupMeta.member_count > 1)
            .order_by(DupGroupMeta.member_count.desc())
            .limit(20)
            .all()
        )
        
        print(f"\n[Analysis] Top {len(multi_groups)} groups with multiple members:")
        print("=" * 80)
        
        for meta in multi_groups:
            items = (
                db.query(Item)
                .filter(Item.dup_group_id == meta.dup_group_id)
                .order_by(Item.published_at.asc())
                .all()
            )
            
            print(f"\n[Group {meta.dup_group_id}] {meta.member_count} members")
            print(f"  First seen: {meta.first_seen_at}")
            print(f"  Last updated: {meta.last_updated_at}")
            print(f"  Timeline:")
            
            for idx, item in enumerate(items, 1):
                print(f"\n  {idx}. [{item.published_at.strftime('%Y-%m-%d %H:%M')}]")
                print(f"     Title: {item.title}")
                print(f"     Source: {item.source.title if item.source else 'N/A'}")
                if item.summary_short:
                    summary_short = item.summary_short[:150] + "..." if len(item.summary_short) > 150 else item.summary_short
                    print(f"     Summary: {summary_short}")
                if item.custom_tags:
                    print(f"     Tags: {', '.join(item.custom_tags) if isinstance(item.custom_tags, list) else 'N/A'}")
                print(f"     Link: {item.link}")
            
            print("\n" + "-" * 80)
        
        # Statistics
        member_counts = [m.member_count for m in db.query(DupGroupMeta.member_count).all()]
        if member_counts:
            avg_members = sum(member_counts) / len(member_counts)
            max_members = max(member_counts)
            print(f"\n[Analysis] Statistics:")
            print(f"  Average members per group: {avg_members:.2f}")
            print(f"  Max members in a group: {max_members}")
            print(f"  Groups with 1 member: {member_counts.count(1)}")
            print(f"  Groups with 2+ members: {sum(1 for c in member_counts if c > 1)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

