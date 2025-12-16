"""Meeting intelligence models."""
import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    String, Text, ForeignKey, DateTime, Date, Float, Integer,
    Boolean, Index, JSON
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin


class MeetingGroup(Base, UUIDMixin, TimestampMixin):
    """Meeting group (e.g., recurring series)."""
    
    __tablename__ = "meeting_groups"
    
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orgs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    meetings: Mapped[list["Meeting"]] = relationship(
        back_populates="meeting_group",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index("ix_meeting_groups_org_id", "org_id"),
    )


class Meeting(Base, UUIDMixin, TimestampMixin):
    """Meeting record."""
    
    __tablename__ = "meetings"
    
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orgs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    meeting_group_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meeting_groups.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    meeting_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    meeting_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Processing status
    processing_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )  # pending, processing, completed, failed
    
    # Meeting metadata
    meeting_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    meeting_group: Mapped[Optional["MeetingGroup"]] = relationship(
        back_populates="meetings"
    )
    artifacts: Mapped[list["Artifact"]] = relationship(
        back_populates="meeting",
        cascade="all, delete-orphan"
    )
    participants: Mapped[list["MeetingParticipant"]] = relationship(
        back_populates="meeting",
        cascade="all, delete-orphan"
    )
    transcript_chunks: Mapped[list["TranscriptChunk"]] = relationship(
        back_populates="meeting",
        cascade="all, delete-orphan"
    )
    summaries: Mapped[list["Summary"]] = relationship(
        back_populates="meeting",
        cascade="all, delete-orphan"
    )
    action_items: Mapped[list["ActionItem"]] = relationship(
        back_populates="meeting",
        cascade="all, delete-orphan"
    )
    decisions: Mapped[list["Decision"]] = relationship(
        back_populates="meeting",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index("ix_meetings_org_id", "org_id"),
        Index("ix_meetings_date", "meeting_date"),
        Index("ix_meetings_status", "processing_status"),
    )


class Person(Base, UUIDMixin, TimestampMixin):
    """Person entity."""
    
    __tablename__ = "people"
    
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orgs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    participations: Mapped[list["MeetingParticipant"]] = relationship(
        back_populates="person"
    )
    
    __table_args__ = (
        Index("ix_people_org_id", "org_id"),
        Index("ix_people_email", "email"),
    )


class MeetingParticipant(Base, UUIDMixin):
    """Meeting participant (many-to-many)."""
    
    __tablename__ = "meeting_participants"
    
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    person_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("people.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    attended: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    meeting: Mapped["Meeting"] = relationship(back_populates="participants")
    person: Mapped["Person"] = relationship(back_populates="participations")
    
    __table_args__ = (
        Index("ix_meeting_participants_meeting", "meeting_id"),
        Index("ix_meeting_participants_person", "person_id"),
    )


class Artifact(Base, UUIDMixin, TimestampMixin):
    """Meeting artifact (file)."""
    
    __tablename__ = "artifacts"
    
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
    
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # audio, docx, pdf
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # bytes
    
    # Storage
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    sha256: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Extracted content (for documents)
    content_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Audio metadata
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Processing
    transcription_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )  # pending, processing, completed, failed
    
    transcription_provider: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )  # klang, mistral, openai
    
    # Relationships
    meeting: Mapped[Optional["Meeting"]] = relationship(back_populates="artifacts")
    
    __table_args__ = (
        Index("ix_artifacts_org_id", "org_id"),
        Index("ix_artifacts_meeting_id", "meeting_id"),
        Index("ix_artifacts_sha256", "sha256"),
    )


class TranscriptChunk(Base, UUIDMixin, TimestampMixin):
    """Transcript chunk (segment)."""
    
    __tablename__ = "transcript_chunks"
    
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orgs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    artifact_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("artifacts.id", ondelete="CASCADE"),
        nullable=True,
    )
    
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    speaker: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Timing (for audio)
    start_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    end_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Quality
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Relationships
    meeting: Mapped["Meeting"] = relationship(back_populates="transcript_chunks")
    
    __table_args__ = (
        Index("ix_transcript_chunks_org_id", "org_id"),
        Index("ix_transcript_chunks_meeting", "meeting_id"),
        Index("ix_transcript_chunks_sequence", "meeting_id", "sequence"),
    )


class Summary(Base, UUIDMixin, TimestampMixin):
    """Meeting summary."""
    
    __tablename__ = "summaries"
    
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orgs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    summary_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="full",
    )  # full, executive, brief
    
    content_md: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Generation metadata
    model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Relationships
    meeting: Mapped["Meeting"] = relationship(back_populates="summaries")
    
    __table_args__ = (
        Index("ix_summaries_org_id", "org_id"),
        Index("ix_summaries_meeting", "meeting_id"),
    )


class ActionItem(Base, UUIDMixin, TimestampMixin):
    """Action item extracted from meeting."""
    
    __tablename__ = "action_items"
    
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orgs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    owner_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    owner_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="open",
    )  # open, in_progress, blocked, done, cancelled
    
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    priority: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Provenance
    source_chunk_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transcript_chunks.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_quote: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Relationships
    meeting: Mapped["Meeting"] = relationship(back_populates="action_items")
    
    __table_args__ = (
        Index("ix_action_items_org_id", "org_id"),
        Index("ix_action_items_meeting", "meeting_id"),
        Index("ix_action_items_status", "status"),
        Index("ix_action_items_owner", "owner_email"),
    )


class Decision(Base, UUIDMixin, TimestampMixin):
    """Decision made in meeting."""
    
    __tablename__ = "decisions"
    
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orgs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    decision: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Provenance
    source_chunk_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transcript_chunks.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_quote: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Relationships
    meeting: Mapped["Meeting"] = relationship(back_populates="decisions")
    
    __table_args__ = (
        Index("ix_decisions_org_id", "org_id"),
        Index("ix_decisions_meeting", "meeting_id"),
    )


class Tag(Base, UUIDMixin, TimestampMixin):
    """Tag for categorization."""
    
    __tablename__ = "tags"
    
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orgs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    __table_args__ = (
        Index("ix_tags_org_name", "org_id", "name", unique=True),
    )


class MeetingTag(Base, UUIDMixin):
    """Meeting-tag association."""
    
    __tablename__ = "meeting_tags"
    
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    __table_args__ = (
        Index("ix_meeting_tags_meeting", "meeting_id"),
        Index("ix_meeting_tags_tag", "tag_id"),
        Index("ix_meeting_tags_unique", "meeting_id", "tag_id", unique=True),
    )


class Entity(Base, UUIDMixin, TimestampMixin):
    """Named entity (person, company, product, etc)."""
    
    __tablename__ = "entities"
    
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orgs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    kind: Mapped[str] = mapped_column(String(50), nullable=False)  # person, company, product, location
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    canonical_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    __table_args__ = (
        Index("ix_entities_org_kind_name", "org_id", "kind", "name"),
    )


class MeetingEntity(Base, UUIDMixin):
    """Meeting-entity association."""
    
    __tablename__ = "meeting_entities"
    
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    mention_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    __table_args__ = (
        Index("ix_meeting_entities_meeting", "meeting_id"),
        Index("ix_meeting_entities_entity", "entity_id"),
        Index("ix_meeting_entities_unique", "meeting_id", "entity_id", unique=True),
    )


class Link(Base, UUIDMixin, TimestampMixin):
    """External link mentioned in meeting."""
    
    __tablename__ = "links"
    
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orgs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    url: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    __table_args__ = (
        Index("ix_links_org_id", "org_id"),
        Index("ix_links_meeting", "meeting_id"),
    )

