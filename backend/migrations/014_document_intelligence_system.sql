-- Migration 014: Document Intelligence System (6-Agent Processing Pipeline)
-- Purpose: Enable document processing, web scraping, and multi-agent analysis
-- with zero-hallucination guarantees and full audit trail

-- =====================================================
-- UPLOADED DOCUMENTS (Immutable Source of Truth)
-- =====================================================

CREATE TABLE IF NOT EXISTS uploaded_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    display_name TEXT,  -- Cleaned, human-readable name (auto-generated from filename)
    file_hash TEXT UNIQUE NOT NULL,  -- SHA-256 for deduplication
    file_size BIGINT NOT NULL,  -- Bytes
    mime_type TEXT NOT NULL,
    raw_content BYTEA,  -- Original file (optional - can use Supabase Storage)
    storage_url TEXT,  -- Supabase Storage URL if stored externally
    
    -- Document classification
    document_type TEXT NOT NULL CHECK (document_type IN (
        'pitch_deck', 'financial_report', 'legal_document', 
        'meeting_notes', 'market_research', 'portfolio_update',
        'competitor_analysis', 'news_article', 'other'
    )),
    
    -- Upload metadata
    uploaded_by UUID,  -- References auth.users(id) but no FK constraint (Supabase auth)
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source TEXT NOT NULL DEFAULT 'upload' CHECK (source IN (
        'upload', 'email', 'scrape', 'api', 'integration'
    )),
    source_metadata JSONB DEFAULT '{}',  -- Email address, URL, etc.
    
    -- Processing status
    processing_status TEXT NOT NULL DEFAULT 'pending' CHECK (processing_status IN (
        'pending', 'processing', 'completed', 'failed', 'requires_review'
    )),
    processing_error TEXT,
    
    -- Access control
    visibility TEXT NOT NULL DEFAULT 'internal' CHECK (visibility IN (
        'internal', 'external_founder', 'external_lp', 'public'
    )),
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_uploaded_documents_org_id ON uploaded_documents(org_id);
CREATE INDEX IF NOT EXISTS idx_uploaded_documents_uploaded_by ON uploaded_documents(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_uploaded_documents_document_type ON uploaded_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_uploaded_documents_status ON uploaded_documents(processing_status);
CREATE INDEX IF NOT EXISTS idx_uploaded_documents_uploaded_at ON uploaded_documents(uploaded_at DESC);
CREATE INDEX IF NOT EXISTS idx_uploaded_documents_file_hash ON uploaded_documents(file_hash);

-- =====================================================
-- EXTRACTED DATA (Agent 1: Extractor)
-- =====================================================

CREATE TABLE IF NOT EXISTS extracted_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES uploaded_documents(id) ON DELETE CASCADE,
    extraction_version INT NOT NULL DEFAULT 1,  -- Increment on re-parse
    
    -- Extracted content
    extracted_text TEXT NOT NULL,
    structured_data JSONB NOT NULL DEFAULT '{}',  -- Tables, entities, etc.
    entities JSONB NOT NULL DEFAULT '[]',  -- [{type, value, source, confidence}]
    
    -- Extraction quality
    confidence_score FLOAT NOT NULL CHECK (confidence_score BETWEEN 0 AND 1),
    ambiguities JSONB DEFAULT '[]',  -- Flagged unclear sections
    corrupted_sections JSONB DEFAULT '[]',
    ocr_used BOOLEAN DEFAULT FALSE,
    ocr_confidence FLOAT,
    
    -- Metadata
    extractor_model TEXT NOT NULL,  -- e.g., "gpt-4o-2024-08-06"
    extractor_version TEXT NOT NULL,  -- Code version
    extracted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(document_id, extraction_version)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_extracted_data_document_id ON extracted_data(document_id);
CREATE INDEX IF NOT EXISTS idx_extracted_data_confidence ON extracted_data(confidence_score);

-- =====================================================
-- ANALYSES (Agent 2: Analyzer)
-- =====================================================

CREATE TABLE IF NOT EXISTS document_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES uploaded_documents(id) ON DELETE CASCADE,
    extraction_id UUID NOT NULL REFERENCES extracted_data(id) ON DELETE CASCADE,
    analysis_version INT NOT NULL DEFAULT 1,
    
    -- Analysis results
    classification TEXT NOT NULL,  -- Detailed document classification
    key_metrics JSONB NOT NULL DEFAULT '{}',  -- {metric: {value, source, confidence}}
    insights JSONB NOT NULL DEFAULT '[]',  -- [{claim, evidence, confidence}]
    risks_identified JSONB DEFAULT '[]',
    opportunities_identified JSONB DEFAULT '[]',
    
    -- Quality metrics
    confidence_breakdown JSONB NOT NULL,  -- Per-section confidence
    overall_confidence FLOAT NOT NULL CHECK (overall_confidence BETWEEN 0 AND 1),
    data_completeness FLOAT,  -- % of expected fields found
    internal_consistency BOOLEAN,  -- Any contradictions found?
    gaps JSONB DEFAULT '[]',  -- What's missing
    
    -- Review flags
    requires_human_review BOOLEAN NOT NULL DEFAULT FALSE,
    review_reason TEXT,
    reviewed_by UUID,  -- References auth.users(id) but no FK constraint
    reviewed_at TIMESTAMPTZ,
    
    -- Metadata
    analyzer_model TEXT NOT NULL,
    analyzer_version TEXT NOT NULL,
    analyzed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(document_id, analysis_version)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_analyses_document_id ON document_analyses(document_id);
CREATE INDEX IF NOT EXISTS idx_analyses_requires_review ON document_analyses(requires_human_review) WHERE requires_human_review = TRUE;
CREATE INDEX IF NOT EXISTS idx_analyses_confidence ON document_analyses(overall_confidence);

-- =====================================================
-- RESEARCH RESULTS (Agent 3: Researcher)
-- =====================================================

CREATE TABLE IF NOT EXISTS research_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES document_analyses(id) ON DELETE CASCADE,
    
    -- Claim being verified
    claim TEXT NOT NULL,
    claim_source TEXT NOT NULL,  -- Where in document
    
    -- Verification
    verification_status TEXT NOT NULL CHECK (verification_status IN (
        'confirmed', 'contradicted', 'not_found', 'uncertain'
    )),
    
    -- Public sources
    public_sources JSONB NOT NULL DEFAULT '[]',  -- [{url, title, date, excerpt, reliability}]
    source_count INT NOT NULL DEFAULT 0,
    
    -- Findings
    discrepancies JSONB DEFAULT '[]',
    additional_context JSONB DEFAULT '{}',
    
    -- Confidence adjustment
    confidence_adjustment FLOAT NOT NULL DEFAULT 0.0,  -- -1.0 to +1.0
    
    -- Metadata
    researched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    researcher_version TEXT NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_research_analysis_id ON research_results(analysis_id);
CREATE INDEX IF NOT EXISTS idx_research_verification ON research_results(verification_status);

-- =====================================================
-- GENERATED QUESTIONS (Agent 4: Question Generator)
-- =====================================================

CREATE TABLE IF NOT EXISTS generated_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES document_analyses(id) ON DELETE CASCADE,
    
    -- Question details
    question TEXT NOT NULL,
    category TEXT NOT NULL,  -- financial, technical, team, market, legal, etc.
    priority TEXT NOT NULL CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    
    -- Context
    triggered_by TEXT NOT NULL,  -- What data point triggered this question
    risk_category TEXT,  -- What risk this addresses
    suggested_sources JSONB DEFAULT '[]',  -- Where to find answer
    
    -- Status
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN (
        'open', 'in_progress', 'answered', 'dismissed'
    )),
    answer TEXT,
    answered_by UUID,  -- References auth.users(id) but no FK constraint
    answered_at TIMESTAMPTZ,
    
    -- Metadata
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_questions_analysis_id ON generated_questions(analysis_id);
CREATE INDEX IF NOT EXISTS idx_questions_priority ON generated_questions(priority);
CREATE INDEX IF NOT EXISTS idx_questions_status ON generated_questions(status);

