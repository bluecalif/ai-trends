"""Bookmarks API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import JSONB

from backend.app.core.database import get_db
from backend.app.models.bookmark import Bookmark
from backend.app.models.item import Item
from backend.app.schemas.bookmark import BookmarkResponse, BookmarkCreate, BookmarkUpdate

router = APIRouter(prefix="/api/bookmarks", tags=["bookmarks"])


@router.get("", response_model=List[BookmarkResponse])
async def get_bookmarks(
    tag: Optional[str] = Query(None, description="태그 필터"),
    db: Session = Depends(get_db)
):
    """북마크 목록 조회 (태그 필터링).
    
    Args:
        tag: 태그 필터
        db: Database session
        
    Returns:
        List[BookmarkResponse]: 북마크 목록
    """
    query = db.query(Bookmark)
    if tag:
        # JSON 배열에 특정 태그 포함 여부 (PostgreSQL JSONB @> 연산자 사용)
        # JSON 타입을 JSONB로 캐스팅하여 @> 연산자 사용
        from sqlalchemy import cast
        query = query.filter(cast(Bookmark.tags, JSONB).op('@>')([tag]))
    
    bookmarks = query.order_by(Bookmark.created_at.desc()).all()
    
    # Item 정보 포함
    result = []
    for bookmark in bookmarks:
        item = None
        if bookmark.item_id:
            item = db.query(Item).filter(Item.id == bookmark.item_id).first()
        
        result.append(BookmarkResponse(
            id=bookmark.id,
            item_id=bookmark.item_id,
            title=bookmark.title,
            tags=bookmark.tags or [],
            note=bookmark.note,
            created_at=bookmark.created_at,
            item_title=item.title if item else None,
            item_link=item.link if item else None,
            item_published_at=item.published_at if item else None,
        ))
    
    return result


@router.post("", response_model=BookmarkResponse, status_code=201)
async def create_bookmark(
    bookmark_data: BookmarkCreate,
    db: Session = Depends(get_db)
):
    """북마크 추가 (item_id 또는 link 기반, 중복 체크).
    
    Args:
        bookmark_data: 북마크 생성 데이터
        db: Database session
        
    Returns:
        BookmarkResponse: 생성된 북마크
        
    Raises:
        HTTPException: item_id 또는 link가 없을 때, 중복일 때
    """
    # item_id 또는 link 필수
    if not bookmark_data.item_id and not bookmark_data.link:
        raise HTTPException(status_code=400, detail="Either item_id or link must be provided")
    
    # item_id 또는 link로 Item 찾기
    item = None
    item_id = bookmark_data.item_id
    
    if item_id:
        # item_id로 Item 찾기
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
        
        # 중복 체크 (같은 item_id)
        existing = db.query(Bookmark).filter(Bookmark.item_id == item_id).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Bookmark for item_id {item_id} already exists")
        
        # Item 정보로 title 설정
        title = bookmark_data.title or item.title
    elif bookmark_data.link:
        # link로 Item 찾기
        item = db.query(Item).filter(Item.link == bookmark_data.link).first()
        if item:
            item_id = item.id
            
            # 중복 체크 (같은 item_id)
            existing = db.query(Bookmark).filter(Bookmark.item_id == item_id).first()
            if existing:
                raise HTTPException(status_code=400, detail=f"Bookmark for link '{bookmark_data.link}' already exists")
            
            # Item 정보로 title 설정
            title = bookmark_data.title or item.title
        else:
            # Item이 없으면 link만으로는 북마크 생성 불가 (item_id 필수)
            raise HTTPException(status_code=404, detail=f"Item with link '{bookmark_data.link}' not found. Please create bookmark with item_id or ensure the item exists in database.")
    else:
        raise HTTPException(status_code=400, detail="Either item_id or link must be provided")
    
    # 북마크 생성
    bookmark = Bookmark(
        item_id=item_id,
        title=title,
        tags=bookmark_data.tags or [],
        note=bookmark_data.note,
    )
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    
    # Item 정보 포함하여 반환
    if bookmark.item_id:
        item = db.query(Item).filter(Item.id == bookmark.item_id).first()
    
    return BookmarkResponse(
        id=bookmark.id,
        item_id=bookmark.item_id,
        title=bookmark.title,
        tags=bookmark.tags or [],
        note=bookmark.note,
        created_at=bookmark.created_at,
        item_title=item.title if item else None,
        item_link=item.link if item else None,
        item_published_at=item.published_at if item else None,
    )


@router.put("/{bookmark_id}", response_model=BookmarkResponse)
async def update_bookmark(
    bookmark_id: int,
    bookmark_data: BookmarkUpdate,
    db: Session = Depends(get_db)
):
    """북마크 수정.
    
    Args:
        bookmark_id: 북마크 ID
        bookmark_data: 수정할 데이터
        db: Database session
        
    Returns:
        BookmarkResponse: 수정된 북마크
        
    Raises:
        HTTPException: 북마크를 찾을 수 없을 때
    """
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    # 업데이트
    update_data = bookmark_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(bookmark, key, value)
    
    db.commit()
    db.refresh(bookmark)
    
    # Item 정보 포함하여 반환
    item = None
    if bookmark.item_id:
        item = db.query(Item).filter(Item.id == bookmark.item_id).first()
    
    return BookmarkResponse(
        id=bookmark.id,
        item_id=bookmark.item_id,
        title=bookmark.title,
        tags=bookmark.tags or [],
        note=bookmark.note,
        created_at=bookmark.created_at,
        item_title=item.title if item else None,
        item_link=item.link if item else None,
        item_published_at=item.published_at if item else None,
    )


@router.delete("/{bookmark_id}", status_code=204)
async def delete_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db)
):
    """북마크 삭제.
    
    Args:
        bookmark_id: 북마크 ID
        db: Database session
        
    Raises:
        HTTPException: 북마크를 찾을 수 없을 때
    """
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    db.delete(bookmark)
    db.commit()
    return None

