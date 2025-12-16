"""API routes."""
from app.api.auth import router as auth_router
from app.api.orgs import router as orgs_router
from app.api.meetings import router as meetings_router
from app.api.artifacts import router as artifacts_router
from app.api.action_items import router as action_items_router
from app.api.decisions import router as decisions_router
from app.api.integrations import router as integrations_router
from app.api.sync import router as sync_router
from app.api.calendar import router as calendar_router
from app.api.meeting_with_agenda import router as meeting_with_agenda_router

__all__ = [
    "auth_router",
    "orgs_router",
    "meetings_router",
    "artifacts_router",
    "action_items_router",
    "decisions_router",
    "integrations_router",
    "sync_router",
    "calendar_router",
    "meeting_with_agenda_router",
]