-- =====================================================
-- GENERATED CONTENT (Agent 5: Content Generator)
-- =====================================================

CREATE TABLE IF NOT EXISTS generated_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES document_analyses(id) ON DELETE CASCADE,
    
    -- Content type
    content_type TEXT NOT NULL CHECK (content_type IN (
        'due_diligence', 'swot_analysis', 'competitive_analysis',
        'investment_memo', 'executive_summary', 'risk_assessment',
        'market_analysis', 'financial_summary', 'custom'
    )),
    
    -- Content
    content TEXT NOT NULL,  -- Markdown with inline citations
    content_html TEXT,  -- Rendered HTML
    sources_cited JSONB NOT NULL DEFAULT '[]',  -- All citations
    
    -- Quality
    confidence_level TEXT NOT NULL CHECK (confidence_level IN ('high', 'medium', 'low')),
    citation_coverage FLOAT,  -- % of claims cited
    disclaimer TEXT NOT NULL,
    
    -- Approval
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    verified_by UUID,  -- References auth.users(id) but no FK constraint
    verified_at TIMESTAMPTZ,
    qa_issues JSONB DEFAULT '[]',
    
    -- Access control
    visibility TEXT NOT NULL DEFAULT 'internal' CHECK (visibility IN (
        'internal', 'external_redacted', 'external_full'
    )),
    
    -- Metadata
    generator_model TEXT NOT NULL,
    generator_version TEXT NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Versioning
    version INT NOT NULL DEFAULT 1,
    superseded_by UUID REFERENCES generated_content(id),
    
    UNIQUE(analysis_id, content_type, version)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_generated_content_analysis_id ON generated_content(analysis_id);
