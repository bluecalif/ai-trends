"""Initialize PRD-defined RSS sources into the database (MVP mandatory).

Run from project root:
  poetry run python -m backend.scripts.init_sources
"""
from backend.app.core.config import get_settings
from backend.app.core.constants import PRD_RSS_SOURCES
from backend.app.core.database import SessionLocal
from backend.app.models.source import Source


def main():
    db = SessionLocal()
    try:
        settings = get_settings()
        db_url = settings.DATABASE_URL
        print(f"[InitSources] DATABASE_URL={db_url}")
        created = 0
        skipped = 0
        for s in PRD_RSS_SOURCES:
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


