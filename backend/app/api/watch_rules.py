"""WatchRules API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.watch_rule import WatchRule
from backend.app.models.person import Person
from backend.app.schemas.watch_rule import WatchRuleResponse, WatchRuleCreate, WatchRuleUpdate

router = APIRouter(prefix="/api/watch-rules", tags=["watch-rules"])


@router.get("", response_model=List[WatchRuleResponse])
async def get_watch_rules(
    person_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """워치 규칙 목록 조회.
    
    Args:
        person_id: 인물 ID 필터 (None이면 전체)
        db: Database session
        
    Returns:
        List[WatchRuleResponse]: 워치 규칙 목록
    """
    query = db.query(WatchRule)
    if person_id is not None:
        query = query.filter(WatchRule.person_id == person_id)
    rules = query.order_by(WatchRule.priority.desc(), WatchRule.label).all()
    return rules


@router.post("", response_model=WatchRuleResponse, status_code=201)
async def create_watch_rule(
    rule_data: WatchRuleCreate,
    db: Session = Depends(get_db)
):
    """워치 규칙 추가.
    
    Args:
        rule_data: 워치 규칙 생성 데이터
        db: Database session
        
    Returns:
        WatchRuleResponse: 생성된 워치 규칙
        
    Raises:
        HTTPException: person_id가 유효하지 않을 때
    """
    # person_id 검증
    if rule_data.person_id:
        person = db.query(Person).filter(Person.id == rule_data.person_id).first()
        if not person:
            raise HTTPException(status_code=404, detail=f"Person with id {rule_data.person_id} not found")
    
    rule = WatchRule(
        label=rule_data.label,
        include_rules=rule_data.include_rules or [],
        exclude_rules=rule_data.exclude_rules or [],
        required_keywords=rule_data.required_keywords or [],
        optional_keywords=rule_data.optional_keywords or [],
        priority=rule_data.priority,
        person_id=rule_data.person_id,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.get("/{rule_id}", response_model=WatchRuleResponse)
async def get_watch_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    """워치 규칙 상세 조회.
    
    Args:
        rule_id: 워치 규칙 ID
        db: Database session
        
    Returns:
        WatchRuleResponse: 워치 규칙 상세 정보
        
    Raises:
        HTTPException: 워치 규칙을 찾을 수 없을 때
    """
    rule = db.query(WatchRule).filter(WatchRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="WatchRule not found")
    return rule


@router.put("/{rule_id}", response_model=WatchRuleResponse)
async def update_watch_rule(
    rule_id: int,
    rule_data: WatchRuleUpdate,
    db: Session = Depends(get_db)
):
    """워치 규칙 수정.
    
    Args:
        rule_id: 워치 규칙 ID
        rule_data: 수정할 데이터
        db: Database session
        
    Returns:
        WatchRuleResponse: 수정된 워치 규칙
        
    Raises:
        HTTPException: 워치 규칙을 찾을 수 없을 때, person_id가 유효하지 않을 때
    """
    rule = db.query(WatchRule).filter(WatchRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="WatchRule not found")
    
    # person_id 검증
    if rule_data.person_id is not None:
        person = db.query(Person).filter(Person.id == rule_data.person_id).first()
        if not person:
            raise HTTPException(status_code=404, detail=f"Person with id {rule_data.person_id} not found")
    
    # 업데이트
    update_data = rule_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rule, key, value)
    
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=204)
async def delete_watch_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    """워치 규칙 삭제.
    
    Args:
        rule_id: 워치 규칙 ID
        db: Database session
        
    Raises:
        HTTPException: 워치 규칙을 찾을 수 없을 때
    """
    rule = db.query(WatchRule).filter(WatchRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="WatchRule not found")
    
    db.delete(rule)
    db.commit()
    return None

