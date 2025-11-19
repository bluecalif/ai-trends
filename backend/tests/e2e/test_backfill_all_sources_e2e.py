"""E2E test: Backfill grouping for all sources with 21-day window.
Includes batch processing and time monitoring.
"""
from datetime import datetime, timezone, timedelta, date
from pathlib import Path
import json
import time

import pytest

from backend.app.core.database import SessionLocal
from backend.app.models.item import Item
from backend.app.models.dup_group_meta import DupGroupMeta
from backend.app.services.group_backfill import GroupBackfill


@pytest.mark.slow
@pytest.mark.e2e_real_data
def test_backfill_all_sources_e2e():
    """Run backfill for all sources with time monitoring."""
    db = SessionLocal()
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = results_dir / f"backfill_all_sources_e2e_{ts}.json"

    result = {
        "test_name": "test_backfill_all_sources_e2e",
        "timestamp": ts,
        "window_days": 21,
        "collection": {"total_items": 0, "items_in_window": 0},
        "backfill": {
            "processed": 0,
            "duration_seconds": 0,
            "items_per_second": 0,
            "groups_created": 0,
            "groups_with_multiple_members": 0,
        },
        "status": "running",
    }

    try:
        ref_date = date.today()
        start_dt = datetime(ref_date.year, ref_date.month, ref_date.day, tzinfo=timezone.utc) - timedelta(days=21)
        end_dt = datetime(ref_date.year, ref_date.month, ref_date.day, tzinfo=timezone.utc)

        # Count items
        total_items = db.query(Item).count()
        items_in_window = (
            db.query(Item)
            .filter(Item.published_at != None)  # noqa: E711
            .filter(Item.published_at >= start_dt)
            .filter(Item.published_at <= end_dt)
            .count()
        )
        result["collection"]["total_items"] = total_items
        result["collection"]["items_in_window"] = items_in_window

        print(f"\n[Backfill E2E] Starting backfill for {items_in_window} items in 21-day window")
        print(f"[Backfill E2E] Total items in DB: {total_items}")

        # Run backfill with timing
        start_time = time.time()
        svc = GroupBackfill(db)
        processed = svc.run_backfill(ref_date, days=21)
        end_time = time.time()

        duration = end_time - start_time
        items_per_sec = processed / duration if duration > 0 else 0

        result["backfill"]["processed"] = processed
        result["backfill"]["duration_seconds"] = round(duration, 2)
        result["backfill"]["items_per_second"] = round(items_per_sec, 2)

        # Count groups
        total_groups = db.query(DupGroupMeta).count()
        groups_with_multiple = (
            db.query(DupGroupMeta).filter(DupGroupMeta.member_count > 1).count()
        )

        result["backfill"]["groups_created"] = total_groups
        result["backfill"]["groups_with_multiple_members"] = groups_with_multiple

        print(f"\n[Backfill E2E] Completed in {duration:.2f} seconds")
        print(f"[Backfill E2E] Processed: {processed} items ({items_per_sec:.2f} items/sec)")
        print(f"[Backfill E2E] Groups created: {total_groups}")
        print(f"[Backfill E2E] Groups with multiple members: {groups_with_multiple}")

        result["status"] = "passed"
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        print(f"\n[Backfill E2E] ERROR: {e}")
        raise
    finally:
        with open(out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n[Backfill E2E] Results saved to: {out}")
        db.close()

