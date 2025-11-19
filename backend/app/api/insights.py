"""Insights API endpoints."""
from datetime import datetime, timedelta, date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from backend.app.core.database import get_db
from backend.app.models.item import Item
from backend.app.models.person import Person
from backend.app.models.person_timeline import PersonTimeline
from backend.app.schemas.insights import (
    WeeklyInsightResponse,
    KeywordTrendResponse,
    PersonInsightResponse
)

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("/weekly", response_model=WeeklyInsightResponse)
async def get_weekly_insights(
    days: int = Query(7, ge=1, le=30, description="분석 기간 (일)"),
    db: Session = Depends(get_db)
):
    """주간 인사이트 조회.
    
    Args:
        days: 분석 기간 (일)
        db: Database session
        
    Returns:
        WeeklyInsightResponse: 주간 인사이트
    """
    # 기간 계산
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    previous_start_date = start_date - timedelta(days=days)
    
    end_dt = datetime.combine(end_date, datetime.max.time())
    start_dt = datetime.combine(start_date, datetime.min.time())
    previous_start_dt = datetime.combine(previous_start_date, datetime.min.time())
    
    # 현재 기간 아이템
    current_items = (
        db.query(Item)
        .filter(and_(Item.published_at >= start_dt, Item.published_at <= end_dt))
        .all()
    )
    
    # 이전 기간 아이템
    previous_items = (
        db.query(Item)
        .filter(and_(Item.published_at >= previous_start_dt, Item.published_at < start_dt))
        .all()
    )
    
    # 키워드 추출 (custom_tags에서)
    current_keywords = {}
    for item in current_items:
        for tag in item.custom_tags or []:
            current_keywords[tag] = current_keywords.get(tag, 0) + 1
    
    previous_keywords = {}
    for item in previous_items:
        for tag in item.custom_tags or []:
            previous_keywords[tag] = previous_keywords.get(tag, 0) + 1
    
    # 키워드 트렌드 계산
    all_keywords = set(list(current_keywords.keys()) + list(previous_keywords.keys()))
    keyword_trends = []
    for keyword in all_keywords:
        current_count = current_keywords.get(keyword, 0)
        previous_count = previous_keywords.get(keyword, 0)
        change = current_count - previous_count
        change_percent = ((current_count - previous_count) / previous_count * 100) if previous_count > 0 else (100 if current_count > 0 else 0)
        
        keyword_trends.append(KeywordTrendResponse(
            keyword=keyword,
            current_count=current_count,
            previous_count=previous_count,
            change=change,
            change_percent=change_percent
        ))
    
    # 상위 10개 키워드 (변화량 기준)
    keyword_trends.sort(key=lambda x: abs(x.change), reverse=True)
    top_keywords = keyword_trends[:10]
    
    # 인물별 인사이트
    persons = db.query(Person).all()
    person_insights = []
    for person in persons:
        # 최근 기간 이벤트
        events = (
            db.query(PersonTimeline)
            .filter(
                and_(
                    PersonTimeline.person_id == person.id,
                    PersonTimeline.created_at >= start_dt,
                    PersonTimeline.created_at <= end_dt
                )
            )
            .order_by(PersonTimeline.created_at.desc())
            .limit(5)
            .all()
        )
        
        # 이벤트 타입별 통계
        event_type_counts = {}
        for event in events:
            event_type_counts[event.event_type] = event_type_counts.get(event.event_type, 0) + 1
        
        # 최근 이벤트 정보
        recent_events = []
        for event in events:
            item = db.query(Item).filter(Item.id == event.item_id).first()
            recent_events.append({
                "event_id": event.id,
                "event_type": event.event_type,
                "item_id": event.item_id,
                "item_title": item.title if item else None,
                "item_link": item.link if item else None,
                "created_at": event.created_at.isoformat() if event.created_at else None,
            })
        
        if events or event_type_counts:
            person_insights.append(PersonInsightResponse(
                person_id=person.id,
                person_name=person.name,
                event_type_counts=event_type_counts,
                recent_events=recent_events
            ))
    
    return WeeklyInsightResponse(
        week_start=start_dt,
        week_end=end_dt,
        top_keywords=top_keywords,
        person_insights=person_insights,
        summary=None  # 향후 AI 생성 요약 추가 가능
    )


