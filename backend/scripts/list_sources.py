"""List all sources from database.

Run:
  poetry run python -m backend.scripts.list_sources
"""
import sys
import io

# Fix Windows PowerShell encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from backend.app.core.database import SessionLocal
from backend.app.models.source import Source


def main():
    db = SessionLocal()
    try:
        all_sources = db.query(Source).order_by(Source.title).all()
        print(f"[ListSources] Total sources: {len(all_sources)}\n")
        
        for src in all_sources:
            status = "ACTIVE" if src.is_active else "INACTIVE"
            print(f"[{status}] ID={src.id:3d} | {src.title:40s} | {src.feed_url}")
        
        print("\n[Summary]")
        active = db.query(Source).filter(Source.is_active == True).count()  # noqa: E712
        inactive = db.query(Source).filter(Source.is_active == False).count()  # noqa: E712
        print(f"  Active: {active}")
        print(f"  Inactive: {inactive}")
        print(f"  Total: {len(all_sources)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

