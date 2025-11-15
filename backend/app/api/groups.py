from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.app.core.database import get_db
from backend.app.models.dup_group_meta import DupGroupMeta
from backend.app.models.item import Item

router = APIRouter(prefix="/api/groups", tags=["groups"])


@router.get("")
def list_groups(
    since: str = Query(..., description="ISO date (YYYY-MM-DD) since which to compute new/incremental"),
    kind: str = Query("new", regex="^(new|incremental)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    try:
        since_dt = datetime.fromisoformat(since)
    except Exception:
        raise HTTPException(400, "Invalid since format. Expected YYYY-MM-DD")

    q = db.query(DupGroupMeta)
    if kind == "new":
        q = q.filter(DupGroupMeta.first_seen_at >= since_dt)
    else:
        q = q.filter(and_(DupGroupMeta.first_seen_at < since_dt, DupGroupMeta.last_updated_at >= since_dt))

    total = q.count()
    metas: List[DupGroupMeta] = (
        q.order_by(DupGroupMeta.last_updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # Fetch representative item (seed == dup_group_id)
    groups = []
    for m in metas:
        seed = db.query(Item).filter(Item.id == m.dup_group_id).first()
        groups.append(
            {
                "dup_group_id": m.dup_group_id,
                "first_seen_at": m.first_seen_at,
                "last_updated_at": m.last_updated_at,
                "member_count": m.member_count,
                "representative": {
                    "id": seed.id if seed else None,
                    "title": seed.title if seed else None,
                    "link": seed.link if seed else None,
                    "published_at": seed.published_at if seed else None,
                    "summary_short": seed.summary_short if seed else None,
                },
            }
        )

    return {"total": total, "page": page, "page_size": page_size, "groups": groups}


@router.get("/{dup_group_id}")
def get_group(
    dup_group_id: int,
    db: Session = Depends(get_db),
):
    items = (
        db.query(Item)
        .filter(Item.dup_group_id == dup_group_id)
        .order_by(Item.published_at.asc())
        .all()
    )
    return [
        {
            "id": it.id,
            "title": it.title,
            "link": it.link,
            "published_at": it.published_at,
            "summary_short": it.summary_short,
        }
        for it in items
    ]


