# Production Meeting Intelligence System Architecture

## Executive Summary

This document defines the production architecture for a GDPR-compliant, zero-hallucination meeting intelligence system with three processing layers and strict data governance.

## Core Principles

### 1. Zero Fabrication Policy
- **NEVER** invent: speakers, timestamps, attendees, companies, emails, dates, metrics
- **ALWAYS** use `null` for missing data
- **ALWAYS** log missing data as issues
- **ALWAYS** trace outputs to source data

### 2. GDPR Compliance
- Purpose limitation
- Data minimization  
- PII tagging and protection
- Retention policies
- Right to deletion
- Audit trails

### 3. Three-Agent Workflow
Every generated content must pass through:
1. **Generator Agent**: Creates output from grounded data
2. **Matcher Agent**: Validates traceability to source
3. **QA/Approver Agent**: Verifies correctness and compliance

---

## System Architecture

### Layer 1: ASR Ingestion (Verbatim)

**Purpose**: Store raw transcription data without modification

**Responsibilities**:
- Accept audio/video files or transcription JSON
- Store verbatim transcript with timestamps
- Store speaker diarization (speaker IDs, not names)
- Store metadata (file info, upload time, source)
- **Never** modify, correct, or fabricate content

**Data Model**:
```python
class TranscriptRaw:
    id: UUID
    artifact_id: UUID  # Link to uploaded file
    org_id: UUID
    
    # Raw transcript data
    transcript_text: str  # Verbatim, unmodified
    language: str  # Detected language
    confidence: float  # Overall confidence
    
    # Diarization
    speakers: List[SpeakerSegment]  # speaker_id, start, end, text
    speaker_count: int
    
    # Metadata
    source_provider: str  # "klang", "mistral", "openai", "manual"
    source_metadata: JSONB  # Provider-specific data
    processing_timestamp: datetime
    
    # Audit
    created_at: datetime
    sha256_hash: str  # Content hash for verification

class SpeakerSegment:
    speaker_id: str  # "SPEAKER_0", "SPEAKER_1" (not real names)
    start_time: float
    end_time: float
    text: str
    confidence: float
```

**Rules**:
- ✅ Store exactly what ASR provider returns
- ✅ Log if confidence < threshold as issue
- ✅ Hash content for tamper detection
- ❌ Never assign real names at this layer
- ❌ Never correct or modify transcript
- ❌ Never merge or split speakers automatically

---

### Layer 2: Normalization & GDPR Compliance

**Purpose**: Transform raw data into compliant, normalized form

**Responsibilities**:
- Normalize speaker identities (with user confirmation)
- Segment transcript into logical chunks
- Tag PII (names, emails, phone numbers, addresses)
- Apply GDPR rules (purpose, retention, minimization)
- Create "training-safe" version (PII redacted)
- Maintain evidence links to Layer 1

**Data Model**:
```python
class TranscriptNormalized:
    id: UUID
    raw_transcript_id: UUID  # Link to Layer 1
    org_id: UUID
    meeting_id: UUID
    
    # Normalized content
    segments: List[TranscriptSegment]
    
    # GDPR compliance
    pii_tags: List[PIITag]
    purpose: str  # "meeting_minutes", "training_data", etc.
    retention_until: datetime
    gdpr_basis: str  # "legitimate_interest", "consent", etc.
    
    # Evidence
    source_hash: str  # Hash of source Layer 1 data
    normalization_version: str  # Version of rules applied
    
    created_at: datetime

class TranscriptSegment:
    id: UUID
    sequence: int
    speaker_normalized: Optional[str]  # Real name (if confirmed)
    speaker_raw_id: str  # Link back to Layer 1
    text: str
    start_time: float
    end_time: float
    
    # PII status
    has_pii: bool
    pii_tags: List[str]  # IDs of PII instances
    
    # Evidence
    raw_segment_ids: List[UUID]  # Which Layer 1 segments

class PIITag:
    id: UUID
    entity_type: str  # "person_name", "email", "phone", "company"
    text: str  # Actual PII value
    redacted_text: str  # "[NAME]", "[EMAIL]", etc.
    start_char: int
    end_char: int
    segment_id: UUID
    confidence: float
    
    # GDPR
    can_store: bool
    can_train: bool
    deletion_requested: bool

class SpeakerMapping:
    id: UUID
    org_id: UUID
    raw_speaker_id: str  # "SPEAKER_0"
    normalized_name: Optional[str]
    normalized_email: Optional[str]
    
    # Confirmation
    confirmed: bool
    confirmed_by_user_id: Optional[UUID]
    confirmed_at: Optional[datetime]
    
    # Evidence
    confidence_score: float
    basis: str  # "user_input", "email_signature", "inferred"
```

