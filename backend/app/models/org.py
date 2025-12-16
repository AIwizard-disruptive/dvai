"""Organization and membership models."""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin


class Org(Base, UUIDMixin, TimestampMixin):
    """Organization model."""
    
    __tablename__ = "orgs"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    memberships: Mapped[list["OrgMembership"]] = relationship(
        back_populates="org",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Org(id={self.id}, name={self.name})>"


class OrgMembership(Base, UUIDMixin, TimestampMixin):
    """Organization membership model."""
    
    __tablename__ = "org_memberships"
    
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orgs.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # References Supabase auth.users.id
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="member",
    )  # owner, admin, member, viewer
    
    # Relationships
    org: Mapped["Org"] = relationship(back_populates="memberships")
    
    __table_args__ = (
        Index("ix_org_memberships_org_user", "org_id", "user_id", unique=True),
        Index("ix_org_memberships_user_id", "user_id"),
    )
    
    def __repr__(self) -> str:
        return f"<OrgMembership(org_id={self.org_id}, user_id={self.user_id}, role={self.role})>"

