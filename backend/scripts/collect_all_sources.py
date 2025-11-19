"""Collect all active RSS sources once.

Run:
  poetry run python -m backend.scripts.collect_all_sources
"""
import sys
import io

# Fix Windows PowerShell encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from backend.app.core.database import SessionLocal
from backend.app.models.source import Source
from backend.app.services.rss_collector import RSSCollector
from backend.app.core.config import get_settings


def main():
    db = SessionLocal()
    try:
        settings = get_settings()
        print(f"[CollectAll] DATABASE_URL={settings.DATABASE_URL}")
        collector = RSSCollector(db)
        sources = db.query(Source).filter(Source.is_active == True).all()  # noqa: E712
        source_titles = [s.title for s in sources]
        print(f"[CollectAll] active_sources={len(sources)} -> {source_titles}")
        total = 0
        for src in sources:
            try:
                cnt = collector.collect_source(src)
                print(f"[CollectAll] {src.title}: +{cnt}")
                total += max(0, cnt)
            except Exception as e:
                print(f"[CollectAll] {src.title}: ERROR {e}")
        print(f"[CollectAll] Done. total_new={total}, sources={len(sources)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()


