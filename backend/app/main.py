"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk

from app.config import settings
from app.database import init_db, close_db
from app.middleware import AuthMiddleware
from app.api import (
    auth_router,
    orgs_router,
    meetings_router,
    artifacts_router,
    action_items_router,
    decisions_router,
    integrations_router,
    sync_router,
    calendar_router,
    meeting_with_agenda_router,
)
from app.api.upload_ui import router as upload_ui_router
from app.api.upload_protected import router as upload_protected_router
from app.api.login_ui import router as login_ui_router
from app.api.recording_ui import router as recording_ui_router
from app.api.dashboard import router as dashboard_router
from app.api.meeting_view import router as meeting_view_router
from app.api.upload_simple import router as upload_simple_router
from app.api.meeting_automation import router as automation_router
from app.api.generate_docs import router as generate_docs_router
from app.api.documents import router as documents_router
from app.api.task_assistance import router as task_assistance_router
from app.api.document_viewer import router as document_viewer_router
from app.api.personal_agenda import router as personal_agenda_router
from app.api.integration_test import router as integration_test_router
from app.api.user_integrations import router as user_integrations_router
from app.api.marcus_test_distribution import router as marcus_test_router
from app.api.create_linear_from_meeting import router as linear_sync_router
from app.api.knowledge_bank import router as knowledge_router
from app.api.linear_sync import router as linear_sync_router


# Initialize Sentry if configured
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.env,
        traces_sample_rate=0.1 if settings.env == "production" else 1.0,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager."""
    # Startup
    try:
        await init_db()
        print("✓ Database connected successfully")
    except Exception as e:
        print(f"⚠ Database connection failed: {e}")
        print("⚠ Server will run in limited mode (upload UI available, but API endpoints disabled)")
    yield
    # Shutdown
    try:
        await close_db()
    except Exception:
        pass


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth middleware
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(login_ui_router, tags=["Login UI"])
app.include_router(recording_ui_router, tags=["Recording UI"])
app.include_router(upload_ui_router, tags=["Upload UI"])
app.include_router(upload_protected_router, tags=["Upload UI"])
app.include_router(upload_simple_router, tags=["Upload"])
app.include_router(dashboard_router, tags=["Dashboard"])
app.include_router(meeting_view_router, tags=["Meeting View"])
app.include_router(personal_agenda_router, tags=["Personal Agenda"])
app.include_router(automation_router, prefix="/automation", tags=["Automation"])
app.include_router(integration_test_router, tags=["Integrations"])
app.include_router(user_integrations_router, tags=["User Integrations"])
app.include_router(marcus_test_router, tags=["Marcus Test"])
app.include_router(linear_sync_router, tags=["Linear Sync"])
app.include_router(linear_sync_router, tags=["Linear Sync"])
app.include_router(generate_docs_router, prefix="/docs", tags=["Document Generation"])
app.include_router(documents_router, prefix="/documents", tags=["Documents"])
app.include_router(task_assistance_router, prefix="/tasks", tags=["Task Assistance"])
app.include_router(document_viewer_router, prefix="/viewer", tags=["Document Viewer"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(orgs_router, prefix="/orgs", tags=["Organizations"])
app.include_router(meetings_router, prefix="/meetings", tags=["Meetings"])
app.include_router(artifacts_router, prefix="/artifacts", tags=["Artifacts"])
app.include_router(action_items_router, prefix="/action-items", tags=["Action Items"])
app.include_router(decisions_router, prefix="/decisions", tags=["Decisions"])
app.include_router(integrations_router, prefix="/integrations", tags=["Integrations"])
app.include_router(sync_router, prefix="/sync", tags=["Sync"])
app.include_router(calendar_router, prefix="/calendar", tags=["Calendar"])
app.include_router(meeting_with_agenda_router, tags=["AI Agenda"])
app.include_router(knowledge_router, tags=["Knowledge Bank"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.env,
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Meeting Intelligence Platform API",
        "version": "1.0.0",
        "docs_url": "/docs" if settings.debug else None,
    }

