"""API endpoints for creating meetings with AI-generated agendas."""
import uuid
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware import require_org_access
from app.models import Meeting
from app.services.agenda_generator import (
    get_agenda_generator_service,
    MeetingAgenda,
)


router = APIRouter()


class CreateMeetingWithAgendaRequest(BaseModel):
    """Request to create a meeting with AI-generated agenda."""
    meeting_name: str = Field(..., min_length=1, max_length=500, description="Name/title of the meeting")
    meeting_description: str = Field(..., min_length=10, description="Description of what the meeting is about")
    
    # Calendar event details
    start_time: Optional[datetime] = Field(None, description="When the meeting should start (if creating calendar event)")
    duration_minutes: Optional[int] = Field(60, description="Meeting duration (if not AI-suggested)")
    location: Optional[str] = Field(None, description="Meeting location or video link")
    attendee_emails: list[str] = Field(default_factory=list, description="Email addresses of attendees")
    
    # Options
    create_calendar_event: bool = Field(True, description="Whether to create Google Calendar event")
    send_invites: bool = Field(False, description="Whether to send calendar invites (requires calendar event)")
    
    # Additional context for AI
    meeting_type: Optional[str] = Field(None, description="Type of meeting (e.g., 'planning', 'review', 'decision')")
    company_context: Optional[str] = Field(None, description="Company or project context")


class MeetingWithAgendaResponse(BaseModel):
    """Response after creating meeting with agenda."""
    meeting_id: str
    meeting_name: str
    agenda: dict  # MeetingAgenda as dict
    agenda_markdown: str
    calendar_event_id: Optional[str] = None
    calendar_event_link: Optional[str] = None
    status: str


@router.post("/meetings/with-agenda", response_model=MeetingWithAgendaResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting_with_ai_agenda(
    request: Request,
    data: CreateMeetingWithAgendaRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """
    Create a meeting with AI-generated agenda and optionally sync to Google Calendar.
    
    This endpoint:
    1. Takes meeting name + description
    2. Uses AI to generate a comprehensive agenda
    3. Creates meeting record in database
    4. Optionally creates Google Calendar event with the agenda
    5. Returns the meeting with full agenda
    
    The agenda includes:
    - Meeting objective
    - Discussion topics with time estimates
    - Expected decisions to make
    - Proposed next steps
    - Preparation notes
    """
    org_id, user = auth
    
    # Generate AI agenda
    agenda_service = get_agenda_generator_service()
    
    # Prepare context for AI
    meeting_context = {}
    if data.meeting_type:
        meeting_context["meeting_type"] = data.meeting_type
    if data.company_context:
        meeting_context["company_context"] = data.company_context
    
    try:
        agenda = await agenda_service.generate_agenda(
            meeting_name=data.meeting_name,
            meeting_description=data.meeting_description,
            participants=data.attendee_emails,
            meeting_context=meeting_context if meeting_context else None,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate agenda: {str(e)}"
        )
    
    # Format agenda
    agenda_markdown = agenda_service.format_agenda_as_markdown(agenda)
    
    # Use AI-suggested duration if not provided
    duration = data.duration_minutes or agenda.suggested_duration_minutes
    
    # Calculate end time if start time provided
    end_time = None
    if data.start_time:
        end_time = data.start_time + timedelta(minutes=duration)
    
    # Create meeting record
    meeting_id = uuid.uuid4()
    meeting_date = data.start_time.date() if data.start_time else None
    
    await db.execute(
        text("""
            INSERT INTO meetings (
                id, org_id, title, meeting_date, meeting_type, location,
                duration_minutes, processing_status, meeting_metadata, created_at, updated_at
            ) VALUES (
                :id, :org_id, :title, :meeting_date, :meeting_type, :location,
                :duration, 'pending', :metadata, NOW(), NOW()
            )
        """),
        {
            "id": meeting_id,
            "org_id": org_id,
            "title": data.meeting_name,
            "meeting_date": meeting_date,
            "meeting_type": data.meeting_type,
            "location": data.location,
            "duration": duration,
            "metadata": {
                "description": data.meeting_description,
                "ai_generated_agenda": agenda.model_dump(),
                "agenda_markdown": agenda_markdown,
                "attendee_emails": data.attendee_emails,
            },
        }
    )
    
    await db.commit()
    
    calendar_event_id = None
    calendar_event_link = None
    
    # Create calendar event if requested
    if data.create_calendar_event and data.start_time:
        if not data.attendee_emails:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="attendee_emails required when creating calendar event"
            )
        
        # Queue calendar event creation
        from app.worker.tasks.sync import create_meeting_calendar_event_with_agenda
        
        background_tasks.add_task(
            create_meeting_calendar_event_with_agenda.delay,
            str(meeting_id),
            str(org_id),
            data.send_invites,
        )
        
        status_msg = "queued_calendar_event"
    else:
        status_msg = "created_no_calendar"
    
    return MeetingWithAgendaResponse(
        meeting_id=str(meeting_id),
        meeting_name=data.meeting_name,
        agenda=agenda.model_dump(),
        agenda_markdown=agenda_markdown,
        calendar_event_id=calendar_event_id,
        calendar_event_link=calendar_event_link,
        status=status_msg,
    )


@router.get("/meetings/{meeting_id}/agenda", response_model=dict)
async def get_meeting_agenda(
    meeting_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """
    Get the AI-generated agenda for a meeting.
    
    Returns the structured agenda if it exists in the meeting metadata.
    """
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
            detail="Meeting not found"
        )
    
    if not meeting.meeting_metadata or "ai_generated_agenda" not in meeting.meeting_metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No AI-generated agenda found for this meeting"
        )
    
    return {
        "meeting_id": str(meeting.id),
        "meeting_name": meeting.title,
        "agenda": meeting.meeting_metadata["ai_generated_agenda"],
        "agenda_markdown": meeting.meeting_metadata.get("agenda_markdown", ""),
    }


@router.post("/meetings/{meeting_id}/regenerate-agenda", response_model=dict)
async def regenerate_meeting_agenda(
    meeting_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """
    Regenerate the AI agenda for an existing meeting.
    
    Useful if the meeting details changed or you want a fresh perspective.
    """
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
            detail="Meeting not found"
        )
    
    # Get description and attendees from metadata
    metadata = meeting.meeting_metadata or {}
    description = metadata.get("description", "No description provided")
    attendees = metadata.get("attendee_emails", [])
    meeting_context = {
        "meeting_type": meeting.meeting_type,
    } if meeting.meeting_type else None
    
    # Generate new agenda
    agenda_service = get_agenda_generator_service()
    try:
        agenda = await agenda_service.generate_agenda(
            meeting_name=meeting.title,
            meeting_description=description,
            participants=attendees,
            meeting_context=meeting_context,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate agenda: {str(e)}"
        )
    
    agenda_markdown = agenda_service.format_agenda_as_markdown(agenda)
    
    # Update meeting metadata
    updated_metadata = meeting.meeting_metadata or {}
    updated_metadata["ai_generated_agenda"] = agenda.model_dump()
    updated_metadata["agenda_markdown"] = agenda_markdown
    
    await db.execute(
        text("""
            UPDATE meetings
            SET meeting_metadata = :metadata,
                updated_at = NOW()
            WHERE id = :meeting_id
        """),
        {
            "meeting_id": meeting_id,
            "metadata": updated_metadata,
        }
    )
    await db.commit()
    
    return {
        "meeting_id": str(meeting.id),
        "meeting_name": meeting.title,
        "agenda": agenda.model_dump(),
        "agenda_markdown": agenda_markdown,
        "status": "regenerated",
    }

