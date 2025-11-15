"""RSS collection API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.services.rss_collector import RSSCollector
from backend.app.models.source import Source
from backend.app.schemas.rss import CollectResponse, CollectAllResponse

router = APIRouter(tags=["rss"])


@router.post("/collect/{source_id}", response_model=CollectResponse)
async def collect_source(
    source_id: int,
    db: Session = Depends(get_db)
):
    """Collect items from a specific source.
    
    Args:
        source_id: Source ID to collect from
        db: Database session
        
    Returns:
        Collection result with count of new items
        
    Raises:
        HTTPException: If source not found or collection fails
    """
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    if not source.is_active:
        raise HTTPException(status_code=400, detail="Source is not active")
    
    collector = RSSCollector(db)
    try:
        count = collector.collect_source(source)
        return CollectResponse(
            message=f"Collected {count} new items",
            source_id=source_id,
            count=count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Collection failed: {str(e)}")


@router.post("/collect-all", response_model=CollectAllResponse)
async def collect_all(db: Session = Depends(get_db)):
    """Collect items from all active sources.
    
    Args:
        db: Database session
        
    Returns:
        Collection results for all sources
    """
    collector = RSSCollector(db)
    sources = db.query(Source).filter(Source.is_active == True).all()
    
    results = []
    for source in sources:
        try:
            count = collector.collect_source(source)
            results.append({
                "source_id": source.id,
                "source_title": source.title,
                "count": count,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "source_id": source.id,
                "source_title": source.title,
                "count": 0,
                "status": "error",
                "error": str(e)
            })
    
    return CollectAllResponse(results=results)

