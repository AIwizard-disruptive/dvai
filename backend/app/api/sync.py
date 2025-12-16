"""Sync endpoints for Linear, Gmail, Calendar."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware import require_org_access
from app.models import Meeting

router = APIRouter()


@router.post("/linear/meeting/{meeting_id}")
async def sync_meeting_to_linear(
    meeting_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """Sync meeting action items to Linear."""
    org_id, _ = auth
    
    result = await db.execute(
        select(Meeting)
        .where(Meeting.id == meeting_id)
        .where(Meeting.org_id == org_id)
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found",
        )
    
    # TODO: Implement Linear sync task
    
    return {
        "status": "queued",
        "message": "Linear sync queued",
        "meeting_id": str(meeting_id),
    }


@router.post("/google/email/meeting/{meeting_id}")
async def create_follow_up_email(
    meeting_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """Generate follow-up email for meeting."""
    org_id, _ = auth
    
    result = await db.execute(
        select(Meeting)
        .where(Meeting.id == meeting_id)
        .where(Meeting.org_id == org_id)
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found",
        )
    
    # TODO: Implement Gmail draft creation task
    
    return {
        "status": "queued",
        "message": "Email draft creation queued",
        "meeting_id": str(meeting_id),
    }


@router.post("/google/calendar/meeting/{meeting_id}")
async def create_calendar_event(
    meeting_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """Create calendar event for meeting."""
    org_id, _ = auth
    
    result = await db.execute(
        select(Meeting)
        .where(Meeting.id == meeting_id)
        .where(Meeting.org_id == org_id)
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found",
        )
    
    # TODO: Implement Google Calendar event creation task
    
    return {
        "status": "queued",
        "message": "Calendar event creation queued",
        "meeting_id": str(meeting_id),
    }



