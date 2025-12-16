-- Migration 002: Production Architecture - Three Layers + GDPR + Evidence
-- Adds Layer 1 (raw transcripts), Layer 2 (normalized + GDPR), Layer 3 (intelligence with evidence)

-- ============================================================================
-- LAYER 1: RAW TRANSCRIPTION DATA (Verbatim, Unmodified)
-- ============================================================================

CREATE TABLE IF NOT EXISTS transcripts_raw (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artifact_id UUID REFERENCES artifacts(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    
    -- Raw transcript content (never modified)
    transcript_text TEXT NOT NULL,
    language VARCHAR(10),
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
    
    -- Speaker diarization (speaker IDs, NOT real names)
    speaker_segments JSONB NOT NULL, -- Array of {speaker_id, start_time, end_time, text, confidence}
    speaker_count INTEGER,
    
    -- Source provenance
    source_provider VARCHAR(50) NOT NULL, -- "klang", "mistral", "openai", "manual"
    source_metadata JSONB, -- Provider-specific data
    
    -- Integrity
    sha256_hash VARCHAR(64) NOT NULL UNIQUE,
    processing_timestamp TIMESTAMPTZ DEFAULT NOW(),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_transcripts_raw_artifact ON transcripts_raw(artifact_id);
CREATE INDEX idx_transcripts_raw_org ON transcripts_raw(org_id);
CREATE INDEX idx_transcripts_raw_hash ON transcripts_raw(sha256_hash);

-- Enable RLS
ALTER TABLE transcripts_raw ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view raw transcripts in their orgs"
    ON transcripts_raw FOR SELECT
    USING (org_id IN (
        SELECT org_id FROM org_memberships WHERE user_id = auth.uid()
    ));


-- ============================================================================
-- LAYER 2: NORMALIZED TRANSCRIPTS + GDPR COMPLIANCE
-- ============================================================================

CREATE TABLE IF NOT EXISTS transcripts_normalized (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_transcript_id UUID NOT NULL REFERENCES transcripts_raw(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    meeting_id UUID REFERENCES meetings(id) ON DELETE CASCADE,
    
    -- Normalized segments (with confirmed speaker names)
    segments JSONB NOT NULL, -- Array of segment objects
    
    -- GDPR compliance
    purpose VARCHAR(50) NOT NULL, -- "meeting_minutes", "training_data", "analytics"
    retention_until TIMESTAMPTZ, -- Auto-delete after this date
    gdpr_basis VARCHAR(50), -- "legitimate_interest", "consent", "contract"
    
    -- PII summary
    has_pii BOOLEAN DEFAULT false,
    pii_redacted_version TEXT, -- Training-safe version with PII replaced
    
    -- Evidence and versioning
    source_hash VARCHAR(64) NOT NULL, -- Hash of source Layer 1 data
    normalization_version VARCHAR(20) NOT NULL,
    normalization_config JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_transcripts_normalized_raw ON transcripts_normalized(raw_transcript_id);
CREATE INDEX idx_transcripts_normalized_meeting ON transcripts_normalized(meeting_id);
CREATE INDEX idx_transcripts_normalized_org ON transcripts_normalized(org_id);
CREATE INDEX idx_transcripts_normalized_retention ON transcripts_normalized(retention_until) WHERE retention_until IS NOT NULL;

-- Enable RLS
ALTER TABLE transcripts_normalized ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view normalized transcripts in their orgs"
    ON transcripts_normalized FOR SELECT
    USING (org_id IN (
        SELECT org_id FROM org_memberships WHERE user_id = auth.uid()
    ));


-- ============================================================================
-- PII TAGS (GDPR Compliance)
-- ============================================================================

CREATE TABLE IF NOT EXISTS pii_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    normalized_transcript_id UUID REFERENCES transcripts_normalized(id) ON DELETE CASCADE,
    segment_sequence INTEGER, -- Which segment in the normalized transcript
    
    -- PII details
    entity_type VARCHAR(50) NOT NULL, -- "person_name", "email", "phone", "address", "company", "financial"
    text TEXT NOT NULL, -- Actual PII value (encrypted at rest)
    redacted_text VARCHAR(50) NOT NULL, -- "[NAME]", "[EMAIL]", "[PHONE]", etc.
    
    -- Position in text
    start_char INTEGER NOT NULL,
    end_char INTEGER NOT NULL,
    
    -- Detection confidence
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
    detection_method VARCHAR(50), -- "ner", "regex", "manual"
    
    -- GDPR flags
    can_store BOOLEAN DEFAULT true,
    can_train BOOLEAN DEFAULT false, -- Can use in training data
    deletion_requested BOOLEAN DEFAULT false,
    deletion_requested_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_pii_tags_transcript ON pii_tags(normalized_transcript_id);
CREATE INDEX idx_pii_tags_org ON pii_tags(org_id);
CREATE INDEX idx_pii_tags_entity_type ON pii_tags(entity_type);
CREATE INDEX idx_pii_tags_deletion ON pii_tags(deletion_requested) WHERE deletion_requested = true;

-- Enable RLS
ALTER TABLE pii_tags ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view PII tags in their orgs"
    ON pii_tags FOR SELECT
    USING (org_id IN (
        SELECT org_id FROM org_memberships WHERE user_id = auth.uid()
    ));


-- ============================================================================
-- SPEAKER MAPPINGS (User-confirmed identities)
-- ============================================================================

CREATE TABLE IF NOT EXISTS speaker_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    raw_speaker_id VARCHAR(50) NOT NULL, -- "SPEAKER_0", "SPEAKER_1"
    
    -- Normalized identity (user-confirmed)
    normalized_name VARCHAR(255),
    normalized_email VARCHAR(255),
    normalized_role VARCHAR(255),
    
    -- Confirmation status
    confirmed BOOLEAN DEFAULT false,
    confirmed_by_user_id UUID, -- Who confirmed this mapping
    confirmed_at TIMESTAMPTZ,
    
    -- Evidence
    confidence_score FLOAT,
    basis VARCHAR(100), -- "user_input", "email_signature", "calendar_invite", "inferred"
    supporting_evidence JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(org_id, raw_speaker_id)
);

CREATE INDEX idx_speaker_mappings_org ON speaker_mappings(org_id);
CREATE INDEX idx_speaker_mappings_confirmed ON speaker_mappings(confirmed);

-- Enable RLS
ALTER TABLE speaker_mappings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage speaker mappings in their orgs"
    ON speaker_mappings FOR ALL
    USING (org_id IN (
        SELECT org_id FROM org_memberships WHERE user_id = auth.uid()
    ));


-- ============================================================================
-- LAYER 3: EVIDENCE POINTERS (Traceability)
-- ============================================================================

CREATE TABLE IF NOT EXISTS evidence_pointers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- What artifact does this evidence support?
    artifact_type VARCHAR(50) NOT NULL, -- "decision", "action_item", "summary", "risk"
    artifact_id UUID NOT NULL,
    
    -- What is the source?
    source_table VARCHAR(100) NOT NULL, -- "transcripts_normalized", "transcript_segments"
    source_id UUID NOT NULL,
    source_field VARCHAR(100), -- Which field contains the evidence
    
    -- Evidence content
    quote TEXT, -- Exact text from source
    relevance_score FLOAT CHECK (relevance_score >= 0 AND relevance_score <= 1),
    
    -- Context
    context JSONB, -- Additional context (speaker, timestamp, etc.)
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_evidence_artifact ON evidence_pointers(artifact_type, artifact_id);
CREATE INDEX idx_evidence_source ON evidence_pointers(source_table, source_id);


-- ============================================================================
-- EXTRACTION RUNS (3-Agent Workflow Tracking)
-- ============================================================================

CREATE TABLE IF NOT EXISTS extraction_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    
    -- What was extracted
    run_type VARCHAR(50) NOT NULL, -- "decisions", "action_items", "summary", "risks", "topics"
    
    -- QA Goal (REQUIRED)
    qa_goal VARCHAR(200) NOT NULL, -- "zero_hallucinations", "maximize_recall", "board_ready", etc.
    
    -- Model version
    generator_model VARCHAR(100),
    matcher_model VARCHAR(100),
    qa_model VARCHAR(100),
    workflow_version VARCHAR(20),
    
    -- Results
    items_extracted INTEGER DEFAULT 0,
    items_passed_qa INTEGER DEFAULT 0,
    items_rejected INTEGER DEFAULT 0,
    
    -- Issues encountered
    issues JSONB, -- Array of issue objects
    
    -- Performance
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_seconds FLOAT,
    
    -- Traceability
    correlation_id VARCHAR(100) UNIQUE,
    config JSONB, -- Full configuration used
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_extraction_runs_meeting ON extraction_runs(meeting_id);
CREATE INDEX idx_extraction_runs_org ON extraction_runs(org_id);
CREATE INDEX idx_extraction_runs_type ON extraction_runs(run_type);
CREATE INDEX idx_extraction_runs_correlation ON extraction_runs(correlation_id);

-- Enable RLS
ALTER TABLE extraction_runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view extraction runs in their orgs"
    ON extraction_runs FOR SELECT
    USING (org_id IN (
        SELECT org_id FROM org_memberships WHERE user_id = auth.uid()
    ));


-- ============================================================================
-- ISSUES LOG (Missing Data, Low Confidence, Hallucinations)
-- ============================================================================

CREATE TABLE IF NOT EXISTS issues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    extraction_run_id UUID REFERENCES extraction_runs(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    
    -- Issue details
    issue_type VARCHAR(50) NOT NULL, -- "missing_data", "low_confidence", "pii_leak", "hallucination", "qa_failed"
    severity VARCHAR(20) NOT NULL, -- "critical", "warning", "info"
    description TEXT NOT NULL,
    
    -- Evidence
    evidence JSONB, -- What triggered this issue
    affected_item_id UUID,
    affected_item_type VARCHAR(50),
    
    -- Resolution
    resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMPTZ,
    resolution_note TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_issues_run ON issues(extraction_run_id);
CREATE INDEX idx_issues_org ON issues(org_id);
CREATE INDEX idx_issues_type ON issues(issue_type);
CREATE INDEX idx_issues_severity ON issues(severity);
CREATE INDEX idx_issues_resolved ON issues(resolved) WHERE resolved = false;

-- Enable RLS
ALTER TABLE issues ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view issues in their orgs"
    ON issues FOR SELECT
    USING (org_id IN (
        SELECT org_id FROM org_memberships WHERE user_id = auth.uid()
    ));


-- ============================================================================
-- AUDIT LOGS (Full System Auditability)
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    correlation_id VARCHAR(100),
    
    -- Who
    user_id UUID,
    org_id UUID REFERENCES orgs(id) ON DELETE CASCADE,
    ip_address INET,
    user_agent TEXT,
    
    -- What
    action VARCHAR(100) NOT NULL, -- "create", "update", "delete", "export", "view"
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    
    -- How
    method VARCHAR(10), -- "GET", "POST", etc.
    endpoint VARCHAR(200),
    
    -- Changes (for update/delete)
    changes JSONB, -- {before: {...}, after: {...}}
    
    -- Evidence snapshot (what data was available at action time)
    evidence_snapshot JSONB,
    
    -- Result
    success BOOLEAN NOT NULL,
    error TEXT,
    duration_ms INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_org ON audit_logs(org_id);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_correlation ON audit_logs(correlation_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

-- Enable RLS
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view audit logs for their orgs"
    ON audit_logs FOR SELECT
    USING (
        org_id IN (
            SELECT org_id FROM org_memberships 
            WHERE user_id = auth.uid() 
            AND role IN ('owner', 'admin')
        )
    );


-- ============================================================================
-- DELETION REQUESTS (GDPR Right to Erasure)
-- ============================================================================

CREATE TABLE IF NOT EXISTS deletion_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- What to delete
    request_type VARCHAR(50) NOT NULL, -- "user_data", "meeting", "speaker", "pii"
    entity_id UUID NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    
    -- Who requested
    requested_by UUID NOT NULL,
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Scope
    scope VARCHAR(50) NOT NULL, -- "all", "pii_only", "specific_fields"
    reason TEXT,
    fields_to_delete TEXT[], -- If scope = "specific_fields"
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- "pending", "approved", "executing", "completed", "rejected"
    approved_by UUID,
    approved_at TIMESTAMPTZ,
    executed_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Impact tracking
    affected_tables TEXT[],
    affected_records INTEGER,
    cascade_depth INTEGER, -- How many levels of cascade
    
    -- Error handling
    error TEXT,
    retry_count INTEGER DEFAULT 0,
    
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE
);

CREATE INDEX idx_deletion_requests_status ON deletion_requests(status);
CREATE INDEX idx_deletion_requests_org ON deletion_requests(org_id);
CREATE INDEX idx_deletion_requests_entity ON deletion_requests(entity_id, entity_type);
CREATE INDEX idx_deletion_requests_requested_by ON deletion_requests(requested_by);

-- Enable RLS
ALTER TABLE deletion_requests ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage deletion requests in their orgs"
    ON deletion_requests FOR ALL
    USING (org_id IN (
        SELECT org_id FROM org_memberships WHERE user_id = auth.uid()
    ));


-- ============================================================================
-- UPDATE EXISTING TABLES
-- ============================================================================

-- Add evidence tracking to existing tables
ALTER TABLE action_items ADD COLUMN IF NOT EXISTS extraction_run_id UUID REFERENCES extraction_runs(id);
ALTER TABLE action_items ADD COLUMN IF NOT EXISTS qa_passed BOOLEAN DEFAULT true;
ALTER TABLE action_items ADD COLUMN IF NOT EXISTS qa_issues JSONB;
ALTER TABLE action_items ADD COLUMN IF NOT EXISTS generator_version VARCHAR(50);

ALTER TABLE decisions ADD COLUMN IF NOT EXISTS extraction_run_id UUID REFERENCES extraction_runs(id);
ALTER TABLE decisions ADD COLUMN IF NOT EXISTS qa_passed BOOLEAN DEFAULT true;
ALTER TABLE decisions ADD COLUMN IF NOT EXISTS qa_issues JSONB;
ALTER TABLE decisions ADD COLUMN IF NOT EXISTS generator_version VARCHAR(50);

ALTER TABLE summaries ADD COLUMN IF NOT EXISTS extraction_run_id UUID REFERENCES extraction_runs(id);
ALTER TABLE summaries ADD COLUMN IF NOT EXISTS qa_passed BOOLEAN DEFAULT true;
ALTER TABLE summaries ADD COLUMN IF NOT EXISTS qa_issues JSONB;

-- Add GDPR fields to meetings
ALTER TABLE meetings ADD COLUMN IF NOT EXISTS retention_until TIMESTAMPTZ;
ALTER TABLE meetings ADD COLUMN IF NOT EXISTS gdpr_purpose VARCHAR(50);
ALTER TABLE meetings ADD COLUMN IF NOT EXISTS data_classification VARCHAR(50) DEFAULT 'internal';

-- Add updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_transcripts_raw_updated_at BEFORE UPDATE ON transcripts_raw FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_transcripts_normalized_updated_at BEFORE UPDATE ON transcripts_normalized FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_speaker_mappings_updated_at BEFORE UPDATE ON speaker_mappings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ============================================================================
-- RETENTION POLICY AUTOMATION
-- ============================================================================

CREATE OR REPLACE FUNCTION auto_delete_expired_data()
RETURNS void AS $$
BEGIN
    -- Delete expired normalized transcripts
    DELETE FROM transcripts_normalized 
    WHERE retention_until IS NOT NULL 
    AND retention_until < NOW();
    
    -- Delete expired meetings
    DELETE FROM meetings 
    WHERE retention_until IS NOT NULL 
    AND retention_until < NOW();
    
    -- Log deletions
    INSERT INTO audit_logs (action, resource_type, success, changes)
    VALUES ('auto_delete', 'retention_policy', true, jsonb_build_object('deleted_at', NOW()));
END;
$$ LANGUAGE plpgsql;

-- Run daily (setup with pg_cron or external scheduler)
-- SELECT cron.schedule('auto-delete-expired-data', '0 2 * * *', 'SELECT auto_delete_expired_data()');


-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE transcripts_raw IS 'Layer 1: Verbatim transcripts from ASR, never modified';
COMMENT ON TABLE transcripts_normalized IS 'Layer 2: Normalized transcripts with GDPR compliance';
COMMENT ON TABLE pii_tags IS 'GDPR: All detected PII with redaction info';
COMMENT ON TABLE speaker_mappings IS 'User-confirmed speaker identities';
COMMENT ON TABLE evidence_pointers IS 'Layer 3: Traceability from extracted items to source data';
COMMENT ON TABLE extraction_runs IS '3-Agent workflow tracking with QA goals';
COMMENT ON TABLE issues IS 'Missing data, low confidence, hallucinations log';
COMMENT ON TABLE audit_logs IS 'Complete system audit trail';
COMMENT ON TABLE deletion_requests IS 'GDPR right to erasure tracking';

