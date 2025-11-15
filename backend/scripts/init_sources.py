"""Initialize PRD-defined RSS sources into the database (MVP mandatory).

Run from project root:
  poetry run python -m backend.scripts.init_sources
"""
from typing import List, Dict

from backend.app.core.config import get_settings

from backend.app.core.database import SessionLocal
from backend.app.models.source import Source


PRD_SOURCES: List[Dict[str, str]] = [
    {"title": "TechCrunch", "feed_url": "https://techcrunch.com/feed/", "site_url": "https://techcrunch.com"},
    {"title": "VentureBeat – AI", "feed_url": "https://venturebeat.com/category/ai/feed/", "site_url": "https://venturebeat.com"},
    {"title": "MarkTechPost", "feed_url": "https://www.marktechpost.com/feed/", "site_url": "https://www.marktechpost.com"},
    {"title": "WIRED (All)", "feed_url": "https://www.wired.com/feed/rss", "site_url": "https://www.wired.com"},
    {"title": "The Verge (All)", "feed_url": "https://www.theverge.com/rss/index.xml", "site_url": "https://www.theverge.com"},
    {"title": "IEEE Spectrum – AI", "feed_url": "https://spectrum.ieee.org/rss/fulltext", "site_url": "https://spectrum.ieee.org"},
    {"title": "AITimes", "feed_url": "https://www.aitimes.com/rss/allArticle.xml", "site_url": "https://www.aitimes.com"},
    {"title": "arXiv – cs.AI", "feed_url": "http://export.arxiv.org/rss/cs.AI", "site_url": "https://arxiv.org/list/cs.AI/recent"},
    {"title": "OpenAI News", "feed_url": "https://openai.com/blog/rss.xml", "site_url": "https://openai.com"},
    {"title": "The Keyword (Google DeepMind filtered)", "feed_url": "https://blog.google/feed/", "site_url": "https://blog.google/technology/google-deepmind/"},
]


def main():
    db = SessionLocal()
    try:
        settings = get_settings()
        db_url = settings.DATABASE_URL
        print(f"[InitSources] DATABASE_URL={db_url}")
        created = 0
        skipped = 0
        for s in PRD_SOURCES:
            exists = db.query(Source).filter(Source.feed_url == s["feed_url"]).first()
            if exists:
                skipped += 1
                continue
            src = Source(
                title=s["title"],
                feed_url=s["feed_url"],
                site_url=s.get("site_url"),
                is_active=True,
            )
            db.add(src)
            created += 1
        db.commit()
        total = db.query(Source).count()
        active = db.query(Source).filter(Source.is_active == True).count()  # noqa: E712
        print(f"[InitSources] created={created} skipped={skipped} total={created+skipped}")
        print(f"[InitSources] sources total={total}, active={active}")
    finally:
        db.close()


if __name__ == "__main__":
    main()


