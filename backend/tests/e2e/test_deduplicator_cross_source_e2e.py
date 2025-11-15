"""E2E: Cross-source dedup/grouping on real RSS data.
Collect from multiple sources, widen time window, and save results JSON.
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json

import pytest

from backend.app.core.database import SessionLocal
from backend.app.models.source import Source
from backend.app.models.item import Item
from backend.app.services.rss_collector import RSSCollector
from backend.app.services.deduplicator import Deduplicator


SOURCES = [
    ("TechCrunch", "https://techcrunch.com/feed/", "https://techcrunch.com"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "https://www.theverge.com"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/", "https://venturebeat.com"),
]


@pytest.mark.slow
@pytest.mark.e2e_real_data
def test_deduplicator_cross_source_e2e():
    db = SessionLocal()
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = results_dir / f"deduplicator_cross_source_e2e_{ts}.json"

    result = {
        "test_name": "test_deduplicator_cross_source_e2e",
        "timestamp": ts,
        "sources": [],
        "collection": {"total": 0, "per_source": []},
        "window_days": 10,
        "params": {
            "similarity_threshold": 0.20,
            "lookback_days": 14,
            "max_items_per_source": 15,
        },
        "grouping": {"candidates": 0, "grouped": 0, "groups": []},
        "status": "running",
    }

    try:
        # Ensure sources exist and collect
        collector = RSSCollector(db)
        per_source_stats = []
        for title, feed, site in SOURCES:
            src = db.query(Source).filter(Source.feed_url == feed).first()
            if not src:
                src = Source(title=title, feed_url=feed, site_url=site, is_active=True)
                db.add(src)
                db.flush()
                db.commit()
            result["sources"].append({"id": src.id, "title": src.title, "feed_url": src.feed_url})

            count = 0
            try:
                count = collector.collect_source(src)
            except Exception as e:
                per_source_stats.append({"source_id": src.id, "collected": 0, "error": str(e)})
            else:
                per_source_stats.append({"source_id": src.id, "collected": count})
                result["collection"]["total"] += max(0, count)

        result["collection"]["per_source"] = per_source_stats

        # Query recent items across these sources
        since = datetime.now(timezone.utc) - timedelta(days=result["window_days"])
        src_ids = [s["id"] for s in result["sources"]]
        items = (
            db.query(Item)
            .filter(Item.source_id.in_(src_ids))
            .filter(Item.published_at != None)  # noqa: E711
            .filter(Item.published_at >= since)
            .order_by(Item.published_at.desc())
            .limit(len(src_ids) * result["params"]["max_items_per_source"])
            .all()
        )
        result["grouping"]["candidates"] = len(items)

        # Dedup/group
        d = Deduplicator(
            db,
            similarity_threshold=result["params"]["similarity_threshold"],
            lookback_days=result["params"]["lookback_days"],
        )

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
                        "source_id": it.source_id,
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
        print(f"[TEST RESULTS] Collected(total): {result['collection']['total']}")
        print(f"[TEST RESULTS] Candidates: {result['grouping']['candidates']}, Grouped: {result['grouping']['grouped']}")
        db.close()


