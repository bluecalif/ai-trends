"""Check field status for items in database."""
import sys
import io

# Fix Windows PowerShell encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from sqlalchemy import func
from backend.app.core.database import SessionLocal
from backend.app.models.item import Item

def main():
    db = SessionLocal()
    try:
        # Total items
        total = db.query(Item).count()
        
        # Items with field
        with_field = db.query(Item).filter(Item.field.isnot(None)).count()
        
        # Items without field
        without_field = db.query(Item).filter(Item.field.is_(None)).count()
        
        # Count by field value
        field_counts = (
            db.query(Item.field, func.count(Item.id).label('count'))
            .filter(Item.field.isnot(None))
            .group_by(Item.field)
            .order_by(func.count(Item.id).desc())
            .all()
        )
        
        print(f"\n[Field Status] ===== Summary =====")
        print(f"Total items: {total}")
        print(f"Items with field: {with_field}")
        print(f"Items without field: {without_field}")
        print()
        
        if field_counts:
            print(f"[Field Status] ===== Items by Field =====")
            for field, count in field_counts:
                print(f"  {field}: {count}")
        else:
            print(f"[Field Status] No items with field values")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()

