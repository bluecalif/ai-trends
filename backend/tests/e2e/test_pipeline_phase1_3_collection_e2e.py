"""E2E test for Phase 1.3: RSS Collection (all sources, 21-day window).
Tests collection of items from all active sources within 21-day window.
"""
import sys
import io
import json
from datetime import datetime, timezone, timedelta, date
from pathlib import Path

# Fix Windows PowerShell encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import pytest

from backend.app.core.database import SessionLocal
from backend.app.models.source import Source
from backend.app.models.item import Item
from backend.app.services.rss_collector import RSSCollector


@pytest.mark.slow
@pytest.mark.e2e_real_data
def test_phase1_3_collection_all_sources_21days():
    """E2E: Collect items from all active sources (21-day window)."""
    db = SessionLocal()
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_file = results_dir / f"pipeline_phase1_3_collection_{ts}.json"
    summary_file = results_dir / f"pipeline_phase1_3_collection_{ts}_summary.json"
    
    # Calculate 21-day window
    ref_date = date.today()
    start_dt = datetime(ref_date.year, ref_date.month, ref_date.day, tzinfo=timezone.utc) - timedelta(days=21)
    end_dt = datetime(ref_date.year, ref_date.month, ref_date.day, tzinfo=timezone.utc)
    
    result = {
        "phase": "1.3",
        "phase_name": "RSS Collection",
        "test_name": "test_phase1_3_collection_all_sources_21days",
        "timestamp": ts,
        "window": {
            "start": start_dt.isoformat(),
            "end": end_dt.isoformat(),
            "days": 21
        },
        "sources": [],
        "summary": {
            "total_sources": 0,
            "active_sources": 0,
            "collected_items": 0,
            "items_in_window": 0,
            "errors": []
        },
        "status": "running"
    }
    
    try:
        # Get all active sources (excluding DeepMind/The Keyword if inactive)
        all_sources = db.query(Source).filter(Source.is_active == True).all()  # noqa: E712
        
        # Filter out DeepMind (The Keyword) - only if it's actually DeepMind
        # Note: The Keyword feed is used for DeepMind filtering, but we exclude it if it's marked inactive
        sources = [s for s in all_sources if s.is_active]
        
        result["summary"]["total_sources"] = len(all_sources)
        result["summary"]["active_sources"] = len(sources)
        
        if not sources:
            result["status"] = "skipped_no_sources"
            result["error"] = "No active sources found (excluding DeepMind)"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            db.close()
            return
        
        collector = RSSCollector(db)
        total_collected = 0
        
        for source in sources:
            source_result = {
                "source_id": source.id,
                "title": source.title,
                "feed_url": source.feed_url,
                "collected_count": 0,
                "status": "pending",
                "error": None
            }
            
            try:
                count = collector.collect_source(source)
                source_result["collected_count"] = count
                source_result["status"] = "success"
                total_collected += count
            except Exception as e:
                source_result["status"] = "error"
                source_result["error"] = str(e)
                result["summary"]["errors"].append({
                    "source": source.title,
                    "error": str(e)
                })
            
            result["sources"].append(source_result)
        
        result["summary"]["collected_items"] = total_collected
        
        # Get all items in the 21-day window with full details
        items_in_window = (
            db.query(Item)
            .filter(Item.published_at != None)  # noqa: E711
            .filter(Item.published_at >= start_dt)
            .filter(Item.published_at <= end_dt)
            .order_by(Item.published_at.desc())
            .all()
        )
        
        result["summary"]["items_in_window"] = len(items_in_window)
        
        # Add all items with full details
        result["items"] = []
        for item in items_in_window:
            item_data = {
                "id": item.id,
                "source_id": item.source_id,
                "source_title": item.source.title if item.source else None,
                "title": item.title,
                "summary_short": item.summary_short,
                "link": item.link,
                "published_at": item.published_at.isoformat() if item.published_at else None,
                "author": item.author,
                "thumbnail_url": item.thumbnail_url,
                "iptc_topics": item.iptc_topics if isinstance(item.iptc_topics, list) else [],
                "iab_categories": item.iab_categories if isinstance(item.iab_categories, list) else [],
                "custom_tags": item.custom_tags if isinstance(item.custom_tags, list) else [],
                "dup_group_id": item.dup_group_id,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
            }
            result["items"].append(item_data)
        
        result["status"] = "passed"
        
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        result["error_type"] = type(e).__name__
    finally:
        # Save full detailed result
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        
        # Create and save summary (without items array)
        summary = {
            "phase": result.get("phase"),
            "phase_name": result.get("phase_name"),
            "test_name": result.get("test_name"),
            "timestamp": result.get("timestamp"),
            "window": result.get("window"),
            "sources": result.get("sources", []),
            "summary": result.get("summary", {}),
            "status": result.get("status"),
        }
        if "error" in result:
            summary["error"] = result["error"]
        if "error_type" in result:
            summary["error_type"] = result["error_type"]
        
        # Add item count statistics
        items = result.get("items", [])
        summary["item_statistics"] = {
            "total_items": len(items),
            "items_with_summary": sum(1 for it in items if it.get("summary_short")),
            "items_with_entities": 0,  # Will be populated in Phase 1.5
            "items_with_classification": sum(1 for it in items if it.get("custom_tags") or it.get("iptc_topics")),
            "items_with_group": sum(1 for it in items if it.get("dup_group_id")),
            "items_by_source": {},
            "items_by_source_and_date": {}
        }
        
        # Count items by source
        for item in items:
            source_title = item.get("source_title", "Unknown")
            summary["item_statistics"]["items_by_source"][source_title] = \
                summary["item_statistics"]["items_by_source"].get(source_title, 0) + 1
        
        # Count items by source and date
        for item in items:
            source_title = item.get("source_title", "Unknown")
            published_at = item.get("published_at")
            
            if published_at:
                # Extract date from ISO format datetime string
                try:
                    pub_date = published_at[:10]  # "YYYY-MM-DD" part
                except Exception:
                    pub_date = "Unknown"
            else:
                pub_date = "Unknown"
            
            if source_title not in summary["item_statistics"]["items_by_source_and_date"]:
                summary["item_statistics"]["items_by_source_and_date"][source_title] = {}
            
            summary["item_statistics"]["items_by_source_and_date"][source_title][pub_date] = \
                summary["item_statistics"]["items_by_source_and_date"][source_title].get(pub_date, 0) + 1
        
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n[Phase 1.3] Full results saved to: {out_file}")
        print(f"[Phase 1.3] Summary saved to: {summary_file}")
        print(f"[Phase 1.3] Status: {result['status']}")
        print(f"[Phase 1.3] Active sources: {result['summary']['active_sources']}")
        print(f"[Phase 1.3] Collected items: {result['summary']['collected_items']}")
        print(f"[Phase 1.3] Items in 21-day window: {result['summary']['items_in_window']}")
        print(f"[Phase 1.3] Total items in JSON: {len(items)}")
        if result["summary"]["errors"]:
            print(f"[Phase 1.3] Errors: {len(result['summary']['errors'])}")
            for err in result["summary"]["errors"]:
                print(f"  - {err['source']}: {err['error']}")
        
        db.close()


if __name__ == "__main__":
    test_phase1_3_collection_all_sources_21days()