**Process Flow**:
```
1. Load raw transcript from Layer 1
2. Segment into logical chunks
3. Run PII detection
4. Tag all PII entities
5. Present speaker mappings to user for confirmation
6. Store normalized version with evidence links
7. Generate training-safe version (PII redacted)
8. Set retention policy
```

**Rules**:
- ✅ Always link back to Layer 1 source
- ✅ Require user confirmation for speaker names
- ✅ Tag ALL PII (names, emails, phone, addresses)
- ✅ Create training-safe redacted version
- ✅ Set explicit retention policy
- ❌ Never guess speaker identities
- ❌ Never store PII without tagging
- ❌ Never auto-merge speakers without confirmation

---

### Layer 3: Intelligence Extraction

**Purpose**: Extract structured insights from normalized data

**Responsibilities**:
- Extract decisions with evidence
- Extract action items with owners and deadlines
- Extract risks and concerns
- Identify key topics and themes
- Generate structured artifacts
- **Always** ground outputs in source data

**Data Model**:
```python
class Decision:
    id: UUID
    meeting_id: UUID
    org_id: UUID
    
    # Content (from 3-agent workflow)
    decision: str
    rationale: Optional[str]
    impact: Optional[str]
    
    # Evidence (from Matcher Agent)
    evidence: List[EvidencePointer]
    confidence: float
    
    # QA
    qa_goal: str
    qa_passed: bool
    qa_issues: List[str]
    
    # Provenance
    extraction_version: str
    generator_model: str
    created_at: datetime

class ActionItem:
    id: UUID
    meeting_id: UUID
    org_id: UUID
    
    # Content
    title: str
    description: Optional[str]
    owner_name: Optional[str]
    owner_email: Optional[str]
    due_date: Optional[date]
    priority: Optional[str]
    status: str  # "open", "in_progress", "done"
    
    # Evidence
    evidence: List[EvidencePointer]
    confidence: float
    
    # External sync
    external_refs: List[ExternalRef]  # Linear, Jira, etc.
    idempotency_key: str
    
    # QA
    qa_passed: bool
    qa_issues: List[str]

class EvidencePointer:
    source_table: str  # "transcript_segments"
    source_id: UUID
    source_field: str  # "text"
    quote: str  # Exact text from source
    relevance_score: float

class ExtractionRun:
    id: UUID
    meeting_id: UUID
    run_type: str  # "decisions", "action_items", "summary"
    
    # Configuration
    qa_goal: str  # "zero_hallucinations", "maximize_recall", etc.
    model_version: str
    
    # Results
    items_extracted: int
    items_passed_qa: int
    items_rejected: int
    
    # Issues
    issues: List[Issue]
    
    # Audit
    started_at: datetime
    completed_at: datetime
    correlation_id: str

class Issue:
    id: UUID
    type: str  # "missing_data", "low_confidence", "pii_leak", "hallucination"
    severity: str  # "critical", "warning", "info"
    description: str
    evidence: JSONB
    resolved: bool
```

**Three-Agent Workflow**:

