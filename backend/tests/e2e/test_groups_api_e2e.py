"""E2E for groups API with backfill & incremental; save JSON results."""
from datetime import datetime, timezone, timedelta, date
from pathlib import Path
import json
import pytest

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.services.group_backfill import GroupBackfill


@pytest.mark.slow
@pytest.mark.e2e_real_data
def test_groups_api_e2e_backfill_and_incremental():
    client = TestClient(app)
    db = SessionLocal()
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = results_dir / f"groups_api_e2e_{ts}.json"

    result = {
        "test_name": "test_groups_api_e2e_backfill_and_incremental",
        "timestamp": ts,
        "backfill": {"processed": 0, "window_days": 21},
        "incremental": {"processed": 0},
        "api": {"new": None, "incremental": None},
        "status": "running",
    }

    try:
        # Backfill for [today-21d, today]
        ref = datetime.now(timezone.utc).date()
        backfill = GroupBackfill(db)
        processed = backfill.run_backfill(ref, days=21)
        result["backfill"]["processed"] = processed

        # Incremental for last 24h
        since_dt = datetime.now(timezone.utc) - timedelta(days=1)
        inc_processed = backfill.run_incremental(since_dt)
        result["incremental"]["processed"] = inc_processed

        # API: new groups since today (likely small) and incremental since yesterday
        since_today = ref.strftime("%Y-%m-%d")
        r1 = client.get(f"/api/groups?since={since_today}&kind=new&page=1&page_size=10")
        result["api"]["new"] = r1.json() if r1.status_code == 200 else {"error": r1.text, "status": r1.status_code}

        since_yesterday = (ref - timedelta(days=1)).strftime("%Y-%m-%d")
        r2 = client.get(f"/api/groups?since={since_yesterday}&kind=incremental&page=1&page_size=10")
        result["api"]["incremental"] = r2.json() if r2.status_code == 200 else {"error": r2.text, "status": r2.status_code}

        result["status"] = "passed"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        raise
    finally:
        with open(out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        db.close()
        print(f"\n[TEST RESULTS] Saved to: {out}")
        print(f"[TEST RESULTS] Status: {result['status']}")
        if result.get("api"):
            for k, v in result["api"].items():
                try:
                    print(f"[TEST RESULTS] API {k}: total={v.get('total')}")
                except Exception:
                    pass


