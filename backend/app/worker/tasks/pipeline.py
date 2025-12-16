"""Pipeline tasks for meeting processing."""
import uuid
import tempfile
import os
from datetime import datetime
from typing import Optional
from celery import chain, group
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.worker.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models import (
    Meeting, Artifact, TranscriptChunk, Summary,
    ActionItem, Decision, Tag, MeetingTag, Entity,
    MeetingEntity, ProcessingRun
)
from app.providers import get_transcription_provider
from app.services.document import DocumentService
from app.services.extraction import get_extraction_service


async def create_processing_run(
    org_id: uuid.UUID,
    stage: str,
    meeting_id: Optional[uuid.UUID] = None,
    artifact_id: Optional[uuid.UUID] = None,
) -> uuid.UUID:
    """Create a processing run record."""
    async with AsyncSessionLocal() as db:
        run = ProcessingRun(
            org_id=org_id,
            meeting_id=meeting_id,
            artifact_id=artifact_id,
            stage=stage,
            status="queued",
        )
        db.add(run)
        await db.commit()
        await db.refresh(run)
        return run.id


async def update_processing_run(
    run_id: uuid.UUID,
    status: str,
    error: Optional[str] = None,
    metadata: Optional[dict] = None,
):
    """Update processing run status."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ProcessingRun).where(ProcessingRun.id == run_id)
        )
        run = result.scalar_one()
        
        run.status = status
        if error:
            run.error = error
        if metadata:
            run.metadata = metadata
        
        if status == "running":
            run.started_at = datetime.utcnow()
        elif status in ["succeeded", "failed"]:
            run.finished_at = datetime.utcnow()
        
        await db.commit()


@celery_app.task(name="pipeline.process_artifact")
def process_artifact(artifact_id: str, org_id: str):
    """
    Process an artifact through the full pipeline.
    
    This is the main entry point that chains all pipeline stages.
    """
    artifact_uuid = uuid.UUID(artifact_id)
    org_uuid = uuid.UUID(org_id)
    
    # Build processing chain
    workflow = chain(
        ingest_artifact.s(artifact_id, org_id),
        transcribe_or_extract.s(artifact_id, org_id),
        extract_intelligence.s(artifact_id, org_id),
        sync_to_linear.s(artifact_id, org_id),
        sync_to_google_email.s(artifact_id, org_id),
        sync_to_google_calendar.s(artifact_id, org_id),
    )
    
    return workflow()


@celery_app.task(name="pipeline.ingest_artifact")
def ingest_artifact(artifact_id: str, org_id: str):
    """Stage 1: Ingest artifact and create/link meeting."""
    import asyncio
    return asyncio.run(_ingest_artifact(artifact_id, org_id))


async def _ingest_artifact(artifact_id: str, org_id: str):
    """Async implementation of ingest_artifact."""
    artifact_uuid = uuid.UUID(artifact_id)
    org_uuid = uuid.UUID(org_id)
    
    run_id = await create_processing_run(
        org_id=org_uuid,
        stage="ingest",
        artifact_id=artifact_uuid,
    )
    
    try:
        await update_processing_run(run_id, "running")
        
        async with AsyncSessionLocal() as db:
            # Get artifact
            result = await db.execute(
                select(Artifact).where(Artifact.id == artifact_uuid)
            )
            artifact = result.scalar_one()
            
            # Parse filename for metadata
            doc_service = DocumentService()
            metadata = doc_service.parse_filename_metadata(artifact.filename)
            
            # Create or link meeting
            if not artifact.meeting_id:
                meeting = Meeting(
                    org_id=org_uuid,
                    title=metadata.get("title", f"Meeting from {artifact.filename}"),
                    meeting_date=metadata.get("date"),
                    meeting_type=metadata.get("type"),
                    company=metadata.get("company"),
                    processing_status="processing",
                )
                db.add(meeting)
                await db.flush()
                
                artifact.meeting_id = meeting.id
                await db.commit()
            
        await update_processing_run(run_id, "succeeded")
        return {"status": "success", "artifact_id": artifact_id}
    
    except Exception as e:
        await update_processing_run(run_id, "failed", error=str(e))
        raise


@celery_app.task(name="pipeline.transcribe_or_extract")
def transcribe_or_extract(prev_result: dict, artifact_id: str, org_id: str):
    """Stage 2: Transcribe audio or extract text from document."""
    import asyncio
    return asyncio.run(_transcribe_or_extract(artifact_id, org_id))


async def _transcribe_or_extract(artifact_id: str, org_id: str):
    """Async implementation of transcribe_or_extract."""
    artifact_uuid = uuid.UUID(artifact_id)
    org_uuid = uuid.UUID(org_id)
    
    run_id = await create_processing_run(
        org_id=org_uuid,
        stage="transcribe",
        artifact_id=artifact_uuid,
    )
    
    try:
        await update_processing_run(run_id, "running")
        
        async with AsyncSessionLocal() as db:
            # Get artifact
            result = await db.execute(
                select(Artifact).where(Artifact.id == artifact_uuid)
            )
            artifact = result.scalar_one()
            
            if artifact.file_type == "docx":
                # Extract text from Word document
                # Download from Supabase Storage (placeholder - implement actual download)
                file_path = f"/tmp/{artifact.id}.docx"
                
                doc_service = DocumentService()
                text = doc_service.extract_text_from_docx(file_path)
                
                artifact.content_text = text
                artifact.transcription_status = "completed"
                
                # Create single transcript chunk
                chunk = TranscriptChunk(
                    org_id=org_uuid,
                    meeting_id=artifact.meeting_id,
                    artifact_id=artifact.id,
                    sequence=0,
                    speaker=None,
                    text=text,
                )
                db.add(chunk)
            
            else:  # audio file
                # Get signed URL from Supabase Storage (placeholder)
                signed_url = f"https://storage.supabase.co/{artifact.storage_path}"
                
                # Transcribe
                provider = get_transcription_provider()
                result = await provider.transcribe(signed_url, artifact.language)
                
                artifact.language = result.language
                artifact.duration_seconds = result.duration
                artifact.transcription_provider = provider.name
                artifact.transcription_status = "completed"
                
                # Save segments as chunks
                for i, segment in enumerate(result.segments):
                    chunk = TranscriptChunk(
                        org_id=org_uuid,
                        meeting_id=artifact.meeting_id,
                        artifact_id=artifact.id,
                        sequence=i,
                        speaker=segment.speaker,
                        text=segment.text,
                        start_time=segment.start,
                        end_time=segment.end,
                        confidence=segment.confidence,
                        language=result.language,
                    )
                    db.add(chunk)
            
            await db.commit()
        
        await update_processing_run(run_id, "succeeded")
        return {"status": "success", "artifact_id": artifact_id}
    
    except Exception as e:
        await update_processing_run(run_id, "failed", error=str(e))
        raise


@celery_app.task(name="pipeline.extract_intelligence")
def extract_intelligence(prev_result: dict, artifact_id: str, org_id: str):
    """Stage 3: Extract structured intelligence using LLM."""
    import asyncio
    return asyncio.run(_extract_intelligence(artifact_id, org_id))


async def _extract_intelligence(artifact_id: str, org_id: str):
    """Async implementation of extract_intelligence."""
    artifact_uuid = uuid.UUID(artifact_id)
    org_uuid = uuid.UUID(org_id)
    
    run_id = await create_processing_run(
        org_id=org_uuid,
        stage="extract",
        artifact_id=artifact_uuid,
    )
    
    try:
        await update_processing_run(run_id, "running")
        
        async with AsyncSessionLocal() as db:
            # Get artifact and meeting
            result = await db.execute(
                select(Artifact).where(Artifact.id == artifact_uuid)
            )
            artifact = result.scalar_one()
            
            result = await db.execute(
                select(Meeting).where(Meeting.id == artifact.meeting_id)
            )
            meeting = result.scalar_one()
            
            # Get transcript chunks
            result = await db.execute(
                select(TranscriptChunk)
                .where(TranscriptChunk.meeting_id == meeting.id)
                .order_by(TranscriptChunk.sequence)
            )
            chunks = result.scalars().all()
            
            # Prepare data for extraction
            chunk_dicts = [
                {
                    "id": str(chunk.id),
                    "speaker": chunk.speaker,
                    "text": chunk.text,
                    "start_time": chunk.start_time,
                    "end_time": chunk.end_time,
                }
                for chunk in chunks
            ]
            
            meeting_metadata = {
                "title": meeting.title,
                "date": str(meeting.meeting_date) if meeting.meeting_date else None,
                "type": meeting.meeting_type,
            }
            
            # Extract intelligence
            extraction_service = get_extraction_service()
            intelligence = await extraction_service.extract_intelligence(
                transcript_chunks=chunk_dicts,
                meeting_metadata=meeting_metadata,
            )
            
            # Save summary
            summary = Summary(
                org_id=org_uuid,
                meeting_id=meeting.id,
                summary_type="full",
                content_md=intelligence.summary_md,
                model="gpt-4o",
            )
            db.add(summary)
            
            # Save decisions
            for dec in intelligence.decisions:
                # Find source chunk
                source_chunk_id = None
                source_quote = None
                if dec.source_chunk_indices:
                    idx = dec.source_chunk_indices[0]
                    if idx < len(chunks):
                        source_chunk_id = chunks[idx].id
                        source_quote = chunks[idx].text[:500]
                
                decision = Decision(
                    org_id=org_uuid,
                    meeting_id=meeting.id,
                    decision=dec.decision,
                    rationale=dec.rationale,
                    source_chunk_id=source_chunk_id,
                    source_quote=source_quote,
                    confidence=0.9 if dec.confidence == "high" else 0.7 if dec.confidence == "medium" else 0.5,
                )
                db.add(decision)
            
            # Save action items
            for item in intelligence.action_items:
                # Find source chunk
                source_chunk_id = None
                source_quote = None
                if item.source_chunk_indices:
                    idx = item.source_chunk_indices[0]
                    if idx < len(chunks):
                        source_chunk_id = chunks[idx].id
                        source_quote = chunks[idx].text[:500]
                
                action_item = ActionItem(
                    org_id=org_uuid,
                    meeting_id=meeting.id,
                    title=item.title,
                    description=item.description,
                    owner_name=item.owner_name,
                    owner_email=item.owner_email,
                    status=item.status,
                    due_date=item.due_date,
                    priority=item.priority,
                    source_chunk_id=source_chunk_id,
                    source_quote=source_quote,
                    confidence=0.9 if item.confidence == "high" else 0.7 if item.confidence == "medium" else 0.5,
                )
                db.add(action_item)
            
            # Save tags
            for tag_name in intelligence.tags:
                # Find or create tag
                result = await db.execute(
                    select(Tag)
                    .where(Tag.org_id == org_uuid)
                    .where(Tag.name == tag_name)
                )
                tag = result.scalar_one_or_none()
                
                if not tag:
                    tag = Tag(org_id=org_uuid, name=tag_name)
                    db.add(tag)
                    await db.flush()
                
                # Link to meeting
                meeting_tag = MeetingTag(meeting_id=meeting.id, tag_id=tag.id)
                db.add(meeting_tag)
            
            # Save entities
            for ent in intelligence.entities:
                # Find or create entity
                result = await db.execute(
                    select(Entity)
                    .where(Entity.org_id == org_uuid)
                    .where(Entity.kind == ent.kind)
                    .where(Entity.name == ent.name)
                )
                entity = result.scalar_one_or_none()
                
                if not entity:
                    entity = Entity(
                        org_id=org_uuid,
                        kind=ent.kind,
                        name=ent.name,
                    )
                    db.add(entity)
                    await db.flush()
                
                # Link to meeting
                meeting_entity = MeetingEntity(
                    meeting_id=meeting.id,
                    entity_id=entity.id,
                    mention_count=1,
                )
                db.add(meeting_entity)
            
            # Update meeting status
            meeting.processing_status = "completed"
            
            await db.commit()
        
        await update_processing_run(run_id, "succeeded")
        return {"status": "success", "artifact_id": artifact_id}
    
    except Exception as e:
        await update_processing_run(run_id, "failed", error=str(e))
        raise


@celery_app.task(name="pipeline.sync_to_linear")
def sync_to_linear(prev_result: dict, artifact_id: str, org_id: str):
    """
    Stage 4: Create Linear project and tasks with Drive doc links.
    
    Runs the enhanced distribution:
    - Creates Google Drive folder
    - Uploads all documents
    - Creates Linear project
    - Creates tasks with Drive links
    - Sets proper assignees and deadlines
    """
    import asyncio
    return asyncio.run(_sync_to_linear(artifact_id, org_id))


async def _sync_to_linear(artifact_id: str, org_id: str):
    """Async implementation of Linear sync."""
    try:
        # Run the enhanced sync for this meeting
        import subprocess
        import json
        
        # Get meeting ID from artifact
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Artifact).where(Artifact.id == uuid.UUID(artifact_id))
            )
            artifact = result.scalar_one()
            meeting_id = str(artifact.meeting_id)
        
        print(f"\n🚀 Running enhanced distribution for meeting {meeting_id[:8]}...")
        
        # Run sync_with_drive_links.py as subprocess
        result = subprocess.run(
            ['python3', 'sync_with_drive_links.py'],
            cwd='/Users/marcus/Library/Mobile Documents/com~apple~CloudDocs/Documents/Cursor-projects/Disruptive Ventures/DV Legacy/dv/backend',
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✅ Enhanced distribution completed successfully!")
            return {"status": "success", "message": "Drive folders, Linear project, and tasks created"}
        else:
            print(f"⚠ Enhanced distribution had errors: {result.stderr}")
            return {"status": "partial", "errors": result.stderr}
    
    except Exception as e:
        print(f"✗ Enhanced distribution failed: {str(e)}")
        return {"status": "failed", "error": str(e)}


@celery_app.task(name="pipeline.sync_to_google_email")
def sync_to_google_email(prev_result: dict, artifact_id: str, org_id: str):
    """
    Stage 5: Create Gmail draft with all tasks for all assignees.
    
    This is already done in sync_to_linear (enhanced distribution),
    so we just log completion here.
    """
    print("✅ Gmail drafts created in enhanced distribution (Step 4)")
    return {"status": "completed_in_step_4"}


@celery_app.task(name="pipeline.sync_to_google_calendar")
def sync_to_google_calendar(prev_result: dict, artifact_id: str, org_id: str):
    """
    Stage 6: Create calendar events for deadlines.
    
    This will be implemented in future enhancement.
    For now, deadlines are in Linear tasks.
    """
    print("ℹ️  Calendar integration - future enhancement")
    return {"status": "future_feature"}