```python
class ThreeAgentWorkflow:
    """
    Ensures all generated content is grounded, traceable, and QA'd
    """
    
    def extract_content(
        self,
        meeting_id: UUID,
        content_type: str,  # "decisions", "action_items", "summary"
        qa_goal: str,  # Required QA target
        context: Dict
    ) -> ExtractionResult:
        
        # Agent 1: Generator
        generated = self.generator_agent.generate(
            meeting_id=meeting_id,
            content_type=content_type,
            context=context
        )
        
        # Agent 2: Matcher (Evidence)
        matched = self.matcher_agent.validate_evidence(
            generated_content=generated,
            source_data=context["source_segments"]
        )
        
        # Agent 3: QA/Approver
        approved = self.qa_agent.verify(
            content=matched,
            qa_goal=qa_goal,
            checks=[
                "no_hallucinations",
                "gdpr_compliant",
                "evidence_valid",
                "output_quality"
            ]
        )
        
        return approved
```

**Rules**:
- ✅ Every extracted item MUST have evidence pointers
- ✅ Every extraction MUST specify QA goal
- ✅ Run full 3-agent workflow
- ✅ Log issues for rejected items
- ✅ Store extraction version and config
- ❌ Never extract without evidence
- ❌ Never skip QA step
- ❌ Never fabricate owner names/emails
- ❌ Never invent dates or metrics

---

## GDPR Compliance Implementation

### Data Classification

```python
class DataClassification(Enum):
    PUBLIC = "public"  # Can be shared freely
    INTERNAL = "internal"  # Org-only
    CONFIDENTIAL = "confidential"  # Restricted access
    PII = "pii"  # Personal identifiable information
    SENSITIVE_PII = "sensitive_pii"  # Health, financial, etc.

class DataPurpose(Enum):
    MEETING_MINUTES = "meeting_minutes"
    ACTION_TRACKING = "action_tracking"
    TRAINING_DATA = "training_data"
    ANALYTICS = "analytics"
    COMPLIANCE = "compliance"

class RetentionPolicy:
    purpose: DataPurpose
    retention_days: int
    auto_delete: bool
    notify_before_deletion_days: int
```

### PII Detection and Tagging

```python
class PIIDetector:
    """
    Detect and tag all PII in text
    """
    
    def detect_pii(self, text: str) -> List[PIITag]:
        """
        Detect:
        - Person names (NER)
        - Email addresses (regex)
        - Phone numbers (regex)
        - Addresses (NER)
        - Company names (NER)
        - Dates (when combined with person)
        - Financial data
        """
        pass
    
    def redact_for_training(self, text: str, pii_tags: List[PIITag]) -> str:
        """
        Replace PII with tokens: [NAME], [EMAIL], [PHONE]
        Preserves structure for training
        """
        pass
```

### Deletion Workflow

```python
class DeletionRequest:
    id: UUID
    request_type: str  # "user_data", "meeting", "speaker"
    entity_id: UUID
    requested_by: UUID
    requested_at: datetime
    
    # What to delete
    scope: str  # "all", "pii_only", "specific_fields"
    reason: str
    
    # Status
    status: str  # "pending", "approved", "executed", "rejected"
    executed_at: Optional[datetime]
    
    # Cascade tracking
    affected_tables: List[str]
    affected_records: int

def handle_deletion_request(request: DeletionRequest):
    """
    1. Validate request
    2. Identify all affected records (cascade)
    3. Create audit log
    4. Execute deletion
    5. Verify deletion
    6. Notify requester
    """
    pass
```

---

## Security & Access Control

### Row-Level Security (RLS)

```sql
-- Every table has org_id
-- Users can only access their org's data
CREATE POLICY "org_isolation"
  ON meetings FOR ALL
  USING (
    org_id IN (
      SELECT org_id FROM org_memberships
      WHERE user_id = auth.uid()
    )
  );

-- Role-based within org
CREATE POLICY "role_based_access"
  ON meetings FOR UPDATE
  USING (
    org_id IN (
      SELECT org_id FROM org_memberships
      WHERE user_id = auth.uid()
      AND role IN ('owner', 'admin', 'editor')
    )
  );
```

### Encryption

```python
class EncryptionService:
    """
    - At-rest: PostgreSQL transparent encryption
    - In-transit: TLS/HTTPS
    - Sensitive fields: Envelope encryption
    """
    
    def encrypt_sensitive_field(self, value: str, context: Dict) -> str:
        """
        Use envelope encryption for PII:
        1. Generate data encryption key (DEK)
        2. Encrypt data with DEK
        3. Encrypt DEK with master key (from KMS)
        4. Store encrypted data + encrypted DEK
        """
        pass
```