CREATE INDEX IF NOT EXISTS idx_generated_content_type ON generated_content(content_type);
CREATE INDEX IF NOT EXISTS idx_generated_content_verified ON generated_content(verified);

-- =====================================================
-- PROCESSING AUDIT LOG (Complete Traceability)
-- =====================================================

CREATE TABLE IF NOT EXISTS document_processing_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES uploaded_documents(id) ON DELETE CASCADE,
    
    -- Agent & action
    agent TEXT NOT NULL CHECK (agent IN (
        'extractor', 'analyzer', 'researcher', 'question_generator',
        'content_generator', 'verifier', 'system'
    )),
    action TEXT NOT NULL,  -- 'extract', 'analyze', 'verify', 'approve', 'reject'
    
    -- Data
    input_data JSONB,
    output_data JSONB,
    
    -- Quality metrics
    confidence_score FLOAT,
    issues_flagged JSONB DEFAULT '[]',
    
    -- Performance
    processing_time_ms INT,
    tokens_used INT,
    model_used TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id UUID  -- References auth.users(id) but no FK constraint
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_audit_document_id ON document_processing_audit_log(document_id);
CREATE INDEX IF NOT EXISTS idx_audit_agent ON document_processing_audit_log(agent);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON document_processing_audit_log(created_at DESC);

-- =====================================================
-- WEB SCRAPING CONFIGS
-- =====================================================

CREATE TABLE IF NOT EXISTS scraping_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Target
    name TEXT NOT NULL UNIQUE,  -- e.g., "competitor_pricing_acme"
    url TEXT NOT NULL,
    scraper_type TEXT NOT NULL CHECK (scraper_type IN (
        'static_html', 'dynamic_js', 'api', 'rss_feed'
    )),
    
    -- Configuration
    selectors JSONB NOT NULL DEFAULT '{}',  -- CSS/XPath selectors
    expected_schema JSONB NOT NULL,  -- What data to expect
    authentication JSONB,  -- Encrypted credentials if needed
    
    -- Schedule
    frequency TEXT NOT NULL CHECK (frequency IN (
        'hourly', 'daily', 'weekly', 'monthly', 'on_demand'
    )),
    next_run_at TIMESTAMPTZ,
    
    -- Monitoring
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    alert_on_change BOOLEAN DEFAULT FALSE,
    alert_on_failure BOOLEAN DEFAULT TRUE,
    last_successful_run TIMESTAMPTZ,
    consecutive_failures INT DEFAULT 0,
    
    -- Metadata
    created_by UUID,  -- References auth.users(id) but no FK constraint
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_scraping_configs_enabled ON scraping_configs(enabled) WHERE enabled = TRUE;
CREATE INDEX IF NOT EXISTS idx_scraping_configs_next_run ON scraping_configs(next_run_at);

