"""
Layer 2: Normalization & GDPR Compliance Service
Transforms raw transcripts into normalized, compliant form
"""
import hashlib
import uuid
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.pii_detection import PIIDetectionService, PIIEntity

class NormalizedSegment(BaseModel):
    """Normalized transcript segment"""
    sequence: int
    speaker_raw_id: str  # Link to Layer 1
    speaker_normalized: Optional[str]  # Real name (if confirmed)
    text: str
    start_time: Optional[float]
    end_time: Optional[float]
    has_pii: bool
    pii_entity_ids: List[uuid.UUID]

class Layer2NormalizationService:
    """
    Layer 2: Normalization + GDPR
    
    Responsibilities:
    - Segment transcript logically
    - Map speakers (with user confirmation)
    - Tag ALL PII
    - Apply retention policies
    - Create training-safe version
    - Link evidence to Layer 1
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pii_detector = PIIDetectionService(db)
    
    async def normalize_transcript(
        self,
        raw_transcript_id: uuid.UUID,
        org_id: uuid.UUID,
        meeting_id: uuid.UUID,
        purpose: str,  # "meeting_minutes", "training_data", etc.
        correlation_id: str
    ) -> uuid.UUID:
        """
        Normalize raw transcript with GDPR compliance
        
        Steps:
        1. Load Layer 1 raw transcript
        2. Segment logically
        3. Detect and tag ALL PII
        4. Map speakers (user-confirmed names)
        5. Set retention policy
        6. Create redacted version
        7. Store with evidence links
        """
        # Load raw transcript
        raw_data = await self._load_raw_transcript(raw_transcript_id)
        
        if not raw_data:
            raise ValueError(f"Raw transcript {raw_transcript_id} not found")
        
        # Segment transcript
        segments = await self._segment_transcript(
            raw_data["speaker_segments"],
            org_id
        )
        
        # Detect PII in all segments
        all_pii: List[Tuple[int, List[PIIEntity]]] = []
        for i, segment in enumerate(segments):
            pii_entities = self.pii_detector.detect_pii(segment.text)
            if pii_entities:
                all_pii.append((i, pii_entities))
                segment.has_pii = True
        
        # Create redacted version (training-safe)
        redacted_text = self._create_redacted_version(
            raw_data["transcript_text"],
            [pii for _, pii_list in all_pii for pii in pii_list]
        )
        
        # Compute source hash
        source_hash = raw_data["sha256_hash"]
        
        # Set retention policy
        retention_date = self._calculate_retention(purpose)
        
        # Store normalized transcript
        normalized_id = uuid.uuid4()
        query = """
        INSERT INTO transcripts_normalized (
            id, raw_transcript_id, org_id, meeting_id,
            segments, purpose, retention_until, gdpr_basis,
            has_pii, pii_redacted_version,
            source_hash, normalization_version
        ) VALUES (
            :id, :raw_transcript_id, :org_id, :meeting_id,
            :segments, :purpose, :retention_until, :gdpr_basis,
            :has_pii, :pii_redacted_version,
            :source_hash, :normalization_version
        )
        """
        
        await self.db.execute(query, {
            "id": normalized_id,
            "raw_transcript_id": raw_transcript_id,
            "org_id": org_id,
            "meeting_id": meeting_id,
            "segments": [s.dict() for s in segments],
            "purpose": purpose,
            "retention_until": retention_date,
            "gdpr_basis": "legitimate_interest",  # or "consent"
            "has_pii": len(all_pii) > 0,
            "pii_redacted_version": redacted_text,
            "source_hash": source_hash,
            "normalization_version": "1.0.0"
        })
        
        # Store PII tags
        for segment_idx, pii_list in all_pii:
            await self.pii_detector.store_pii_tags(
                org_id=org_id,
                normalized_transcript_id=normalized_id,
                segment_sequence=segment_idx,
                pii_entities=pii_list
            )
        
        await self.db.commit()
        
        # Audit log
        await self._audit_log(
            action="layer2_normalize",
            resource_id=normalized_id,
            org_id=org_id,
            correlation_id=correlation_id,
            metadata={
                "raw_transcript_id": str(raw_transcript_id),
                "segments_count": len(segments),
                "pii_count": sum(len(pii_list) for _, pii_list in all_pii),
                "purpose": purpose,
                "retention_until": retention_date.isoformat() if retention_date else None
            }
        )
        
        return normalized_id
    
    async def _load_raw_transcript(
        self,
        raw_transcript_id: uuid.UUID
    ) -> Optional[Dict]:
        """Load Layer 1 raw transcript"""
        query = """
        SELECT id, transcript_text, speaker_segments, sha256_hash
        FROM transcripts_raw
        WHERE id = :id
        """
        result = await self.db.execute(query, {"id": raw_transcript_id})
        row = result.fetchone()
        
        if row:
            return {
                "id": row[0],
                "transcript_text": row[1],
                "speaker_segments": row[2],
                "sha256_hash": row[3]
            }
        return None
    
    async def _segment_transcript(
        self,
        speaker_segments: List[Dict],
        org_id: uuid.UUID
    ) -> List[NormalizedSegment]:
        """
        Segment transcript logically
        
        Maps speaker IDs to confirmed names (if available)
        """
        normalized_segments = []
        
        # Load speaker mappings
        speaker_mappings = await self._load_speaker_mappings(
            org_id,
            [s["speaker_id"] for s in speaker_segments]
        )
        
        for i, raw_segment in enumerate(speaker_segments):
            speaker_id = raw_segment["speaker_id"]
            
            # Get confirmed name if exists
            normalized_name = None
            if speaker_id in speaker_mappings:
                mapping = speaker_mappings[speaker_id]
                if mapping.get("confirmed"):
                    normalized_name = mapping.get("normalized_name")
            
            normalized_segments.append(NormalizedSegment(
                sequence=i,
                speaker_raw_id=speaker_id,
                speaker_normalized=normalized_name,  # NULL if not confirmed
                text=raw_segment["text"],
                start_time=raw_segment.get("start_time"),
                end_time=raw_segment.get("end_time"),
                has_pii=False,  # Will be updated
                pii_entity_ids=[]
            ))
        
        return normalized_segments
    
    async def _load_speaker_mappings(
        self,
        org_id: uuid.UUID,
        speaker_ids: List[str]
    ) -> Dict[str, Dict]:
        """Load confirmed speaker mappings"""
        if not speaker_ids:
            return {}
        
        query = """
        SELECT raw_speaker_id, normalized_name, confirmed
        FROM speaker_mappings
        WHERE org_id = :org_id
        AND raw_speaker_id = ANY(:speaker_ids)
        """
        
        result = await self.db.execute(query, {
            "org_id": org_id,
            "speaker_ids": speaker_ids
        })
        
        mappings = {}
        for row in result:
            mappings[row[0]] = {
                "normalized_name": row[1],
                "confirmed": row[2]
            }
        
        return mappings
    
    def _create_redacted_version(
        self,
        text: str,
        pii_entities: List[PIIEntity]
    ) -> str:
        """Create training-safe version with PII redacted"""
        return self.pii_detector.redact_pii(text, pii_entities)
    
    def _calculate_retention(self, purpose: str) -> Optional[datetime]:
        """
        Calculate retention date based on purpose
        
        GDPR requires purpose limitation
        """
        retention_policies = {
            "meeting_minutes": 365 * 3,  # 3 years
            "training_data": 365 * 7,  # 7 years
            "analytics": 365 * 2,  # 2 years
            "compliance": 365 * 10,  # 10 years
            "temporary": 30  # 30 days
        }
        
        days = retention_policies.get(purpose, 365)
        return datetime.utcnow() + timedelta(days=days)
    
    async def _audit_log(
        self,
        action: str,
        resource_id: uuid.UUID,
        org_id: uuid.UUID,
        correlation_id: str,
        metadata: Dict
    ):
        """Create audit log"""
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
            "resource_type": "transcript_normalized",
            "resource_id": resource_id,
            "success": True,
            "changes": metadata
        })




