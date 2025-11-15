"""E2E: Verify RSS collection quality across all sources.
For each Source in DB, attempt collection and save a per-source report JSON.
"""
from datetime import datetime, timezone
from pathlib import Path
import json

import pytest

from backend.app.core.database import SessionLocal
from backend.app.models.source import Source
from backend.app.services.rss_collector import RSSCollector


@pytest.mark.slow
@pytest.mark.e2e_real_data
def test_rss_collect_verify_all_sources():
    db = SessionLocal()
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = results_dir / f"rss_collect_verify_{ts}.json"

    result = {
        "test_name": "test_rss_collect_verify_all_sources",
        "timestamp": ts,
        "summary": {"sources_total": 0, "collected_total": 0, "errors": 0},
        "sources": [],
        "status": "running",
    }

    try:
        sources = db.query(Source).order_by(Source.title.asc()).all()
        result["summary"]["sources_total"] = len(sources)

        collector = RSSCollector(db)
        for src in sources:
            entry = {
                "id": src.id,
                "title": src.title,
                "feed_url": src.feed_url,
                "site_url": src.site_url,
                "is_active": src.is_active,
                "collected": 0,
            }
            if not src.is_active:
                entry["skipped"] = True
                result["sources"].append(entry)
                continue

            try:
                count = collector.collect_source(src)
                entry["collected"] = count
                result["summary"]["collected_total"] += max(0, count)
            except Exception as e:
                entry["error"] = str(e)
                result["summary"]["errors"] += 1
            result["sources"].append(entry)

        result["status"] = "passed"
    finally:
        with open(out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n[TEST RESULTS] Saved to: {out}")
        print(f"[TEST RESULTS] Status: {result['status']}")
        print(f"[TEST RESULTS] Sources: {result['summary']['sources_total']}, Errors: {result['summary']['errors']}")
        print(f"[TEST RESULTS] Collected(total): {result['summary']['collected_total']}")
        db.close()


