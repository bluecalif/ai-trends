"""Persons API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.person import Person
from backend.app.models.person_timeline import PersonTimeline
from backend.app.models.item import Item
from backend.app.services.person_tracker import PersonTracker
from backend.app.schemas.person import (
    PersonResponse,
    PersonCreate,
    PersonDetailResponse,
    PersonTimelineEventResponse
)

router = APIRouter(prefix="/api/persons", tags=["persons"])


@router.get("", response_model=List[PersonResponse])
async def get_persons(
    db: Session = Depends(get_db)
):
    """인물 목록 조회.
    
    Args:
        db: Database session
        
    Returns:
        List[PersonResponse]: 인물 목록
    """
    persons = db.query(Person).order_by(Person.name).all()
    return persons


@router.post("", response_model=PersonResponse, status_code=201)
async def create_person(
    person_data: PersonCreate,
    db: Session = Depends(get_db)
):
    """인물 추가.
    
    Args:
        person_data: 인물 생성 데이터
        db: Database session
        
    Returns:
        PersonResponse: 생성된 인물
        
    Raises:
        HTTPException: name이 이미 존재할 때
    """
    # 중복 체크
    existing = db.query(Person).filter(Person.name == person_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Person with name '{person_data.name}' already exists")
    
    person = Person(**person_data.dict())
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


@router.get("/{person_id}", response_model=PersonDetailResponse)
async def get_person(
    person_id: int,
    include_timeline: bool = True,
    include_graph: bool = True,
    db: Session = Depends(get_db)
):
    """인물 상세 조회 (타임라인 + 관계 그래프).
    
    Args:
        person_id: 인물 ID
        include_timeline: 타임라인 포함 여부
        include_graph: 관계 그래프 포함 여부
        db: Database session
        
    Returns:
        PersonDetailResponse: 인물 상세 정보
        
    Raises:
        HTTPException: 인물을 찾을 수 없을 때
    """
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # 타임라인 조회
    timeline_events = []
    if include_timeline:
        events = (
            db.query(PersonTimeline)
            .filter(PersonTimeline.person_id == person_id)
            .order_by(PersonTimeline.created_at.desc())
            .all()
        )
        
        for event in events:
            # Item 정보 가져오기
            item = db.query(Item).filter(Item.id == event.item_id).first()
            timeline_events.append(PersonTimelineEventResponse(
                id=event.id,
                person_id=event.person_id,
                item_id=event.item_id,
                event_type=event.event_type,
                description=event.description,
                created_at=event.created_at,
                item_title=item.title if item else None,
                item_link=item.link if item else None,
                item_published_at=item.published_at if item else None,
            ))
    
    # 관계 그래프 생성
    relationship_graph = None
    if include_graph:
        tracker = PersonTracker(db)
        graph_data = tracker.build_relationship_graph(person_id)
        if graph_data:
            relationship_graph = {
                "person": {
                    "id": graph_data["person"].id,
                    "name": graph_data["person"].name,
                    "bio": graph_data["person"].bio,
                },
                "items": [
                    {
                        "id": item.id,
                        "title": item.title,
                        "link": item.link,
                        "published_at": item.published_at.isoformat() if item.published_at else None,
                    }
                    for item in graph_data["items"]
                ],
                "entities": [
                    {
                        "id": entity.id,
                        "name": entity.name,
                        "type": entity.type.value if hasattr(entity.type, 'value') else str(entity.type),
                    }
                    for entity in graph_data["entities"]
                ],
                "connections": graph_data["connections"],
            }
    
    return PersonDetailResponse(
        id=person.id,
        name=person.name,
        bio=person.bio,
        created_at=person.created_at,
        updated_at=person.updated_at,
        timeline=timeline_events,
        relationship_graph=relationship_graph,
    )

