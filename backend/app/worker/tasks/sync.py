"""Sync tasks for external integrations."""
import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, text

from app.worker.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models import (
    Meeting, ActionItem, Decision, Summary, 
    ExternalRef, Integration, Person, MeetingParticipant
)
from app.integrations.linear import get_linear_client
from app.integrations.google_client import get_google_client
from app.config import settings


async def get_integration_secrets(org_id: uuid.UUID, provider: str) -> Optional[dict]:
    """Get decrypted secrets for an integration."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Integration)
            .where(Integration.org_id == org_id)
            .where(Integration.provider == provider)
            .where(Integration.enabled == True)
        )
        integration = result.scalar_one_or_none()
        
        if not integration:
            return None
        
        # In production, decrypt secrets_encrypted
        # For now, parse JSON (NOT SECURE - placeholder)
        import json
        if integration.secrets_encrypted:
            return json.loads(integration.secrets_encrypted)
        
        return None


@celery_app.task(name="sync.linear.sync_action_items")
def sync_action_items_to_linear(meeting_id: str, org_id: str):
    """Sync action items from a meeting to Linear."""
    import asyncio
    return asyncio.run(_sync_action_items_to_linear(meeting_id, org_id))


async def _sync_action_items_to_linear(meeting_id: str, org_id: str):
    """Async implementation of Linear sync."""
    meeting_uuid = uuid.UUID(meeting_id)
    org_uuid = uuid.UUID(org_id)
    
    # Get Linear secrets
    secrets = await get_integration_secrets(org_uuid, "linear")
    if not secrets:
        return {"status": "error", "message": "Linear not configured"}
    
    async with AsyncSessionLocal() as db:
        # Get meeting and action items
        result = await db.execute(
            select(Meeting).where(Meeting.id == meeting_uuid)
        )
        meeting = result.scalar_one()
        
        result = await db.execute(
            select(ActionItem)
            .where(ActionItem.meeting_id == meeting_uuid)
            .where(ActionItem.status.in_(["open", "in_progress"]))
        )
        action_items = result.scalars().all()
        
        # Get Linear team ID from config
        result = await db.execute(
            select(Integration)
            .where(Integration.org_id == org_uuid)
            .where(Integration.provider == "linear")
        )
        integration = result.scalar_one()
        team_id = integration.config.get("team_id") if integration.config else None
        
        if not team_id:
            return {"status": "error", "message": "Linear team_id not configured"}
        
        # Create Linear client
        linear = get_linear_client(api_key=secrets.get("api_key"))
        
        synced_count = 0
        for item in action_items:
            # Check if already synced
            result = await db.execute(
                select(ExternalRef)
                .where(ExternalRef.local_table == "action_items")
                .where(ExternalRef.local_id == item.id)
                .where(ExternalRef.provider == "linear")
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing issue
                try:
                    # Map status
                    state_mapping = {
                        "open": "Todo",
                        "in_progress": "In Progress",
                        "blocked": "Blocked",
                        "done": "Done",
                    }
                    
                    # Get state ID (would need to fetch from Linear)
                    # For now, just update title/description
                    await linear.update_issue(
                        issue_id=existing.external_id,
                        title=item.title,
                        description=item.description,
                    )
                    synced_count += 1
                except Exception as e:
                    print(f"Failed to update Linear issue: {e}")
            else:
                # Create new issue
                try:
                    description = f"""
{item.description or ''}

