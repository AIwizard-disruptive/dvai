"""
Layer 1: ASR Ingestion Service
Stores verbatim transcripts without modification
ZERO FABRICATION POLICY
"""
import hashlib
import uuid
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

class SpeakerSegment(BaseModel):
    """Raw speaker segment from ASR"""
    speaker_id: str  # "SPEAKER_0", "SPEAKER_1" - NOT real names
    start_time: float
    end_time: float
    text: str
    confidence: float

class RawTranscriptInput(BaseModel):
    """Input for raw transcript ingestion"""
    artifact_id: uuid.UUID
    org_id: uuid.UUID
    transcript_text: str
    language: Optional[str] = None
    confidence: Optional[float] = None
    speaker_segments: List[SpeakerSegment]
    source_provider: str  # "klang", "mistral", "openai", "manual"
    source_metadata: Optional[Dict] = None

class Layer1IngestionService:
    """
    Layer 1: Verbatim transcript storage
    
    RULES:
    - Store exactly what ASR returns, no modifications
    - Never assign real names (use SPEAKER_0, etc.)
    - Never correct or "fix" transcript
    - Never merge or split speakers
    - Hash content for integrity
    - Log issues but don't reject
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def ingest_transcript(
        self,
        input: RawTranscriptInput,
        correlation_id: str
    ) -> uuid.UUID:
        """
        Ingest raw transcript from ASR provider
        
        Returns: transcript_raw_id
        Raises: Never - logs issues instead
        """
        # Generate content hash for integrity
        content_hash = self._compute_hash(
            input.transcript_text,
            input.speaker_segments
        )
        
        # Validate - log issues but don't reject
        issues = self._validate_input(input)
        if issues:
            await self._log_issues(issues, correlation_id, input.org_id)
        
        # Store verbatim
        transcript_id = uuid.uuid4()
        
        query = """
        INSERT INTO transcripts_raw (
            id, artifact_id, org_id,
            transcript_text, language, confidence,
            speaker_segments, speaker_count,
            source_provider, source_metadata,
            sha256_hash, processing_timestamp
        ) VALUES (
            :id, :artifact_id, :org_id,
            :transcript_text, :language, :confidence,
            :speaker_segments, :speaker_count,
            :source_provider, :source_metadata,
            :sha256_hash, :processing_timestamp
        )
        """
        
        await self.db.execute(query, {
            "id": transcript_id,
            "artifact_id": input.artifact_id,
            "org_id": input.org_id,
            "transcript_text": input.transcript_text,
            "language": input.language,
            "confidence": input.confidence,
            "speaker_segments": [s.dict() for s in input.speaker_segments],
            "speaker_count": len(set(s.speaker_id for s in input.speaker_segments)),
            "source_provider": input.source_provider,
            "source_metadata": input.source_metadata or {},
            "sha256_hash": content_hash,
            "processing_timestamp": datetime.utcnow()
        })
        
        await self.db.commit()
        
        # Audit log
        await self._audit_log(
            action="layer1_ingest",
            resource_id=transcript_id,
            org_id=input.org_id,
            correlation_id=correlation_id,
            metadata={
                "source_provider": input.source_provider,
                "speaker_count": len(set(s.speaker_id for s in input.speaker_segments)),
                "transcript_length": len(input.transcript_text),
                "content_hash": content_hash
            }
        )
        
        return transcript_id
    
    def _compute_hash(self, text: str, segments: List[SpeakerSegment]) -> str:
        """Compute SHA256 hash of transcript content for integrity"""
        content = f"{text}|{'|'.join(s.json() for s in segments)}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _validate_input(self, input: RawTranscriptInput) -> List[Dict]:
        """
        Validate input and return issues (NEVER reject)
        
        Issues logged, not raised:
        - Low confidence
        - Missing timestamps
        - Empty segments
        - Suspicious speaker IDs (looks like real names)
        """
        issues = []
        
        # Check confidence
        if input.confidence and input.confidence < 0.7:
            issues.append({
                "type": "low_confidence",
                "severity": "warning",
                "description": f"Overall confidence {input.confidence} below 0.7",
                "evidence": {"confidence": input.confidence}
            })
        
        # Check for missing timestamps
        for i, segment in enumerate(input.speaker_segments):
            if segment.start_time is None or segment.end_time is None:
                issues.append({
                    "type": "missing_data",
                    "severity": "warning",
                    "description": f"Segment {i} missing timestamps",
                    "evidence": {"segment_index": i, "speaker_id": segment.speaker_id}
                })
            
            # Check if speaker_id looks like a real name (violation!)
            if not segment.speaker_id.startswith("SPEAKER_"):
                issues.append({
                    "type": "fabrication_risk",
                    "severity": "critical",
                    "description": f"Speaker ID '{segment.speaker_id}' looks like real name, not anonymous ID",
                    "evidence": {"speaker_id": segment.speaker_id}
                })
        
        # Check for empty transcript
        if not input.transcript_text or len(input.transcript_text.strip()) == 0:
            issues.append({
                "type": "missing_data",
                "severity": "critical",
                "description": "Transcript text is empty",
                "evidence": {}
            })
        
        return issues
    
    async def _log_issues(
        self,
        issues: List[Dict],
        correlation_id: str,
        org_id: uuid.UUID
    ):
        """Log validation issues (not failures)"""
        for issue in issues:
            query = """
            INSERT INTO issues (
                id, org_id, issue_type, severity,
                description, evidence
            ) VALUES (
                :id, :org_id, :issue_type, :severity,
                :description, :evidence
            )
            """
            await self.db.execute(query, {
                "id": uuid.uuid4(),
                "org_id": org_id,
                "issue_type": issue["type"],
                "severity": issue["severity"],
                "description": issue["description"],
                "evidence": issue["evidence"]
            })
    
    async def _audit_log(
        self,
        action: str,
        resource_id: uuid.UUID,
        org_id: uuid.UUID,
        correlation_id: str,
        metadata: Dict
    ):
        """Create audit log entry"""
        query = """
        INSERT INTO audit_logs (
            id, timestamp, correlation_id,
            org_id, action, resource_type, resource_id,
            success, changes
        ) VALUES (
            :id, :timestamp, :correlation_id,
            :org_id, :action, :resource_type, :resource_id,
            :success, :changes
        )
        """
        await self.db.execute(query, {
            "id": uuid.uuid4(),
            "timestamp": datetime.utcnow(),
            "correlation_id": correlation_id,
            "org_id": org_id,
            "action": action,
            "resource_type": "transcript_raw",
            "resource_id": resource_id,
            "success": True,
            "changes": metadata
        })