@router.get("/keywords", response_model=List[KeywordTrendResponse])
async def get_keyword_trends(
    days: int = Query(7, ge=1, le=30, description="분석 기간 (일)"),
    field: Optional[str] = Query(None, description="분야 필터"),
    db: Session = Depends(get_db)
):
    """키워드 트렌드 조회.
    
    Args:
        days: 분석 기간 (일)
        field: 분야 필터 (현재 미구현)
        db: Database session
        
    Returns:
        List[KeywordTrendResponse]: 키워드 트렌드 목록
    """
    # 기간 계산
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    previous_start_date = start_date - timedelta(days=days)
    
    end_dt = datetime.combine(end_date, datetime.max.time())
    start_dt = datetime.combine(start_date, datetime.min.time())
    previous_start_dt = datetime.combine(previous_start_date, datetime.min.time())
    
    # 현재/이전 기간 아이템
    current_items = (
        db.query(Item)
        .filter(and_(Item.published_at >= start_dt, Item.published_at <= end_dt))
        .all()
    )
    
    previous_items = (
        db.query(Item)
        .filter(and_(Item.published_at >= previous_start_dt, Item.published_at < start_dt))
        .all()
    )
    
    # 키워드 추출 및 통계
    current_keywords = {}
    for item in current_items:
        for tag in item.custom_tags or []:
            current_keywords[tag] = current_keywords.get(tag, 0) + 1
    
    previous_keywords = {}
    for item in previous_items:
        for tag in item.custom_tags or []:
            previous_keywords[tag] = previous_keywords.get(tag, 0) + 1
    
    # 트렌드 계산
    all_keywords = set(list(current_keywords.keys()) + list(previous_keywords.keys()))
    trends = []
    for keyword in all_keywords:
        current_count = current_keywords.get(keyword, 0)
        previous_count = previous_keywords.get(keyword, 0)
        change = current_count - previous_count
        change_percent = ((current_count - previous_count) / previous_count * 100) if previous_count > 0 else (100 if current_count > 0 else 0)
        
        trends.append(KeywordTrendResponse(
            keyword=keyword,
            current_count=current_count,
            previous_count=previous_count,
            change=change,
            change_percent=change_percent
        ))
    
    # 변화량 기준 정렬
    trends.sort(key=lambda x: abs(x.change), reverse=True)
    return trends


@router.get("/persons/{person_id}", response_model=PersonInsightResponse)
async def get_person_insights(
    person_id: int,
    days: int = Query(7, ge=1, le=30, description="분석 기간 (일)"),
    db: Session = Depends(get_db)
):
    """인물별 핵심 이슈 요약.
    
    Args:
        person_id: 인물 ID
        days: 분석 기간 (일)
        db: Database session
        
    Returns:
        PersonInsightResponse: 인물별 인사이트
        
    Raises:
        HTTPException: 인물을 찾을 수 없을 때
    """
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # 기간 계산
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    end_dt = datetime.combine(end_date, datetime.max.time())
    start_dt = datetime.combine(start_date, datetime.min.time())
    
    # 최근 이벤트
    events = (
        db.query(PersonTimeline)
        .filter(
            and_(
                PersonTimeline.person_id == person_id,
                PersonTimeline.created_at >= start_dt,
                PersonTimeline.created_at <= end_dt
            )
        )
        .order_by(PersonTimeline.created_at.desc())
        .limit(5)
        .all()
    )
    
    # 이벤트 타입별 통계
    event_type_counts = {}
    for event in events:
        event_type_counts[event.event_type] = event_type_counts.get(event.event_type, 0) + 1
    
    # 최근 이벤트 정보
    recent_events = []
    for event in events:
        item = db.query(Item).filter(Item.id == event.item_id).first()
        recent_events.append({
            "event_id": event.id,
            "event_type": event.event_type,
            "item_id": event.item_id,
            "item_title": item.title if item else None,
            "item_link": item.link if item else None,
            "created_at": event.created_at.isoformat() if event.created_at else None,
        })
    
    return PersonInsightResponse(
        person_id=person.id,
        person_name=person.name,
        event_type_counts=event_type_counts,
        recent_events=recent_events
    )