**From Meeting**: {meeting.title}
**Meeting Date**: {meeting.meeting_date}
**Source Quote**: {item.source_quote[:200] if item.source_quote else 'N/A'}...
**Confidence**: {item.confidence}
                    """.strip()
                    
                    issue = await linear.create_issue(
                        team_id=team_id,
                        title=item.title,
                        description=description,
                        due_date=str(item.due_date) if item.due_date else None,
                        priority=2 if item.priority == "high" else 3,
                    )
                    
                    # Create external ref
                    external_ref = ExternalRef(
                        org_id=org_uuid,
                        local_table="action_items",
                        local_id=item.id,
                        provider="linear",
                        kind="linear_issue",
                        external_id=issue["id"],
                        external_url=issue.get("url"),
                    )
                    db.add(external_ref)
                    synced_count += 1
                    
                except Exception as e:
                    print(f"Failed to create Linear issue: {e}")
        
        await db.commit()
        
        return {
            "status": "success",
            "synced": synced_count,
            "total": len(action_items),
        }


@celery_app.task(name="sync.google.create_email_draft")
def create_google_email_draft(meeting_id: str, org_id: str):
    """Create Gmail draft with meeting follow-up."""
    import asyncio
    return asyncio.run(_create_google_email_draft(meeting_id, org_id))


async def _create_google_email_draft(meeting_id: str, org_id: str):
    """Async implementation of Gmail draft creation."""
    meeting_uuid = uuid.UUID(meeting_id)
    org_uuid = uuid.UUID(org_id)
    
    # Get Google secrets
    secrets = await get_integration_secrets(org_uuid, "google")
    if not secrets:
        return {"status": "error", "message": "Google not configured"}
    
    async with AsyncSessionLocal() as db:
        # Get meeting data
        result = await db.execute(
            select(Meeting).where(Meeting.id == meeting_uuid)
        )
        meeting = result.scalar_one()
        
        # Get summary
        result = await db.execute(
            select(Summary)
            .where(Summary.meeting_id == meeting_uuid)
            .order_by(Summary.created_at.desc())
            .limit(1)
        )
        summary = result.scalar_one_or_none()
        
        # Get decisions
        result = await db.execute(
            select(Decision).where(Decision.meeting_id == meeting_uuid)
        )
        decisions = result.scalars().all()
        
        # Get action items
        result = await db.execute(
            select(ActionItem).where(ActionItem.meeting_id == meeting_uuid)
        )
        action_items = result.scalars().all()
        
        # Get participants for To: field
        result = await db.execute(
            select(Person)
            .join(MeetingParticipant)
            .where(MeetingParticipant.meeting_id == meeting_uuid)
        )
        participants = result.scalars().all()
        participant_emails = [p.email for p in participants if p.email]
        
        # Build email content
        subject = f"Follow-up: {meeting.title}"
        
        body_html = f"""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>{meeting.title}</h2>
    <p><strong>Date:</strong> {meeting.meeting_date or 'N/A'}</p>
    
    <h3>Summary</h3>
    <div>{summary.content_md if summary else 'No summary available'}</div>
    
    <h3>Key Decisions</h3>
    <ul>
        {''.join(f'<li><strong>{d.decision}</strong><br/><em>{d.rationale or ""}</em></li>' for d in decisions)}
    </ul>
    
    <h3>Action Items</h3>
    <ul>
        {''.join(f'<li><strong>{a.title}</strong> - {a.owner_name or "Unassigned"} {f"(Due: {a.due_date})" if a.due_date else ""}<br/>{a.description or ""}</li>' for a in action_items)}
    </ul>
    
    <p><a href="http://localhost:3000/meetings/{meeting_uuid}">View full transcript and details</a></p>
    
    <p>Best regards,<br/>Meeting Intelligence Platform</p>
