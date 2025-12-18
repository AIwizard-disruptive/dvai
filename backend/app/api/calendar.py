"""Calendar and scheduling endpoints."""
import uuid
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from pydantic import BaseModel
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware import require_org_access
from app.models import Meeting, ExternalRef

router = APIRouter()


class CalendarProposal(BaseModel):
    """Calendar event proposal."""
    id: str
    meeting_id: str
    title: str
    description: str
    start_time: str
    end_time: str
    attendees: list[str]
    status: str  # pending, approved, rejected
    created_at: str


class CalendarProposalCreate(BaseModel):
    """Create calendar proposal."""
    meeting_id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    attendees: list[str]


@router.get("/proposals", response_model=list[CalendarProposal])
async def list_calendar_proposals(
    request: Request,
    status_filter: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """
    List calendar event proposals.
    
    These are suggested calendar events that haven't been created yet.
    Users can review and approve/reject them.
    """
    org_id, _ = auth
    
    # Query external_refs for calendar proposals
    query = text("""
        SELECT 
            er.id,
            er.local_id as meeting_id,
            er.external_id,
            er.sync_metadata,
            er.created_at,
            m.title as meeting_title
        FROM external_refs er
        JOIN meetings m ON er.local_id = m.id
        WHERE er.org_id = :org_id
        AND er.kind = 'calendar_proposal'
        AND er.provider = 'google'
    """)
    
    if status_filter:
        query = text(str(query) + " AND er.sync_metadata->>'status' = :status")
        result = await db.execute(query, {"org_id": org_id, "status": status_filter})
    else:
        result = await db.execute(query, {"org_id": org_id})
    
    proposals = []
    for row in result:
        metadata = row.sync_metadata or {}
        proposals.append(
            CalendarProposal(
                id=str(row.id),
                meeting_id=str(row.meeting_id),
                title=metadata.get("title", row.meeting_title),
                description=metadata.get("description", ""),
                start_time=metadata.get("start_time", ""),
                end_time=metadata.get("end_time", ""),
                attendees=metadata.get("attendees", []),
                status=metadata.get("status", "pending"),
                created_at=row.created_at.isoformat(),
            )
        )
    
    return proposals


@router.post("/proposals", response_model=CalendarProposal, status_code=status.HTTP_201_CREATED)
async def create_calendar_proposal(
    proposal_data: CalendarProposalCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """
    Create a calendar event proposal.
    
    This doesn't create an actual calendar event yet - it creates a proposal
    that can be reviewed and approved later.
    """
    org_id, _ = auth
    
    # Verify meeting exists and belongs to org
    meeting_id = uuid.UUID(proposal_data.meeting_id)
    result = await db.execute(
        select(Meeting)
        .where(Meeting.id == meeting_id)
        .where(Meeting.org_id == org_id)
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    
    # Create external_ref as calendar_proposal
    proposal_id = str(uuid.uuid4())
    await db.execute(
        text("""
            INSERT INTO external_refs (
                id, org_id, local_table, local_id,
                provider, kind, external_id, sync_metadata, created_at, updated_at
            ) VALUES (
                :id, :org_id, 'meetings', :meeting_id,
                'google', 'calendar_proposal', :external_id, :metadata, NOW(), NOW()
            )
        """),
        {
            "id": proposal_id,
            "org_id": org_id,
            "meeting_id": meeting_id,
            "external_id": f"proposal_{proposal_id}",
            "metadata": {
                "title": proposal_data.title,
                "description": proposal_data.description,
                "start_time": proposal_data.start_time.isoformat(),
                "end_time": proposal_data.end_time.isoformat(),
                "attendees": proposal_data.attendees,
                "status": "pending",
            }
        }
    )
    await db.commit()
    
    return CalendarProposal(
        id=proposal_id,
        meeting_id=str(meeting_id),
        title=proposal_data.title,
        description=proposal_data.description,
        start_time=proposal_data.start_time.isoformat(),
        end_time=proposal_data.end_time.isoformat(),
        attendees=proposal_data.attendees,
        status="pending",
        created_at=datetime.utcnow().isoformat(),
    )


@router.post("/proposals/{proposal_id}/approve")
async def approve_calendar_proposal(
    proposal_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """
    Approve a calendar proposal and create the actual event.
    
    This triggers the Google Calendar integration to create the event.
    """
    org_id, _ = auth
    
    # Get proposal
    result = await db.execute(
        text("""
            SELECT id, local_id, sync_metadata
            FROM external_refs
            WHERE id = :proposal_id
            AND org_id = :org_id
            AND kind = 'calendar_proposal'
        """),
        {"proposal_id": proposal_id, "org_id": org_id}
    )
    proposal = result.first()
    
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found"
        )
    
    # Update status to approved
    await db.execute(
        text("""
            UPDATE external_refs
            SET sync_metadata = sync_metadata || '{"status": "approved"}'::jsonb,
                updated_at = NOW()
            WHERE id = :proposal_id
        """),
        {"proposal_id": proposal_id}
    )
    await db.commit()
    
    # Trigger calendar event creation
    from app.worker.tasks.sync import create_google_calendar_event
    create_google_calendar_event.delay(str(proposal.local_id), str(org_id))
    
    return {
        "status": "approved",
        "message": "Calendar event creation queued",
        "proposal_id": str(proposal_id),
    }


@router.post("/proposals/{proposal_id}/reject")
async def reject_calendar_proposal(
    proposal_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """Reject a calendar proposal."""
    org_id, _ = auth
    
    result = await db.execute(
        text("""
            UPDATE external_refs
            SET sync_metadata = sync_metadata || '{"status": "rejected"}'::jsonb,
                updated_at = NOW()
            WHERE id = :proposal_id
            AND org_id = :org_id
            AND kind = 'calendar_proposal'
        """),
        {"proposal_id": proposal_id, "org_id": org_id}
    )
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found"
        )
    
    await db.commit()
    
    return {
        "status": "rejected",
        "proposal_id": str(proposal_id),
    }


@router.delete("/proposals/{proposal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_calendar_proposal(
    proposal_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """Delete a calendar proposal."""
    org_id, _ = auth
    
    result = await db.execute(
        text("""
            DELETE FROM external_refs
            WHERE id = :proposal_id
            AND org_id = :org_id
            AND kind = 'calendar_proposal'
        """),
        {"proposal_id": proposal_id, "org_id": org_id}
    )
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found"
        )
    
    await db.commit()
    return None





