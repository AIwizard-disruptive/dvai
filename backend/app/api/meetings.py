"""Meeting endpoints."""
import uuid
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware import require_org_access
from app.models import Meeting, Artifact, TranscriptChunk, Summary, ActionItem, Decision
from app.worker.tasks.pipeline import process_artifact

router = APIRouter()


class MeetingCreate(BaseModel):
    """Meeting creation request."""
    title: str
    meeting_date: Optional[date] = None
    meeting_type: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None


class MeetingUpdate(BaseModel):
    """Meeting update request."""
    title: Optional[str] = None
    meeting_date: Optional[date] = None
    meeting_type: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None


class MeetingResponse(BaseModel):
    """Meeting response."""
    id: str
    title: str
    meeting_date: Optional[str] = None
    meeting_type: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    processing_status: str
    created_at: str
    
    class Config:
        from_attributes = True


class MeetingDetailResponse(MeetingResponse):
    """Meeting detail with related data."""
    transcript_chunks: list[dict] = []
    summary: Optional[dict] = None
    action_items: list[dict] = []
    decisions: list[dict] = []


@router.get("/", response_model=list[MeetingResponse])
async def list_meetings(
    request: Request,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """List meetings for organization."""
    org_id, _ = auth
    
    result = await db.execute(
        select(Meeting)
        .where(Meeting.org_id == org_id)
        .order_by(Meeting.meeting_date.desc().nullslast(), Meeting.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    meetings = result.scalars().all()
    
    return [
        MeetingResponse(
            id=str(m.id),
            title=m.title,
            meeting_date=str(m.meeting_date) if m.meeting_date else None,
            meeting_type=m.meeting_type,
            company=m.company,
            location=m.location,
            processing_status=m.processing_status,
            created_at=m.created_at.isoformat(),
        )
        for m in meetings
    ]


@router.post("/", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    meeting_data: MeetingCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """Create a new meeting."""
    org_id, _ = auth
    
    meeting = Meeting(
        org_id=org_id,
        title=meeting_data.title,
        meeting_date=meeting_data.meeting_date,
        meeting_type=meeting_data.meeting_type,
        company=meeting_data.company,
        location=meeting_data.location,
        processing_status="pending",
    )
    
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    
    return MeetingResponse(
        id=str(meeting.id),
        title=meeting.title,
        meeting_date=str(meeting.meeting_date) if meeting.meeting_date else None,
        meeting_type=meeting.meeting_type,
        company=meeting.company,
        location=meeting.location,
        processing_status=meeting.processing_status,
        created_at=meeting.created_at.isoformat(),
    )


@router.get("/{meeting_id}", response_model=MeetingDetailResponse)
async def get_meeting(
    meeting_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """Get meeting with full details."""
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
    
    # Get transcript chunks
    result = await db.execute(
        select(TranscriptChunk)
        .where(TranscriptChunk.meeting_id == meeting_id)
        .order_by(TranscriptChunk.sequence)
    )
    chunks = result.scalars().all()
    
    # Get summary
    result = await db.execute(
        select(Summary)
        .where(Summary.meeting_id == meeting_id)
        .order_by(Summary.created_at.desc())
        .limit(1)
    )
    summary = result.scalar_one_or_none()
    
    # Get action items
    result = await db.execute(
        select(ActionItem)
        .where(ActionItem.meeting_id == meeting_id)
        .order_by(ActionItem.created_at)
    )
    action_items = result.scalars().all()
    
    # Get decisions
    result = await db.execute(
        select(Decision)
        .where(Decision.meeting_id == meeting_id)
        .order_by(Decision.created_at)
    )
    decisions = result.scalars().all()
    
    return MeetingDetailResponse(
        id=str(meeting.id),
        title=meeting.title,
        meeting_date=str(meeting.meeting_date) if meeting.meeting_date else None,
        meeting_type=meeting.meeting_type,
        company=meeting.company,
        location=meeting.location,
        processing_status=meeting.processing_status,
        created_at=meeting.created_at.isoformat(),
        transcript_chunks=[
            {
                "id": str(c.id),
                "sequence": c.sequence,
                "speaker": c.speaker,
                "text": c.text,
                "start_time": c.start_time,
                "end_time": c.end_time,
            }
            for c in chunks
        ],
        summary={
            "id": str(summary.id),
            "content_md": summary.content_md,
            "created_at": summary.created_at.isoformat(),
        } if summary else None,
        action_items=[
            {
                "id": str(a.id),
                "title": a.title,
                "description": a.description,
                "owner_name": a.owner_name,
                "owner_email": a.owner_email,
                "status": a.status,
                "due_date": str(a.due_date) if a.due_date else None,
                "priority": a.priority,
                "confidence": a.confidence,
            }
            for a in action_items
        ],
        decisions=[
            {
                "id": str(d.id),
                "decision": d.decision,
                "rationale": d.rationale,
                "confidence": d.confidence,
            }
            for d in decisions
        ],
    )


@router.patch("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: uuid.UUID,
    meeting_data: MeetingUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """Update meeting."""
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
    
    # Update fields
    if meeting_data.title:
        meeting.title = meeting_data.title
    if meeting_data.meeting_date:
        meeting.meeting_date = meeting_data.meeting_date
    if meeting_data.meeting_type:
        meeting.meeting_type = meeting_data.meeting_type
    if meeting_data.company:
        meeting.company = meeting_data.company
    if meeting_data.location:
        meeting.location = meeting_data.location
    
    await db.commit()
    await db.refresh(meeting)
    
    return MeetingResponse(
        id=str(meeting.id),
        title=meeting.title,
        meeting_date=str(meeting.meeting_date) if meeting.meeting_date else None,
        meeting_type=meeting.meeting_type,
        company=meeting.company,
        location=meeting.location,
        processing_status=meeting.processing_status,
        created_at=meeting.created_at.isoformat(),
    )


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(
    meeting_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """Delete meeting."""
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
    
    await db.delete(meeting)
    await db.commit()
    
    return None


@router.post("/{meeting_id}/process")
async def process_meeting(
    meeting_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """Trigger processing pipeline for meeting."""
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
    
    # Get meeting's artifacts
    result = await db.execute(
        select(Artifact)
        .where(Artifact.meeting_id == meeting_id)
    )
    artifacts = result.scalars().all()
    
    if not artifacts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meeting has no artifacts to process",
        )
    
    # Trigger processing for first artifact
    artifact = artifacts[0]
    process_artifact.delay(str(artifact.id), str(org_id))
    
    return {
        "status": "processing",
        "meeting_id": str(meeting_id),
        "artifact_id": str(artifact.id),
    }




