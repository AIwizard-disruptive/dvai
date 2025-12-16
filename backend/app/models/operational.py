"""Operational models for processing and integrations."""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin


class ProcessingRun(Base, UUIDMixin, TimestampMixin):
    """Processing run tracking."""
    
    __tablename__ = "processing_runs"
    
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orgs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    meeting_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=True,
    )
    
    artifact_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("artifacts.id", ondelete="CASCADE"),
        nullable=True,
    )
    
    stage: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )  # ingest, transcribe, extract, sync_linear, sync_google_email, sync_google_calendar
    
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="queued",
    )  # queued, running, succeeded, failed
    
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    run_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    __table_args__ = (
        Index("ix_processing_runs_org_id", "org_id"),
        Index("ix_processing_runs_meeting", "meeting_id"),
        Index("ix_processing_runs_status", "status"),
        Index("ix_processing_runs_stage", "stage"),
    )


class ExternalRef(Base, UUIDMixin, TimestampMixin):
    """External reference for synced items."""
    
    __tablename__ = "external_refs"
    
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orgs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    local_table: Mapped[str] = mapped_column(String(100), nullable=False)
    local_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # linear, google
    
    kind: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # linear_issue, gmail_draft, gmail_message, google_event, calendar_proposal
    
    external_id: Mapped[str] = mapped_column(String(500), nullable=False)
    external_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    sync_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    __table_args__ = (
        Index("ix_external_refs_org_id", "org_id"),
        Index("ix_external_refs_local", "local_table", "local_id"),
        Index("ix_external_refs_provider_kind", "provider", "kind"),
        Index("ix_external_refs_external_id", "external_id"),
    )


class Integration(Base, UUIDMixin, TimestampMixin):
    """Integration configuration."""
    
    __tablename__ = "integrations"
    
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orgs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # linear, google, openai, klang, mistral
    
    enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    # Non-secret configuration
    config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Encrypted secrets (encrypted with ENCRYPTION_KEY)
    secrets_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    __table_args__ = (
        Index("ix_integrations_org_provider", "org_id", "provider", unique=True),
    )