---

## Observability & Audit

### Structured Logging

```python
class StructuredLogger:
    def log(
        self,
        level: str,
        message: str,
        correlation_id: str,
        context: Dict,
        evidence: Optional[Dict] = None
    ):
        log_entry = {
            "timestamp": datetime.utcnow(),
            "level": level,
            "message": message,
            "correlation_id": correlation_id,
            "user_id": context.get("user_id"),
            "org_id": context.get("org_id"),
            "meeting_id": context.get("meeting_id"),
            "action": context.get("action"),
            "evidence": evidence,
            "service": context.get("service"),
            "version": context.get("version")
        }
        # Send to logging system
```

### Audit Trail

```python
class AuditLog:
    id: UUID
    timestamp: datetime
    correlation_id: str
    
    # Who
    user_id: Optional[UUID]
    org_id: UUID
    
    # What
    action: str
    resource_type: str
    resource_id: UUID
    
    # How
    method: str
    endpoint: Optional[str]
    
    # Changes
    changes: JSONB  # Before/after
    
    # Evidence
    evidence_snapshot: JSONB
    
    # Result
    success: bool
    error: Optional[str]
```

---

## Integration Adapters

### Interface Pattern

```python
class CalendarAdapter(ABC):
    @abstractmethod
    async def create_event(
        self,
        title: str,
        start: datetime,
        end: datetime,
        attendees: List[str],
        description: Optional[str],
        idempotency_key: str
    ) -> ExternalRef:
        """Idempotent event creation"""
        pass
    
    @abstractmethod
    async def update_event(
        self,
        external_id: str,
        updates: Dict,
        idempotency_key: str
    ) -> ExternalRef:
        pass

class GoogleCalendarAdapter(CalendarAdapter):
    """Google Calendar implementation"""
    pass

class TodoAdapter(ABC):
    @abstractmethod
    async def create_task(
        self,
        title: str,
        description: Optional[str],
        assignee: Optional[str],
        due_date: Optional[date],
        idempotency_key: str
    ) -> ExternalRef:
        pass

class LinearAdapter(TodoAdapter):
    """Linear implementation"""
    pass
```

---

## Database Schema Updates

### Core Tables

