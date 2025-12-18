"""Integration endpoints."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware import require_role
from app.models import Integration

router = APIRouter()


class IntegrationCreate(BaseModel):
    """Integration creation request."""
    provider: str  # linear, google, openai, klang, mistral
    config: Optional[dict] = None
    secrets: dict  # Will be encrypted


class IntegrationResponse(BaseModel):
    """Integration response."""
    id: str
    provider: str
    enabled: bool
    config: Optional[dict] = None
    created_at: str
    
    class Config:
        from_attributes = True


@router.get("/", response_model=list[IntegrationResponse])
async def list_integrations(
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_role("member")),
):
    """List organization integrations."""
    org_id, _ = auth
    
    result = await db.execute(
        select(Integration)
        .where(Integration.org_id == org_id)
        .order_by(Integration.provider)
    )
    integrations = result.scalars().all()
    
    return [
        IntegrationResponse(
            id=str(i.id),
            provider=i.provider,
            enabled=i.enabled,
            config=i.config,
            created_at=i.created_at.isoformat(),
        )
        for i in integrations
    ]


@router.post("/", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    integration_data: IntegrationCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_role("admin")),
):
    """
    Create integration.
    Requires admin role.
    """
    org_id, _ = auth
    
    # Check if integration already exists
    result = await db.execute(
        select(Integration)
        .where(Integration.org_id == org_id)
        .where(Integration.provider == integration_data.provider)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Integration for {integration_data.provider} already exists",
        )
    
    # In production: encrypt secrets with ENCRYPTION_KEY
    # For now, store as JSON (NOT SECURE - placeholder only)
    import json
    secrets_encrypted = json.dumps(integration_data.secrets)
    
    integration = Integration(
        org_id=org_id,
        provider=integration_data.provider,
        enabled=True,
        config=integration_data.config,
        secrets_encrypted=secrets_encrypted,
    )
    
    db.add(integration)
    await db.commit()
    await db.refresh(integration)
    
    return IntegrationResponse(
        id=str(integration.id),
        provider=integration.provider,
        enabled=integration.enabled,
        config=integration.config,
        created_at=integration.created_at.isoformat(),
    )


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_role("admin")),
):
    """Delete integration."""
    org_id, _ = auth
    
    result = await db.execute(
        select(Integration)
        .where(Integration.id == integration_id)
        .where(Integration.org_id == org_id)
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )
    
    await db.delete(integration)
    await db.commit()
    
    return None





