"""Organization endpoints."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware import get_current_user, require_org_access, require_role
from app.models import Org, OrgMembership

router = APIRouter()


class OrgCreate(BaseModel):
    """Organization creation request."""
    name: str


class OrgUpdate(BaseModel):
    """Organization update request."""
    name: Optional[str] = None
    settings: Optional[dict] = None


class OrgResponse(BaseModel):
    """Organization response."""
    id: str
    name: str
    role: str  # User's role in this org
    settings: Optional[dict] = None
    created_at: str
    
    class Config:
        from_attributes = True


@router.get("/", response_model=list[OrgResponse])
async def list_user_orgs(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List organizations user belongs to."""
    user_id = uuid.UUID(current_user["id"])
    
    # Get user's org memberships
    result = await db.execute(
        select(OrgMembership, Org)
        .join(Org, OrgMembership.org_id == Org.id)
        .where(OrgMembership.user_id == user_id)
    )
    
    orgs = []
    for membership, org in result.all():
        orgs.append(
            OrgResponse(
                id=str(org.id),
                name=org.name,
                role=membership.role,
                settings=org.settings,
                created_at=org.created_at.isoformat(),
            )
        )
    
    return orgs


@router.post("/", response_model=OrgResponse, status_code=status.HTTP_201_CREATED)
async def create_org(
    org_data: OrgCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new organization.
    User becomes owner.
    """
    user_id = uuid.UUID(current_user["id"])
    
    # Create org
    org = Org(name=org_data.name)
    db.add(org)
    await db.flush()
    
    # Create membership with owner role
    membership = OrgMembership(
        org_id=org.id,
        user_id=user_id,
        role="owner",
    )
    db.add(membership)
    
    await db.commit()
    await db.refresh(org)
    
    return OrgResponse(
        id=str(org.id),
        name=org.name,
        role="owner",
        settings=org.settings,
        created_at=org.created_at.isoformat(),
    )


@router.get("/{org_id}", response_model=OrgResponse)
async def get_org(
    org_id: uuid.UUID,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get organization details."""
    user_id = uuid.UUID(current_user["id"])
    
    # Get org
    result = await db.execute(
        select(Org).where(Org.id == org_id)
    )
    org = result.scalar_one_or_none()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    # Check membership
    result = await db.execute(
        select(OrgMembership)
        .where(OrgMembership.org_id == org_id)
        .where(OrgMembership.user_id == user_id)
    )
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    return OrgResponse(
        id=str(org.id),
        name=org.name,
        role=membership.role,
        settings=org.settings,
        created_at=org.created_at.isoformat(),
    )


@router.patch("/{org_id}", response_model=OrgResponse)
async def update_org(
    org_id: uuid.UUID,
    org_data: OrgUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_role("admin")),
):
    """
    Update organization.
    Requires admin role.
    """
    # Get org
    result = await db.execute(
        select(Org).where(Org.id == org_id)
    )
    org = result.scalar_one_or_none()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    # Update fields
    if org_data.name:
        org.name = org_data.name
    if org_data.settings is not None:
        org.settings = org_data.settings
    
    await db.commit()
    await db.refresh(org)
    
    return OrgResponse(
        id=str(org.id),
        name=org.name,
        role=request.state.org_role,
        settings=org.settings,
        created_at=org.created_at.isoformat(),
    )


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_org(
    org_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_role("owner")),
):
    """
    Delete organization.
    Requires owner role.
    """
    result = await db.execute(
        select(Org).where(Org.id == org_id)
    )
    org = result.scalar_one_or_none()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    await db.delete(org)
    await db.commit()
    
    return None




