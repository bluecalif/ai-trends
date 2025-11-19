"""E2E for Deduplicator on real RSS data.
Collect recent items, attempt near-duplicate grouping, and save results JSON.
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json

import pytest

from backend.app.services.rss_collector import RSSCollector
from backend.app.services.deduplicator import Deduplicator
from backend.app.models.source import Source
from backend.app.models.item import Item
from backend.app.core.database import SessionLocal


@pytest.mark.slow
@pytest.mark.e2e_real_data
def test_deduplicator_e2e_real_data():
    db = SessionLocal()
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = results_dir / f"deduplicator_e2e_real_data_{ts}.json"

    result = {
        "test_name": "test_deduplicator_e2e_real_data",
        "timestamp": ts,
        "source": None,
        "collection": {"count": 0, "status": "not_run"},
        "grouping": {"candidates": 0, "grouped": 0, "groups": []},
        "status": "running",
    }

    try:
        src = (
            db.query(Source)
            .filter(Source.feed_url == "https://techcrunch.com/feed/")
            .first()
        )
        if not src:
            src = Source(
                title="TechCrunch",
                feed_url="https://techcrunch.com/feed/",
                site_url="https://techcrunch.com",
                is_active=True,
            )
            db.add(src)
            db.flush()
            db.commit()
        result["source"] = {
            "id": src.id,
            "title": src.title,
            "feed_url": src.feed_url,
            "site_url": src.site_url,
        }

        # Get existing items from Supabase actual DB (skip collection, use existing data)
        existing_item_count = db.query(Item).filter(Item.source_id == src.id).count()
        result["collection"]["count"] = existing_item_count
        result["collection"]["status"] = "using_existing_data"
        
        if existing_item_count == 0:
            # If no existing data, try to collect
            print("[Deduplicator E2E] No existing items, attempting collection...")
            coll = RSSCollector(db)
            try:
                c = coll.collect_source(src)
                result["collection"]["count"] = c
                result["collection"]["status"] = "collected_new"
            except Exception as e:
                c = 0
                result["collection"]["error"] = str(e)
                result["collection"]["status"] = "collection_failed"

        # Pull last N items from actual DB and attempt grouping (lookback 7 days)
        items = (
            db.query(Item)
            .filter(Item.source_id == src.id)
            .order_by(Item.published_at.desc())
            .limit(10)
            .all()
        )
        result["grouping"]["candidates"] = len(items)
        d = Deduplicator(db, similarity_threshold=0.25, lookback_days=7)

        grouped = 0
        for it in items:
            gid = d.process_new_item(it)
            if gid:
                grouped += 1
                result["grouping"]["groups"].append(
                    {
                        "item_id": it.id,
                        "group_id": gid,
                        "title": it.title,
                        "published_at": it.published_at.isoformat() if it.published_at else None,
                    }
                )
        result["grouping"]["grouped"] = grouped
        result["status"] = "passed"
    finally:
        with open(out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n[TEST RESULTS] Saved to: {out}")
        print(f"[TEST RESULTS] Status: {result['status']}")
        print(f"[TEST RESULTS] Collected: {result['collection']['count']} items")
        print(f"[TEST RESULTS] Grouped: {result['grouping']['grouped']} / {result['grouping']['candidates']}")
        db.close()

