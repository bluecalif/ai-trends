"""Run grouping backfill for [REF_DATE-21d, REF_DATE] and incremental for last 24h.

Run:
  poetry run python -m backend.scripts.run_backfill
"""
from datetime import datetime, timezone, timedelta

from backend.app.core.database import SessionLocal
from backend.app.services.group_backfill import GroupBackfill
from backend.app.core.config import get_settings


def main():
    db = SessionLocal()
    try:
        settings = get_settings()
        print(f"[Backfill] DATABASE_URL={settings.DATABASE_URL}")
        ref = datetime.now(timezone.utc).date()
        svc = GroupBackfill(db)
        bf = svc.run_backfill(ref, days=21)
        inc = svc.run_incremental(datetime.now(timezone.utc) - timedelta(days=1))
        print(f"[Backfill] ref_date={ref} window_days=21 backfilled={bf}, incremental(last24h)={inc}")
    finally:
        db.close()


if __name__ == "__main__":
    main()


