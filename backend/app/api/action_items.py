"""Action item endpoints."""
import uuid
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware import require_org_access
from app.models import ActionItem

router = APIRouter()


class ActionItemUpdate(BaseModel):
    """Action item update request."""
    title: Optional[str] = None
    description: Optional[str] = None
    owner_name: Optional[str] = None
    owner_email: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[str] = None


class ActionItemResponse(BaseModel):
    """Action item response."""
    id: str
    meeting_id: str
    title: str
    description: Optional[str] = None
    owner_name: Optional[str] = None
    owner_email: Optional[str] = None
    status: str
    due_date: Optional[str] = None
    priority: Optional[str] = None
    confidence: Optional[float] = None
    created_at: str
    
    class Config:
        from_attributes = True


@router.get("/", response_model=list[ActionItemResponse])
async def list_action_items(
    request: Request,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """List action items for organization."""
    org_id, _ = auth
    
    query = select(ActionItem).where(ActionItem.org_id == org_id)
    
    if status_filter:
        query = query.where(ActionItem.status == status_filter)
    
    query = query.order_by(ActionItem.created_at.desc())
    
    result = await db.execute(query)
    action_items = result.scalars().all()
    
    return [
        ActionItemResponse(
            id=str(a.id),
            meeting_id=str(a.meeting_id),
            title=a.title,
            description=a.description,
            owner_name=a.owner_name,
            owner_email=a.owner_email,
            status=a.status,
            due_date=str(a.due_date) if a.due_date else None,
            priority=a.priority,
            confidence=a.confidence,
            created_at=a.created_at.isoformat(),
        )
        for a in action_items
    ]


@router.patch("/{action_item_id}", response_model=ActionItemResponse)
async def update_action_item(
    action_item_id: uuid.UUID,
    item_data: ActionItemUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """Update action item."""
    org_id, _ = auth
    
    result = await db.execute(
        select(ActionItem)
        .where(ActionItem.id == action_item_id)
        .where(ActionItem.org_id == org_id)
    )
    action_item = result.scalar_one_or_none()
    
    if not action_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action item not found",
        )
    
    # Update fields
    if item_data.title:
        action_item.title = item_data.title
    if item_data.description is not None:
        action_item.description = item_data.description
    if item_data.owner_name is not None:
        action_item.owner_name = item_data.owner_name
    if item_data.owner_email is not None:
        action_item.owner_email = item_data.owner_email
    if item_data.status:
        action_item.status = item_data.status
    if item_data.due_date is not None:
        action_item.due_date = item_data.due_date
    if item_data.priority is not None:
        action_item.priority = item_data.priority
    
    await db.commit()
    await db.refresh(action_item)
    
    return ActionItemResponse(
        id=str(action_item.id),
        meeting_id=str(action_item.meeting_id),
        title=action_item.title,
        description=action_item.description,
        owner_name=action_item.owner_name,
        owner_email=action_item.owner_email,
        status=action_item.status,
        due_date=str(action_item.due_date) if action_item.due_date else None,
        priority=action_item.priority,
        confidence=action_item.confidence,
        created_at=action_item.created_at.isoformat(),
    )





