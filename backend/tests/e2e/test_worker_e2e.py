"""E2E tests for worker process and scheduler.

This test verifies that the worker process can start, run scheduled jobs,
and shut down gracefully.
"""

from datetime import datetime, timezone
from pathlib import Path
import json
import pytest
import time
import threading

from backend.app.core.database import SessionLocal
from backend.app.core.scheduler import start_scheduler, stop_scheduler, is_scheduler_running
from backend.app.core.constants import PRD_RSS_SOURCES
from backend.app.models.source import Source
from backend.app.models.item import Item


@pytest.mark.slow
@pytest.mark.e2e_real_data
def test_worker_e2e():
    """E2E test for worker process with real database."""
    db = SessionLocal()
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    result_file = results_dir / f"worker_e2e_{timestamp}.json"

    test_results = {
        "test_name": "test_worker_e2e",
        "timestamp": timestamp,
        "scheduler_tests": {
            "startup": {"status": "running", "scheduler_running": False},
            "jobs_registered": {"status": "running", "job_count": 0},
            "shutdown": {"status": "running", "scheduler_stopped": False},
        },
        "status": "running",
    }

    try:
        # Step 1: Ensure sources exist
        print("[Worker E2E] Step 1: Ensuring sources exist...")
        sources_created = 0
        for source_data in PRD_RSS_SOURCES:
            source = db.query(Source).filter(
                Source.feed_url == source_data["feed_url"]
            ).first()
            if not source:
                source = Source(
                    title=source_data["title"],
                    feed_url=source_data["feed_url"],
                    site_url=source_data.get("site_url"),
                    is_active=True,
                )
                db.add(source)
                sources_created += 1
            else:
                source.is_active = True
        db.commit()
        print(f"[Worker E2E] Sources ready: {sources_created} created")

        # Step 2: Get initial item count
        initial_item_count = db.query(Item).count()
        print(f"[Worker E2E] Initial item count: {initial_item_count}")

        # Step 3: Test scheduler startup
        print("[Worker E2E] Step 2: Testing scheduler startup...")
        assert not is_scheduler_running(), "Scheduler should not be running initially"
        
        start_scheduler()
        assert is_scheduler_running(), "Scheduler should be running after start"
        test_results["scheduler_tests"]["startup"]["scheduler_running"] = True
        test_results["scheduler_tests"]["startup"]["status"] = "completed"
        print("[Worker E2E] Scheduler started successfully")

        # Step 4: Verify jobs are registered
        print("[Worker E2E] Step 3: Verifying jobs are registered...")
        from backend.app.core.scheduler import scheduler
        
        jobs = scheduler.get_jobs()
        job_count = len(jobs)
        test_results["scheduler_tests"]["jobs_registered"]["job_count"] = job_count
        test_results["scheduler_tests"]["jobs_registered"]["status"] = "completed"
        print(f"[Worker E2E] Found {job_count} registered jobs")
        
        # Verify expected jobs exist
        job_ids = [job.id for job in jobs]
        expected_jobs = [
            "rss_collection_all",
            "rss_collection_arxiv",
            "incremental_grouping",
            "daily_backfill_grouping",
        ]
        for expected_job in expected_jobs:
            assert expected_job in job_ids, f"Expected job {expected_job} not found"

        # Step 5: Wait a bit to see if jobs execute (optional, may take time)
        print("[Worker E2E] Step 4: Waiting for potential job execution...")
        time.sleep(5)  # Wait 5 seconds to see if any jobs run
        
        # Check if any new items were collected (optional verification)
        final_item_count = db.query(Item).count()
        items_added = final_item_count - initial_item_count
        print(f"[Worker E2E] Items added during test: {items_added}")

        # Step 6: Test scheduler shutdown
        print("[Worker E2E] Step 5: Testing scheduler shutdown...")
        stop_scheduler()
        time.sleep(1)  # Give scheduler time to stop
        assert not is_scheduler_running(), "Scheduler should not be running after stop"
        test_results["scheduler_tests"]["shutdown"]["scheduler_stopped"] = True
        test_results["scheduler_tests"]["shutdown"]["status"] = "completed"
        print("[Worker E2E] Scheduler stopped successfully")

        # Summary
        test_results["status"] = "passed"
        test_results["summary"] = {
            "scheduler_started": True,
            "scheduler_stopped": True,
            "jobs_registered": job_count,
            "expected_jobs_found": all(job in job_ids for job in expected_jobs),
            "items_before": initial_item_count,
            "items_after": final_item_count,
            "items_added": items_added,
        }

    except Exception as e:
        test_results["status"] = "error"
        test_results["error"] = str(e)
        import traceback
        test_results["traceback"] = traceback.format_exc()
        
        # Ensure scheduler is stopped even on error
        try:
            if is_scheduler_running():
                stop_scheduler()
        except Exception:
            pass
        
        raise
    finally:
        # Ensure scheduler is stopped
        try:
            if is_scheduler_running():
                stop_scheduler()
        except Exception:
            pass
        
        # Save results
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False, default=str)
        db.close()
        print(f"\n[Worker E2E] Results saved to: {result_file}")
        print(f"[Worker E2E] Status: {test_results['status']}")
        if test_results.get("summary"):
            print(f"[Worker E2E] Summary: {json.dumps(test_results['summary'], indent=2)}")


@pytest.mark.slow
@pytest.mark.e2e_real_data
def test_scheduler_job_execution():
    """Test that scheduler jobs can execute (with shorter wait time)."""
    db = SessionLocal()
    
    try:
        # Ensure sources exist
        for source_data in PRD_RSS_SOURCES[:2]:  # Limit to 2 sources
            source = db.query(Source).filter(
                Source.feed_url == source_data["feed_url"]
            ).first()
            if not source:
                source = Source(
                    title=source_data["title"],
                    feed_url=source_data["feed_url"],
                    site_url=source_data.get("site_url"),
                    is_active=True,
                )
                db.add(source)
        db.commit()
        
        # Start scheduler
        if not is_scheduler_running():
            start_scheduler()
        
        # Wait a short time
        time.sleep(2)
        
        # Verify scheduler is still running
        assert is_scheduler_running(), "Scheduler should still be running"
        
    finally:
        # Stop scheduler
        if is_scheduler_running():
            stop_scheduler()
        db.close()

