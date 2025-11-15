from __future__ import annotations
from datetime import datetime, timedelta, timezone, date
from typing import Optional, List

from sqlalchemy.orm import Session

from backend.app.models.item import Item
from backend.app.models.dup_group_meta import DupGroupMeta
from backend.app.services.deduplicator import Deduplicator


class GroupBackfill:
    def __init__(self, db: Session):
        self.db = db

    def run_backfill(self, ref_date: date, days: int = 21) -> int:
        """Backfill grouping for [ref_date-days, ref_date] window.
        Returns number of processed items.
        """
        start_dt = datetime(ref_date.year, ref_date.month, ref_date.day, tzinfo=timezone.utc) - timedelta(days=days)
        end_dt = datetime(ref_date.year, ref_date.month, ref_date.day, tzinfo=timezone.utc)

        items: List[Item] = (
            self.db.query(Item)
            .filter(Item.published_at != None)  # noqa: E711
            .filter(Item.published_at >= start_dt)
            .filter(Item.published_at <= end_dt)
            .order_by(Item.published_at.asc())
            .all()
        )
        d = Deduplicator(self.db, similarity_threshold=0.2, lookback_days=days)
        processed = 0
        for it in items:
            # process will seed if needed or join a group
            d.process_new_item(it)
            processed += 1
        return processed

    def run_incremental(self, since_dt: datetime) -> int:
        """Process items published after since_dt (incremental)."""
        items: List[Item] = (
            self.db.query(Item)
            .filter(Item.published_at != None)  # noqa: E711
            .filter(Item.published_at > since_dt)
            .order_by(Item.published_at.asc())
            .all()
        )
        d = Deduplicator(self.db, similarity_threshold=0.2, lookback_days=21)
        processed = 0
        for it in items:
            d.process_new_item(it)
            processed += 1
        return processed


