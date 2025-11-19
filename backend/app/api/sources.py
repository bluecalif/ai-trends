"""Sources API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.source import Source
from backend.app.schemas.source import SourceResponse, SourceCreate, SourceUpdate

router = APIRouter(prefix="/api/sources", tags=["sources"])


@router.get("", response_model=List[SourceResponse])
async def get_sources(
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """소스 목록 조회.
    
    Args:
        is_active: 활성 상태 필터 (None이면 전체)
        db: Database session
        
    Returns:
        List[SourceResponse]: 소스 목록
    """
    query = db.query(Source)
    if is_active is not None:
        query = query.filter(Source.is_active == is_active)
    sources = query.order_by(Source.title).all()
    return sources


@router.post("", response_model=SourceResponse, status_code=201)
async def create_source(
    source_data: SourceCreate,
    db: Session = Depends(get_db)
):
    """소스 추가.
    
    Args:
        source_data: 소스 생성 데이터
        db: Database session
        
    Returns:
        SourceResponse: 생성된 소스
        
    Raises:
        HTTPException: feed_url이 이미 존재할 때
    """
    # 중복 체크
    existing = db.query(Source).filter(Source.feed_url == source_data.feed_url).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Source with feed_url '{source_data.feed_url}' already exists")
    
    source = Source(**source_data.dict())
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: int,
    db: Session = Depends(get_db)
):
    """소스 상세 조회.
    
    Args:
        source_id: 소스 ID
        db: Database session
        
    Returns:
        SourceResponse: 소스 상세 정보
        
    Raises:
        HTTPException: 소스를 찾을 수 없을 때
    """
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.put("/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: int,
    source_data: SourceUpdate,
    db: Session = Depends(get_db)
):
    """소스 수정.
    
    Args:
        source_id: 소스 ID
        source_data: 수정할 데이터
        db: Database session
        
    Returns:
        SourceResponse: 수정된 소스
        
    Raises:
        HTTPException: 소스를 찾을 수 없을 때
    """
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    # feed_url 변경 시 중복 체크
    if source_data.feed_url and source_data.feed_url != source.feed_url:
        existing = db.query(Source).filter(Source.feed_url == source_data.feed_url).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Source with feed_url '{source_data.feed_url}' already exists")
    
    # 업데이트
    update_data = source_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(source, key, value)
    
    db.commit()
    db.refresh(source)
    return source


@router.delete("/{source_id}", status_code=204)
async def delete_source(
    source_id: int,
    db: Session = Depends(get_db)
):
    """소스 삭제.
    
    Args:
        source_id: 소스 ID
        db: Database session
        
    Raises:
        HTTPException: 소스를 찾을 수 없을 때
    """
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    db.delete(source)
    db.commit()
    return None