-- =====================================================
-- SCRAPED DATA
-- =====================================================

CREATE TABLE IF NOT EXISTS scraped_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id UUID NOT NULL REFERENCES scraping_configs(id) ON DELETE CASCADE,
    
    -- Raw data
    url TEXT NOT NULL,
    raw_html TEXT,
    raw_json JSONB,
    
    -- Extracted data
    structured_data JSONB NOT NULL,
    schema_valid BOOLEAN NOT NULL,
    
    -- Change detection
    data_hash TEXT NOT NULL,  -- For deduplication
    changed_from_previous BOOLEAN,
    diff_from_previous JSONB,
    
    -- Metadata
    scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    http_status INT,
    response_time_ms INT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_scraped_data_config_id ON scraped_data(config_id);
CREATE INDEX IF NOT EXISTS idx_scraped_data_scraped_at ON scraped_data(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_scraped_data_hash ON scraped_data(data_hash);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS
ALTER TABLE uploaded_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE extracted_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_processing_audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE scraping_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE scraped_data ENABLE ROW LEVEL SECURITY;

-- Policy: Org members can see internal documents in their org
CREATE POLICY "Org members can view documents"
    ON uploaded_documents FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM org_memberships 
            WHERE org_memberships.org_id = uploaded_documents.org_id
            AND org_memberships.user_id = auth.uid()
        )
    );

-- Policy: Org members can upload documents
CREATE POLICY "Org members can upload documents"
    ON uploaded_documents FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM org_memberships 
            WHERE org_memberships.org_id = uploaded_documents.org_id
            AND org_memberships.user_id = auth.uid()
            AND org_memberships.role IN ('owner', 'admin', 'member')
        )
    );

-- Policy: Service role full access
CREATE POLICY "Service role can manage documents"
    ON uploaded_documents FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Policy: Read access to extracted data follows document access
CREATE POLICY "Read extracted data if can read document"
    ON extracted_data FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM uploaded_documents
            WHERE uploaded_documents.id = extracted_data.document_id
        )
    );

-- Similar policies for other tables (inherit from document access)
CREATE POLICY "Read analyses if can read document"
    ON document_analyses FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM uploaded_documents
            WHERE uploaded_documents.id = document_analyses.document_id
        )
    );

CREATE POLICY "Read research if can read document"
    ON research_results FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM document_analyses
            JOIN uploaded_documents ON uploaded_documents.id = document_analyses.document_id
            WHERE document_analyses.id = research_results.analysis_id
        )
    );

CREATE POLICY "Read questions if can read document"
    ON generated_questions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM document_analyses
            JOIN uploaded_documents ON uploaded_documents.id = document_analyses.document_id
            WHERE document_analyses.id = generated_questions.analysis_id
        )
    );

CREATE POLICY "Read content if can read document"
    ON generated_content FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM document_analyses
            JOIN uploaded_documents ON uploaded_documents.id = document_analyses.document_id
            WHERE document_analyses.id = generated_content.analysis_id
        )
    );

-- Audit log: Service role only
CREATE POLICY "Service role can read audit logs"
    ON document_processing_audit_log FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Scraping configs: Service role only
CREATE POLICY "Service role can manage scraping configs"
    ON scraping_configs FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Scraped data: Service role only
CREATE POLICY "Service role can manage scraped data"
    ON scraped_data FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- =====================================================
-- TRIGGERS (Auto-update timestamps)
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_uploaded_documents_updated_at
    BEFORE UPDATE ON uploaded_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scraping_configs_updated_at
    BEFORE UPDATE ON scraping_configs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VIEWS (Useful queries)
-- =====================================================

-- View: Complete document pipeline status
CREATE OR REPLACE VIEW v_document_pipeline_status AS
SELECT 
    ud.id,
    ud.filename,
    ud.display_name,
    ud.document_type,
    ud.uploaded_at,
    ud.uploaded_by,
    ud.processing_status,
    ed.id AS extraction_id,
    ed.confidence_score AS extraction_confidence,
    da.id AS analysis_id,
    da.overall_confidence AS analysis_confidence,
    da.requires_human_review,
    COUNT(DISTINCT rr.id) AS research_count,
    COUNT(DISTINCT gq.id) AS questions_count,
    COUNT(DISTINCT gc.id) AS generated_content_count
