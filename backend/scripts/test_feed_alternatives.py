"""Test alternative RSS feed URLs for problematic sources and optionally update them.

Run:
  poetry run python -m backend.scripts.test_feed_alternatives --apply
If --apply is omitted, it runs in dry-run mode and does not update DB.
"""
import argparse
from typing import Dict, List

from backend.app.core.database import SessionLocal
from backend.app.models.source import Source
from backend.app.services.rss_collector import RSSCollector


ALTERNATIVES: Dict[str, List[str]] = {
    # title -> candidate feed URLs (order matters)
    "DeepMind Blog": [
        "https://deepmind.google/discover/blog/feed/",       # without 'basic'
        "https://deepmind.google/discover/rss/",             # site-wide RSS
        "https://deepmind.google/discover/blog/rss/",        # blog rss
        "https://deepmind.google/discover/blog/atom.xml",    # atom fallback
        "https://deepmind.google/discover/rss.xml",          # generic rss.xml
        "https://deepmind.google/rss",                       # generic rss
        "https://deepmind.com/blog/feed",                    # legacy domain
    ],
    "IEEE Spectrum – AI": [
        "https://spectrum.ieee.org/rss/fulltext",            # full site fulltext feed
        "https://spectrum.ieee.org/topic/artificial-intelligence/rss",  # topic feed
    ],
    "OpenAI News": [
        "https://openai.com/blog/rss/",
        "https://openai.com/blog/rss.xml",
    ],
}


def main(apply: bool = False):
    db = SessionLocal()
    try:
        collector = RSSCollector(db)
        for title, candidates in ALTERNATIVES.items():
            src = db.query(Source).filter(Source.title == title).first()
            if not src:
                print(f"[AltFeed] Source not found: {title}")
                continue
            print(f"\n[AltFeed] Testing alternatives for: {title} (current={src.feed_url})")
            chosen = None
            for url in candidates:
                try:
                    entries = collector.parse_feed(url)
                    print(f"[AltFeed] OK: {url} -> entries={len(entries)}")
                    chosen = url
                    break
                except Exception as e:
                    print(f"[AltFeed] FAIL: {url} -> {e}")
            if chosen and apply:
                print(f"[AltFeed] Applying update: {src.feed_url} -> {chosen}")
                src.feed_url = chosen
                db.add(src)
                db.commit()
            elif chosen:
                print(f"[AltFeed] Candidate works (dry-run): {chosen}")
            else:
                print(f"[AltFeed] No working alternative found for {title}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply working alternative to DB")
    args = parser.parse_args()
    main(apply=args.apply)


