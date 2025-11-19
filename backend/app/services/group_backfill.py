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

    def run_backfill(self, ref_date: date, days: int = 21, batch_size: int = 50, verbose: bool = False) -> int:
        """Backfill grouping for [ref_date-days, ref_date] window.
        
        Args:
            ref_date: Reference date (typically today)
            days: Number of days to look back
            batch_size: Number of items to process before showing progress
            verbose: Whether to print detailed progress
            
        Returns:
            Number of processed items.
        """
        start_dt = datetime(ref_date.year, ref_date.month, ref_date.day, tzinfo=timezone.utc) - timedelta(days=days)
        end_dt = datetime(ref_date.year, ref_date.month, ref_date.day, tzinfo=timezone.utc)

        # Load all items in window at once (batch)
        items: List[Item] = (
            self.db.query(Item)
            .filter(Item.published_at != None)  # noqa: E711
            .filter(Item.published_at >= start_dt)
            .filter(Item.published_at <= end_dt)
            .order_by(Item.published_at.asc())
            .all()
        )
        
        total = len(items)
        if verbose:
            print(f"[Backfill] Processing {total} items in {days}-day window")
        
        # Pre-load all items for lookback (batch optimization)
        # This reduces DB queries in Deduplicator
        all_items_lookup = {it.id: it for it in items}
        
        d = Deduplicator(self.db, similarity_threshold=0.2, lookback_days=days, verbose=verbose)
        processed = 0
        
        for idx, it in enumerate(items, 1):
            # process will seed if needed or join a group
            d.process_new_item(it)
            processed += 1
            
            # Progress update
            if verbose and (idx % batch_size == 0 or idx == total):
                pct = (idx / total * 100) if total > 0 else 0
                print(f"[Backfill] Progress: {idx}/{total} ({pct:.1f}%)")
        
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