FROM uploaded_documents ud
LEFT JOIN extracted_data ed ON ed.document_id = ud.id
LEFT JOIN document_analyses da ON da.document_id = ud.id
LEFT JOIN research_results rr ON rr.analysis_id = da.id
LEFT JOIN generated_questions gq ON gq.analysis_id = da.id
LEFT JOIN generated_content gc ON gc.analysis_id = da.id
GROUP BY ud.id, ed.id, da.id;

-- View: Documents requiring human review
CREATE OR REPLACE VIEW v_documents_requiring_review AS
SELECT 
    ud.id,
    ud.filename,
    ud.display_name,
    ud.document_type,
    ud.uploaded_at,
    da.overall_confidence,
    da.review_reason,
    da.gaps
FROM uploaded_documents ud
JOIN document_analyses da ON da.document_id = ud.id
WHERE da.requires_human_review = TRUE
AND da.reviewed_at IS NULL
ORDER BY ud.uploaded_at DESC;

-- =====================================================
-- FUNCTIONS (Utility)
-- =====================================================

-- Function: Get latest analysis for document
CREATE OR REPLACE FUNCTION get_latest_analysis(doc_id UUID)
RETURNS TABLE (
    analysis_id UUID,
    classification TEXT,
    overall_confidence FLOAT,
    key_metrics JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        da.id,
        da.classification,
        da.overall_confidence,
        da.key_metrics
    FROM document_analyses da
    WHERE da.document_id = doc_id
    ORDER BY da.analysis_version DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function: Calculate processing metrics
CREATE OR REPLACE FUNCTION get_processing_metrics(start_date TIMESTAMPTZ DEFAULT NOW() - INTERVAL '30 days')
RETURNS TABLE (
    total_documents INT,
    avg_confidence FLOAT,
    human_review_rate FLOAT,
    avg_processing_time_ms FLOAT,
    hallucination_incidents INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT ud.id)::INT,
        AVG(da.overall_confidence)::FLOAT,
        (COUNT(DISTINCT CASE WHEN da.requires_human_review THEN da.id END)::FLOAT / 
         NULLIF(COUNT(DISTINCT da.id), 0))::FLOAT,
        AVG(alog.processing_time_ms)::FLOAT,
        COUNT(DISTINCT CASE WHEN alog.action = 'hallucination_detected' THEN alog.id END)::INT
    FROM uploaded_documents ud
    LEFT JOIN document_analyses da ON da.document_id = ud.id
    LEFT JOIN document_processing_audit_log alog ON alog.document_id = ud.id
    WHERE ud.uploaded_at >= start_date;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMMENTS (Documentation)
-- =====================================================

COMMENT ON TABLE uploaded_documents IS 'Immutable source of truth for all uploaded documents';
COMMENT ON TABLE extracted_data IS 'Raw extracted data from documents (Agent 1: Extractor)';
COMMENT ON TABLE document_analyses IS 'Structured analysis of documents (Agent 2: Analyzer)';
COMMENT ON TABLE research_results IS 'Public data verification (Agent 3: Researcher)';
COMMENT ON TABLE generated_questions IS 'DD questions generated from gaps/risks (Agent 4: Question Generator)';
COMMENT ON TABLE generated_content IS 'Reports, memos, SWOT analysis (Agent 5: Content Generator)';
COMMENT ON TABLE document_processing_audit_log IS 'Complete audit trail of all processing steps';
COMMENT ON TABLE scraping_configs IS 'Configuration for automated web scraping';
COMMENT ON TABLE scraped_data IS 'Data collected from web scraping';

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

-- Verification query
DO $$
BEGIN
    RAISE NOTICE 'Migration 014 complete: Document Intelligence System';
    RAISE NOTICE 'Created % tables', (
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN (
            'uploaded_documents', 'extracted_data', 'document_analyses',
            'research_results', 'generated_questions', 'generated_content',
            'document_processing_audit_log', 'scraping_configs', 'scraped_data'
        )
    );
END $$;
