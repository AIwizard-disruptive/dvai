"""Decision endpoints."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware import require_org_access
from app.models import Decision

router = APIRouter()


class DecisionResponse(BaseModel):
    """Decision response."""
    id: str
    meeting_id: str
    decision: str
    rationale: Optional[str] = None
    confidence: Optional[float] = None
    source_quote: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True


@router.get("/", response_model=list[DecisionResponse])
async def list_decisions(
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """List decisions for organization."""
    org_id, _ = auth
    
    result = await db.execute(
        select(Decision)
        .where(Decision.org_id == org_id)
        .order_by(Decision.created_at.desc())
        .limit(100)
    )
    decisions = result.scalars().all()
    
    return [
        DecisionResponse(
            id=str(d.id),
            meeting_id=str(d.meeting_id),
            decision=d.decision,
            rationale=d.rationale,
            confidence=d.confidence,
            source_quote=d.source_quote,
            created_at=d.created_at.isoformat(),
        )
        for d in decisions
    ]