```sql
-- Layer 1: Raw transcripts
CREATE TABLE transcripts_raw (
    id UUID PRIMARY KEY,
    artifact_id UUID REFERENCES artifacts(id),
    org_id UUID REFERENCES orgs(id),
    transcript_text TEXT NOT NULL,
    language VARCHAR(10),
    confidence FLOAT,
    speaker_segments JSONB NOT NULL,
    source_provider VARCHAR(50),
    source_metadata JSONB,
    sha256_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Layer 2: Normalized transcripts
CREATE TABLE transcripts_normalized (
    id UUID PRIMARY KEY,
    raw_transcript_id UUID REFERENCES transcripts_raw(id),
    org_id UUID REFERENCES orgs(id),
    meeting_id UUID REFERENCES meetings(id),
    segments JSONB NOT NULL,
    pii_tags JSONB,
    purpose VARCHAR(50) NOT NULL,
    retention_until TIMESTAMPTZ,
    gdpr_basis VARCHAR(50),
    source_hash VARCHAR(64) NOT NULL,
    normalization_version VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- PII tags
CREATE TABLE pii_tags (
    id UUID PRIMARY KEY,
    org_id UUID REFERENCES orgs(id),
    segment_id UUID,
    entity_type VARCHAR(50) NOT NULL,
    text TEXT NOT NULL,
    redacted_text VARCHAR(50),
    start_char INTEGER,
    end_char INTEGER,
    confidence FLOAT,
    can_store BOOLEAN DEFAULT true,
    can_train BOOLEAN DEFAULT false,
    deletion_requested BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Evidence pointers
CREATE TABLE evidence_pointers (
    id UUID PRIMARY KEY,
    artifact_id UUID NOT NULL,  -- Decision, ActionItem, etc.
    artifact_type VARCHAR(50) NOT NULL,
    source_table VARCHAR(100) NOT NULL,
    source_id UUID NOT NULL,
    source_field VARCHAR(100),
    quote TEXT,
    relevance_score FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Extraction runs
CREATE TABLE extraction_runs (
    id UUID PRIMARY KEY,
    meeting_id UUID REFERENCES meetings(id),
    org_id UUID REFERENCES orgs(id),
    run_type VARCHAR(50) NOT NULL,
    qa_goal VARCHAR(200) NOT NULL,
    model_version VARCHAR(50),
    items_extracted INTEGER DEFAULT 0,
    items_passed_qa INTEGER DEFAULT 0,
    items_rejected INTEGER DEFAULT 0,
    issues JSONB,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    correlation_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Issues log
CREATE TABLE issues (
    id UUID PRIMARY KEY,
    extraction_run_id UUID REFERENCES extraction_runs(id),
    org_id UUID REFERENCES orgs(id),
    issue_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT,
    evidence JSONB,
    resolved BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit log
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    correlation_id VARCHAR(100),
    user_id UUID,
    org_id UUID REFERENCES orgs(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    method VARCHAR(10),
    endpoint VARCHAR(200),
    changes JSONB,
    evidence_snapshot JSONB,
    success BOOLEAN,
    error TEXT
);

-- Deletion requests
CREATE TABLE deletion_requests (
    id UUID PRIMARY KEY,
    request_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    requested_by UUID NOT NULL,
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    scope VARCHAR(50),
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    executed_at TIMESTAMPTZ,
    affected_tables TEXT[],
    affected_records INTEGER
);
```

---

## Implementation Priority

### Phase 1: Foundation (Week 1-2)
1. ✅ Update database schema (migrations)
2. ✅ Implement Layer 1 (raw ingestion)
3. ✅ Add audit logging
4. ✅ Add correlation IDs

### Phase 2: GDPR (Week 3-4)
5. ✅ Implement PII detection
6. ✅ Add data classification
7. ✅ Implement retention policies
8. ✅ Add deletion workflow

### Phase 3: Intelligence (Week 5-6)
9. ✅ Implement 3-agent workflow
10. ✅ Add evidence pointers
11. ✅ Implement QA goals
12. ✅ Add extraction runs

### Phase 4: Integrations (Week 7-8)
13. ✅ Calendar adapter interface
14. ✅ Todo adapter interface  
15. ✅ Email adapter interface
16. ✅ Idempotency for external actions

---

## Quality Assurance Goals

Available QA goals for extraction runs:

- `zero_hallucinations`: Maximum evidence validation, reject ungrounded claims
- `maximize_recall`: Extract all possible items, allow lower confidence
- `board_ready_summary`: High quality prose, verified facts only
- `training_safe_dataset`: All PII redacted, safe for model training
- `gdpr_minimization`: Minimum personal data, maximum privacy
- `action_item_completeness`: Ensure owner, deadline, description present

---

## Success Metrics

### Data Quality
- Zero fabricated data (automated checks)
- 100% evidence traceability for extracted items
- PII detection recall > 99%
- User confirmation rate for speaker mapping

### GDPR Compliance
- 100% PII tagged
- 100% data has retention policy
- Deletion requests processed < 30 days
- Training-safe versions auto-generated

### System Performance
- Layer 1 ingestion: < 1s per minute of audio
- Layer 2 normalization: < 5s per transcript
- Layer 3 extraction: < 30s per meeting
- End-to-end: < 2 minutes for 30-min meeting

---

## Next Steps

**Immediate actions**:
1. Review and approve this architecture
2. Generate database migrations
3. Implement Layer 1 service
4. Add structured logging
5. Implement PII detector

**Questions for stakeholder**:
1. Preferred QA goal for production runs?
2. Retention policy defaults per data type?
3. External integrations priority (Linear, Google, etc.)?
4. Auto-deletion policy preferences?





