"""Items API endpoints."""
from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from sqlalchemy.dialects.postgresql import JSONB

from backend.app.core.database import get_db
from backend.app.core.constants import FIELDS, CUSTOM_TAGS
from backend.app.models.item import Item
from backend.app.schemas.item import ItemResponse, ItemListResponse

router = APIRouter(prefix="/api/items", tags=["items"])


@router.get("", response_model=ItemListResponse)
async def get_items(
    field: Optional[str] = Query(None, description="분야 필터 (research, industry, infra, policy, funding)"),
    custom_tag: Optional[str] = Query(None, description="커스텀 태그 필터"),
    date_from: Optional[date] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="종료 날짜 (YYYY-MM-DD)"),
    source_id: Optional[int] = Query(None, description="소스 ID 필터"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    order_by: str = Query("published_at", description="정렬 필드 (published_at, created_at)"),
    order_desc: bool = Query(True, description="내림차순 정렬 여부"),
    db: Session = Depends(get_db)
):
    """뉴스 아이템 목록 조회 (필터링 및 페이지네이션).
    
    Args:
        field: 분야 필터 (research, industry, infra, policy, funding)
        custom_tag: 커스텀 태그 필터
        date_from: 시작 날짜
        date_to: 종료 날짜
        source_id: 소스 ID 필터
        page: 페이지 번호
        page_size: 페이지 크기
        order_by: 정렬 필드
        order_desc: 내림차순 정렬 여부
        db: Database session
        
    Returns:
        ItemListResponse: 아이템 목록 및 페이지네이션 정보
    """
    # 필터 검증
    if field and field not in FIELDS:
        raise HTTPException(status_code=400, detail=f"Invalid field: {field}. Valid values: {', '.join(FIELDS)}")
    if custom_tag and custom_tag not in CUSTOM_TAGS:
        raise HTTPException(status_code=400, detail=f"Invalid custom_tag: {custom_tag}. Valid values: {', '.join(CUSTOM_TAGS)}")
    
    # 기본 쿼리
    query = db.query(Item)
    
    # 필터 적용
    if field:
        # field는 현재 Item 모델에 없지만, 향후 추가될 수 있으므로 주석 처리
        # query = query.filter(Item.field == field)
        pass
    
    if custom_tag:
        # JSON 배열에 특정 태그 포함 여부 (PostgreSQL JSONB @> 연산자 사용)
        # custom_tags가 ["agents", "world_models"] 형태의 배열일 때, ["agents"]를 포함하는지 확인
        # JSON 타입을 JSONB로 캐스팅하여 @> 연산자 사용
        from sqlalchemy import cast
        query = query.filter(cast(Item.custom_tags, JSONB).op('@>')([custom_tag]))
    
    if date_from:
        query = query.filter(Item.published_at >= datetime.combine(date_from, datetime.min.time()))
    
    if date_to:
        query = query.filter(Item.published_at <= datetime.combine(date_to, datetime.max.time()))
    
    if source_id:
        query = query.filter(Item.source_id == source_id)
    
    # 정렬
    if order_by == "published_at":
        order_column = Item.published_at
    elif order_by == "created_at":
        order_column = Item.created_at
    else:
        raise HTTPException(status_code=400, detail=f"Invalid order_by: {order_by}. Valid values: published_at, created_at")
    
    if order_desc:
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column.asc())
    
    # 페이지네이션
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return ItemListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """아이템 상세 조회.
    
    Args:
        item_id: 아이템 ID
        db: Database session
        
    Returns:
        ItemResponse: 아이템 상세 정보
        
    Raises:
        HTTPException: 아이템을 찾을 수 없을 때
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.get("/group/{dup_group_id}", response_model=List[ItemResponse])
async def get_item_group(
    dup_group_id: int,
    db: Session = Depends(get_db)
):
    """사건 그룹 타임라인 조회.
    
    Args:
        dup_group_id: 중복 그룹 ID
        db: Database session
        
    Returns:
        List[ItemResponse]: 그룹에 속한 아이템 목록 (시간순 정렬)
    """
    items = (
        db.query(Item)
        .filter(Item.dup_group_id == dup_group_id)
        .order_by(Item.published_at.asc())
        .all()
    )
    return items

