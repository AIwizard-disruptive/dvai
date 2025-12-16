"""Artifact endpoints."""
import uuid
import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware import require_org_access, get_user_org
from app.models import Artifact
from app.config import settings

router = APIRouter()


class ArtifactResponse(BaseModel):
    """Artifact response."""
    id: str
    filename: str
    file_type: str
    file_size: Optional[int] = None
    transcription_status: str
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("/upload")
async def upload_artifact(
    file: UploadFile = File(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(get_user_org),
):
    """
    Upload an artifact with authentication.
    
    Automatically uses the authenticated user's organization.
    Saves to database and triggers AI processing.
    """
    org_id, user = auth
    
    # Determine file type
    filename = file.filename
    if filename.endswith(".docx"):
        file_type = "docx"
    elif filename.endswith((".mp3", ".wav", ".m4a", ".ogg")):
        file_type = "audio"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type",
        )
    
    # In production: upload to Supabase Storage
    # For now, create placeholder
    artifact_id = uuid.uuid4()
    storage_path = f"orgs/{org_id}/artifacts/{artifact_id}/{filename}"
    
    # Save file locally (placeholder)
    import os
    os.makedirs(f"/tmp/artifacts/{artifact_id}", exist_ok=True)
    file_path = f"/tmp/artifacts/{artifact_id}/{filename}"
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Calculate file size and hash
    file_size = os.path.getsize(file_path)
    
    # Create artifact record
    artifact = Artifact(
        id=artifact_id,
        org_id=org_id,
        filename=filename,
        file_type=file_type,
        file_size=file_size,
        storage_path=storage_path,
        transcription_status="pending",
    )
    
    db.add(artifact)
    await db.commit()
    await db.refresh(artifact)
    
    # Trigger processing
    from app.worker.tasks.pipeline import process_artifact
    process_artifact.delay(str(artifact.id), str(org_id))
    
    return {
        "id": str(artifact.id),
        "filename": artifact.filename,
        "file_type": artifact.file_type,
        "status": "uploaded",
    }


@router.post("/upload-dev")
async def upload_artifact_dev(
    file: UploadFile = File(...),
):
    """
    DEV ONLY: Upload an artifact without authentication.
    
    DISABLED FOR PRODUCTION - Use /artifacts/upload with authentication instead.
    """
    # DISABLED - Always require authentication
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Dev endpoint disabled. Please use /artifacts/upload with authentication.",
    )
    
    # Determine file type
    filename = file.filename
    if filename.endswith((".docx", ".doc")):
        file_type = "docx"
    elif filename.endswith((".mp3", ".wav", ".m4a", ".ogg")):
        file_type = "audio"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Supported: .docx, .doc, .mp3, .wav, .m4a, .ogg",
        )
    
    # Save file locally for development
    artifact_id = uuid.uuid4()
    os.makedirs(f"/tmp/dev-uploads/{artifact_id}", exist_ok=True)
    file_path = f"/tmp/dev-uploads/{artifact_id}/{filename}"
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    file_size = os.path.getsize(file_path)
    
    return {
        "id": str(artifact_id),
        "filename": filename,
        "file_type": file_type,
        "file_size": file_size,
        "status": "uploaded",
        "mode": "development",
        "message": "File saved locally. Database and processing disabled in dev mode.",
        "path": file_path
    }


@router.get("/", response_model=list[ArtifactResponse])
async def list_artifacts(
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """List artifacts."""
    org_id, _ = auth
    
    result = await db.execute(
        select(Artifact)
        .where(Artifact.org_id == org_id)
        .order_by(Artifact.created_at.desc())
        .limit(50)
    )
    artifacts = result.scalars().all()
    
    return [
        ArtifactResponse(
            id=str(a.id),
            filename=a.filename,
            file_type=a.file_type,
            file_size=a.file_size,
            transcription_status=a.transcription_status,
            created_at=a.created_at.isoformat(),
        )
        for a in artifacts
    ]


@router.get("/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(
    artifact_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """Get artifact details."""
    org_id, _ = auth
    
    result = await db.execute(
        select(Artifact)
        .where(Artifact.id == artifact_id)
        .where(Artifact.org_id == org_id)
    )
    artifact = result.scalar_one_or_none()
    
    if not artifact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact not found",
        )
    
    return ArtifactResponse(
        id=str(artifact.id),
        filename=artifact.filename,
        file_type=artifact.file_type,
        file_size=artifact.file_size,
        transcription_status=artifact.transcription_status,
        created_at=artifact.created_at.isoformat(),
    )


@router.delete("/{artifact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_artifact(
    artifact_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_org_access),
):
    """Delete artifact."""
    org_id, _ = auth
    
    result = await db.execute(
        select(Artifact)
        .where(Artifact.id == artifact_id)
        .where(Artifact.org_id == org_id)
    )
    artifact = result.scalar_one_or_none()
    
    if not artifact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact not found",
        )
    
    # In production: delete from Supabase Storage
    
    await db.delete(artifact)
    await db.commit()
    
    return None

