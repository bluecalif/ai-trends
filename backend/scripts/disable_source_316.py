"""Disable source ID 316 that's causing feed parsing errors."""
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
            print(f"\n[Disable Source 316] Current status:")
            print(f"  Title: {source.title}")
            print(f"  Active: {source.is_active}")
            
            if source.is_active:
                source.is_active = False
                db.commit()
                print(f"\n[Disable Source 316] Source disabled successfully")
            else:
                print(f"\n[Disable Source 316] Source is already disabled")
        else:
            print("\n[Disable Source 316] Source not found")
    except Exception as e:
        db.rollback()
        print(f"\n[Disable Source 316] Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()

