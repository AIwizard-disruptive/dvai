-- ============================================================================
-- MIGRATION 010: DEALFLOW WHEEL (CLEAN)
-- Lead qualification, research, outreach automation
-- ============================================================================

-- Inbound leads (NEW)
CREATE TABLE IF NOT EXISTS dealflow_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    company_name TEXT NOT NULL,
    website TEXT,
    domain TEXT,
    founder_name TEXT,
    founder_email TEXT,
    founder_linkedin TEXT,
    source TEXT,
    source_details TEXT,
    referrer_id UUID REFERENCES people(id),
    pitch_deck_url TEXT,
    one_liner TEXT,
    company_stage TEXT,
    ai_qualification_score FLOAT,
    ai_qualification_reason TEXT,
    meets_thesis BOOLEAN,
    thesis_match_reason TEXT,
    research_status TEXT DEFAULT 'pending',
    research_completed_at TIMESTAMPTZ,
    stage TEXT DEFAULT 'new',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dealflow_leads_org ON dealflow_leads(org_id);
CREATE INDEX IF NOT EXISTS idx_dealflow_leads_stage ON dealflow_leads(stage);
CREATE INDEX IF NOT EXISTS idx_dealflow_leads_score ON dealflow_leads(ai_qualification_score);

-- AI-generated research (NEW)
CREATE TABLE IF NOT EXISTS dealflow_research (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL REFERENCES dealflow_leads(id) ON DELETE CASCADE,
    market_size TEXT,
    market_trends TEXT[],
    competitors TEXT[],
    competitive_advantages TEXT[],
    product_analysis TEXT,
    business_model_analysis TEXT,
    traction_metrics JSONB,
    founder_backgrounds TEXT[],
    team_strengths TEXT[],
    team_gaps TEXT[],
    investment_opportunity TEXT,
    key_risks TEXT[],
    suggested_questions TEXT[],
    sources_used TEXT[],
    generated_by TEXT,
    generation_time_ms INTEGER,
    google_doc_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dealflow_research_lead ON dealflow_research(lead_id);

-- Market analysis cache (NEW)
CREATE TABLE IF NOT EXISTS market_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    market_name TEXT NOT NULL,
    market_category TEXT,
    market_size_tam TEXT,
    market_size_sam TEXT,
    growth_rate TEXT,
    key_trends TEXT[],
    key_players TEXT[],
    investment_attractiveness TEXT,
    key_risks TEXT[],
    sources TEXT[],
    last_updated TIMESTAMPTZ,
    google_doc_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_market_analyses_org ON market_analyses(org_id);
CREATE INDEX IF NOT EXISTS idx_market_analyses_name ON market_analyses(market_name);

-- Automated outreach (NEW)
CREATE TABLE IF NOT EXISTS dealflow_outreach (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL REFERENCES dealflow_leads(id) ON DELETE CASCADE,
    campaign_type TEXT,
    subject TEXT,
    body TEXT,
    sent_at TIMESTAMPTZ,
    sent_via TEXT,
    opened_at TIMESTAMPTZ,
    replied_at TIMESTAMPTZ,
    reply_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dealflow_outreach_lead ON dealflow_outreach(lead_id);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_dealflow_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_dealflow_leads_updated_at ON dealflow_leads;
CREATE TRIGGER update_dealflow_leads_updated_at BEFORE UPDATE ON dealflow_leads FOR EACH ROW EXECUTE FUNCTION update_dealflow_updated_at();

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

ALTER TABLE dealflow_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE dealflow_research ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE dealflow_outreach ENABLE ROW LEVEL SECURITY;

-- Dealflow leads
CREATE POLICY "Org members view leads" ON dealflow_leads FOR SELECT
    USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid()));

CREATE POLICY "Org members manage leads" ON dealflow_leads FOR ALL
    USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member')));

CREATE POLICY "Service role dealflow_leads" ON dealflow_leads FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Dealflow research
CREATE POLICY "Org members view research" ON dealflow_research FOR SELECT
    USING (lead_id IN (SELECT id FROM dealflow_leads WHERE org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid())));

CREATE POLICY "Org members manage research" ON dealflow_research FOR ALL
    USING (lead_id IN (SELECT id FROM dealflow_leads WHERE org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member'))));

CREATE POLICY "Service role dealflow_research" ON dealflow_research FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Market analyses
CREATE POLICY "Org members view market" ON market_analyses FOR SELECT
    USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid()));

CREATE POLICY "Org members manage market" ON market_analyses FOR ALL
    USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member')));

CREATE POLICY "Service role market_analyses" ON market_analyses FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Dealflow outreach
CREATE POLICY "Org members view outreach" ON dealflow_outreach FOR SELECT
    USING (lead_id IN (SELECT id FROM dealflow_leads WHERE org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid())));

CREATE POLICY "Org members manage outreach" ON dealflow_outreach FOR ALL
    USING (lead_id IN (SELECT id FROM dealflow_leads WHERE org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member'))));

CREATE POLICY "Service role dealflow_outreach" ON dealflow_outreach FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE dealflow_leads IS 'Inbound leads with AI qualification and pipeline tracking';
COMMENT ON TABLE dealflow_research IS 'AI-generated research reports for qualified leads';
COMMENT ON TABLE market_analyses IS 'Reusable market analysis cache across leads';
COMMENT ON TABLE dealflow_outreach IS 'Automated outreach campaigns with tracking';