</body>
</html>
        """.strip()
        
        # Create Google client
        google = get_google_client(
            access_token=secrets.get("access_token"),
            refresh_token=secrets.get("refresh_token"),
        )
        
        # Create draft or send
        if settings.enable_email_send:
            # Actually send email
            result_data = await google.send_email(
                to=participant_emails,
                subject=subject,
                body_html=body_html,
            )
            kind = "gmail_message"
        else:
            # Create draft only (safer default)
            result_data = await google.create_email_draft(
                to=participant_emails,
                subject=subject,
                body_html=body_html,
            )
            kind = "gmail_draft"
        
        # Save external ref
        external_ref = ExternalRef(
            org_id=org_uuid,
            local_table="meetings",
            local_id=meeting_uuid,
            provider="google",
            kind=kind,
            external_id=result_data["id"],
        )
        db.add(external_ref)
        await db.commit()
        
        return {
            "status": "success",
            "kind": kind,
            "id": result_data["id"],
        }


@celery_app.task(name="sync.google.create_calendar_event")
def create_google_calendar_event(meeting_id: str, org_id: str):
    """Create Google Calendar event."""
    import asyncio
    return asyncio.run(_create_google_calendar_event(meeting_id, org_id))


async def _create_google_calendar_event(meeting_id: str, org_id: str):
    """Async implementation of calendar event creation."""
    meeting_uuid = uuid.UUID(meeting_id)
    org_uuid = uuid.UUID(org_id)
    
    # Get Google secrets
    secrets = await get_integration_secrets(org_uuid, "google")
    if not secrets:
        return {"status": "error", "message": "Google not configured"}
    
    async with AsyncSessionLocal() as db:
        # Get meeting
        result = await db.execute(
            select(Meeting).where(Meeting.id == meeting_uuid)
        )
        meeting = result.scalar_one()
        
        # Get participants
        result = await db.execute(
            select(Person)
            .join(MeetingParticipant)
            .where(MeetingParticipant.meeting_id == meeting_uuid)
        )
        participants = result.scalars().all()
        attendee_emails = [p.email for p in participants if p.email]
        
        # Determine event time (1 week from now as default)
        start_time = datetime.utcnow() + timedelta(days=7)
        end_time = start_time + timedelta(hours=1)
        
        # Create Google client
        google = get_google_client(
            access_token=secrets.get("access_token"),
            refresh_token=secrets.get("refresh_token"),
        )
        
        # Create event or proposal
        if settings.enable_calendar_booking:
            # Actually create event
            result_data = await google.create_calendar_event(
                summary=f"Follow-up: {meeting.title}",
                start_time=start_time,
                end_time=end_time,
                description=f"Follow-up meeting for: {meeting.title}",
                attendees=attendee_emails,
                send_updates=True,
            )
            kind = "google_event"
        else:
            # Create proposal only (safer default)
            external_ref = ExternalRef(
                org_id=org_uuid,
                local_table="meetings",
                local_id=meeting_uuid,
                provider="google",
                kind="calendar_proposal",
                external_id=f"proposal_{meeting_uuid}",
                sync_metadata={
                    "title": f"Follow-up: {meeting.title}",
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "attendees": attendee_emails,
                    "status": "pending",
                }
            )
            db.add(external_ref)
            await db.commit()
            
            return {
                "status": "proposal_created",
                "message": "Calendar proposal created. Review and approve in dashboard.",
            }
        
        # Save external ref for actual event
        external_ref = ExternalRef(
            org_id=org_uuid,
            local_table="meetings",
            local_id=meeting_uuid,
            provider="google",
            kind=kind,
            external_id=result_data["id"],
            external_url=result_data.get("html_link"),
        )
        db.add(external_ref)
        await db.commit()
        
        return {
            "status": "success",
            "kind": kind,
            "id": result_data["id"],
            "url": result_data.get("html_link"),
        }


@celery_app.task(name="sync.google.create_meeting_with_agenda")
def create_meeting_calendar_event_with_agenda(meeting_id: str, org_id: str, send_invites: bool = False):
    """Create Google Calendar event with AI-generated agenda in description."""
    import asyncio
    return asyncio.run(_create_meeting_calendar_event_with_agenda(meeting_id, org_id, send_invites))


async def _create_meeting_calendar_event_with_agenda(meeting_id: str, org_id: str, send_invites: bool):
    """Async implementation of calendar event creation with AI agenda."""
    meeting_uuid = uuid.UUID(meeting_id)
    org_uuid = uuid.UUID(org_id)
    
    # Get Google secrets
    secrets = await get_integration_secrets(org_uuid, "google")
    if not secrets:
        return {"status": "error", "message": "Google not configured"}
    
    async with AsyncSessionLocal() as db:
        # Get meeting with metadata
        result = await db.execute(
            select(Meeting).where(Meeting.id == meeting_uuid)
        )
        meeting = result.scalar_one()
        
        # Extract meeting details from metadata
        metadata = meeting.meeting_metadata or {}
        ai_agenda = metadata.get("ai_generated_agenda")
        attendee_emails = metadata.get("attendee_emails", [])
        
        if not ai_agenda:
            return {"status": "error", "message": "No AI agenda found in meeting metadata"}
        
        # Format agenda for calendar
        from app.services.agenda_generator import get_agenda_generator_service, MeetingAgenda
        agenda_service = get_agenda_generator_service()
        agenda_obj = MeetingAgenda(**ai_agenda)
        agenda_text = agenda_service.format_agenda_for_calendar(agenda_obj)
        
        # Determine event time
        if meeting.meeting_date:
            start_time = datetime.combine(meeting.meeting_date, datetime.min.time())
        else:
            # Default to tomorrow at 10 AM
            start_time = (datetime.utcnow() + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
        
        duration_minutes = meeting.duration_minutes or agenda_obj.suggested_duration_minutes
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Create Google client
        google = get_google_client(
            access_token=secrets.get("access_token"),
            refresh_token=secrets.get("refresh_token"),
        )
        
        # Create calendar event with agenda
        try:
            result_data = await google.create_calendar_event(
                summary=meeting.title,
                start_time=start_time,
                end_time=end_time,
                description=agenda_text,
                location=meeting.location,
                attendees=attendee_emails,
                send_updates=send_invites,
            )
            
            # Save external ref
            external_ref = ExternalRef(
                org_id=org_uuid,
                local_table="meetings",
                local_id=meeting_uuid,
                provider="google",
                kind="google_event",
                external_id=result_data["id"],
                external_url=result_data.get("html_link"),
                sync_metadata={
                    "created_with_ai_agenda": True,
                    "send_invites": send_invites,
                }
            )
            db.add(external_ref)
            await db.commit()
            
            return {
                "status": "success",
                "event_id": result_data["id"],
                "event_url": result_data.get("html_link"),
                "message": "Calendar event created with AI-generated agenda"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create calendar event: {str(e)}"
            }



