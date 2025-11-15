"""Deactivate a source by title (set is_active = False).

Usage:
  poetry run python -m backend.scripts.deactivate_source --title "DeepMind Blog"
"""
import argparse

from backend.app.core.database import SessionLocal
from backend.app.models.source import Source


def main(title: str):
    db = SessionLocal()
    try:
        src = db.query(Source).filter(Source.title == title).first()
        if not src:
            print(f"[DeactivateSource] Not found: {title}")
            return
        if src.is_active:
            src.is_active = False
            db.add(src)
            db.commit()
            print(f"[DeactivateSource] Deactivated: {title}")
        else:
            print(f"[DeactivateSource] Already inactive: {title}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True, help="Exact source title to deactivate")
    args = parser.parse_args()
    main(args.title)


