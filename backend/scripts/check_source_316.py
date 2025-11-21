"""Check source ID 316 that's causing feed parsing errors."""
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
        source = db.query(Source).filter(Source.id == 316).first()
        if source:
            print(f"\n[Source 316] Found:")
            print(f"  Title: {source.title}")
            print(f"  Feed URL: {source.feed_url}")
            print(f"  Active: {source.is_active}")
            print(f"  Category: {source.category}")
        else:
            print("\n[Source 316] Not found in database")
    finally:
        db.close()

if __name__ == "__main__":
    main()

