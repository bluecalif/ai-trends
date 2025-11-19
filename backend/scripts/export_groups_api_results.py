"""Export groups API results to JSON for analysis.
Tests /api/groups endpoint with new/incremental queries.
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
from backend.app.models.dup_group_meta import DupGroupMeta
from backend.app.models.item import Item


def query_groups(db, since_dt: datetime, kind: str, page: int = 1, page_size: int = 100):
    """Query groups similar to API endpoint."""
    from sqlalchemy import and_
    
    q = db.query(DupGroupMeta)
    if kind == "new":
        q = q.filter(DupGroupMeta.first_seen_at >= since_dt)
    else:
        q = q.filter(and_(DupGroupMeta.first_seen_at < since_dt, DupGroupMeta.last_updated_at >= since_dt))
    
    total = q.count()
    metas = (
        q.order_by(DupGroupMeta.last_updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    
    groups = []
    for m in metas:
        seed = db.query(Item).filter(Item.id == m.dup_group_id).first()
        groups.append({
            "dup_group_id": m.dup_group_id,
            "first_seen_at": m.first_seen_at.isoformat() if m.first_seen_at else None,
            "last_updated_at": m.last_updated_at.isoformat() if m.last_updated_at else None,
            "member_count": m.member_count,
            "representative": {
                "id": seed.id if seed else None,
                "title": seed.title if seed else None,
                "link": seed.link if seed else None,
                "published_at": seed.published_at.isoformat() if seed and seed.published_at else None,
            },
        })
    
    return {"total": total, "page": page, "page_size": page_size, "groups": groups}


def main():
    db = SessionLocal()
    results_dir = Path(__file__).parent.parent / "tests" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    
    try:
        # Use REF_DATE (today) as since date
        ref_date = date.today()
        since_dt = datetime(ref_date.year, ref_date.month, ref_date.day, tzinfo=timezone.utc)
        
        print(f"\n[Export] Querying groups since {since_dt.date()}")
        
        # Query new groups
        new_groups = query_groups(db, since_dt, "new", page=1, page_size=100)
        print(f"[Export] New groups: {new_groups['total']} total, {len(new_groups['groups'])} in page 1")
        
        # Query incremental groups
        inc_groups = query_groups(db, since_dt, "incremental", page=1, page_size=100)
        print(f"[Export] Incremental groups: {inc_groups['total']} total, {len(inc_groups['groups'])} in page 1")
        
        # Save results
        result = {
            "timestamp": ts,
            "ref_date": ref_date.isoformat(),
            "since_datetime": since_dt.isoformat(),
            "new_groups": new_groups,
            "incremental_groups": inc_groups,
        }
        
        out_file = results_dir / f"groups_api_export_{ts}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n[Export] Results saved to: {out_file}")
        
        # Summary
        print(f"\n[Export] Summary:")
        print(f"  New groups: {new_groups['total']}")
        print(f"  Incremental groups: {inc_groups['total']}")
        print(f"  Total groups in DB: {db.query(DupGroupMeta).count()}")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()

