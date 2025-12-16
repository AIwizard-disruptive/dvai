-- ============================================================================
-- MIGRATION 010: DEALFLOW WHEEL  
-- Lead qualification, research, outreach automation
-- ============================================================================

-- Inbound leads
CREATE TABLE IF NOT EXISTS dealflow_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    
    -- Company info
    company_name TEXT NOT NULL,
    website TEXT,
    domain TEXT,
    
    -- Contact
    founder_name TEXT,
    founder_email TEXT,
    founder_linkedin TEXT,
    
    -- Source
    source TEXT, -- 'email', 'website_form', 'linkedin', 'referral', 'event'
    source_details TEXT,
    referrer_id UUID REFERENCES people(id),
    
    -- Initial info
    pitch_deck_url TEXT,
    one_liner TEXT,
    company_stage TEXT, -- 'idea', 'mvp', 'revenue', 'growth'
    
    -- AI qualification (immediate)
    ai_qualification_score FLOAT, -- 0-100
    ai_qualification_reason TEXT,
    meets_thesis BOOLEAN,
    thesis_match_reason TEXT,
    
    -- Research status
    research_status TEXT DEFAULT 'pending', -- 'pending', 'in_progress', 'completed'
    research_completed_at TIMESTAMPTZ,
    
    -- Pipeline stage
    stage TEXT DEFAULT 'new', -- 'new', 'researching', 'meeting_scheduled', 'diligence', 'term_sheet', 'closed_won', 'closed_lost'
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dealflow_leads_org ON dealflow_leads(org_id);
CREATE INDEX IF NOT EXISTS idx_dealflow_leads_stage ON dealflow_leads(stage);
CREATE INDEX IF NOT EXISTS idx_dealflow_leads_score ON dealflow_leads(ai_qualification_score);
CREATE INDEX IF NOT EXISTS idx_dealflow_leads_email ON dealflow_leads(founder_email);
CREATE INDEX IF NOT EXISTS idx_dealflow_leads_domain ON dealflow_leads(domain);
CREATE INDEX IF NOT EXISTS idx_dealflow_leads_source ON dealflow_leads(source);

-- AI-generated research
CREATE TABLE IF NOT EXISTS dealflow_research (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL REFERENCES dealflow_leads(id) ON DELETE CASCADE,
    
    -- Market analysis
    market_size TEXT, -- TAM, SAM, SOM analysis
    market_trends TEXT[],
    competitors TEXT[], -- List of competitors
    competitive_advantages TEXT[],
    
    -- Company analysis
    product_analysis TEXT,
    business_model_analysis TEXT,
    traction_metrics JSONB,
    
    -- Team analysis
    founder_backgrounds TEXT[],
    team_strengths TEXT[],
    team_gaps TEXT[],
    
    -- Investment perspective
    investment_opportunity TEXT,
    key_risks TEXT[],
    suggested_questions TEXT[], -- For first meeting
    
    -- Sources
    sources_used TEXT[], -- URLs, reports used
    
    -- AI metadata
    generated_by TEXT, -- 'gpt-4', etc.
    generation_time_ms INTEGER,
    
    -- Storage
    google_doc_id TEXT, -- Full research report in Google Docs
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dealflow_research_lead ON dealflow_research(lead_id);

-- Market analysis cache (reusable across leads)
CREATE TABLE IF NOT EXISTS market_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    
    -- Market definition
    market_name TEXT NOT NULL,
    market_category TEXT,
    
    -- Analysis
    market_size_tam TEXT,
    market_size_sam TEXT,
    growth_rate TEXT,
    key_trends TEXT[],
    key_players TEXT[],
    
    -- Investment perspective
    investment_attractiveness TEXT,
    key_risks TEXT[],
    
    -- Sources
    sources TEXT[],
    last_updated TIMESTAMPTZ,
    
    -- Storage
    google_doc_id TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_market_analyses_org ON market_analyses(org_id);
CREATE INDEX IF NOT EXISTS idx_market_analyses_name ON market_analyses(market_name);
CREATE INDEX IF NOT EXISTS idx_market_analyses_category ON market_analyses(market_category);

-- Automated outreach
CREATE TABLE IF NOT EXISTS dealflow_outreach (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL REFERENCES dealflow_leads(id) ON DELETE CASCADE,
    
    -- Campaign
    campaign_type TEXT, -- 'initial_outreach', 'follow_up', 'rejection', 'invitation'
    
    -- Generated email
    subject TEXT,
    body TEXT, -- AI-generated personalized email
    
    -- Sending
    sent_at TIMESTAMPTZ,
    sent_via TEXT, -- 'gmail', 'manual'
    
    -- Tracking
    opened_at TIMESTAMPTZ,
    replied_at TIMESTAMPTZ,
    reply_text TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dealflow_outreach_lead ON dealflow_outreach(lead_id);
CREATE INDEX IF NOT EXISTS idx_dealflow_outreach_campaign ON dealflow_outreach(campaign_type);
CREATE INDEX IF NOT EXISTS idx_dealflow_outreach_sent ON dealflow_outreach(sent_at);

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_dealflow_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_dealflow_leads_updated_at
    BEFORE UPDATE ON dealflow_leads
    FOR EACH ROW
    EXECUTE FUNCTION update_dealflow_updated_at();

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE dealflow_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE dealflow_research ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE dealflow_outreach ENABLE ROW LEVEL SECURITY;

-- Dealflow Leads: All org members can view, admins can manage
CREATE POLICY "Org members can view dealflow leads"
    ON dealflow_leads FOR SELECT
    USING (
        org_id IN (
            SELECT om.org_id FROM org_memberships om
            WHERE om.user_id = auth.uid()
        )
    );

CREATE POLICY "Org admins can manage dealflow leads"
    ON dealflow_leads FOR ALL
    USING (
        org_id IN (
            SELECT om.org_id FROM org_memberships om
            WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member')
        )
    );

-- Dealflow Research: Linked to leads (same access)
CREATE POLICY "Org members can view dealflow research"
    ON dealflow_research FOR SELECT
    USING (
        lead_id IN (
            SELECT id FROM dealflow_leads
            WHERE org_id IN (
                SELECT om.org_id FROM org_memberships om
                WHERE om.user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Org admins can manage dealflow research"
    ON dealflow_research FOR ALL
    USING (
        lead_id IN (
            SELECT id FROM dealflow_leads
            WHERE org_id IN (
                SELECT om.org_id FROM org_memberships om
                WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member')
            )
        )
    );

-- Market Analyses: All org members can view
CREATE POLICY "Org members can view market analyses"
    ON market_analyses FOR SELECT
    USING (
        org_id IN (
            SELECT om.org_id FROM org_memberships om
            WHERE om.user_id = auth.uid()
        )
    );

CREATE POLICY "Org admins can manage market analyses"
    ON market_analyses FOR ALL
    USING (
        org_id IN (
            SELECT om.org_id FROM org_memberships om
            WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member')
        )
    );

-- Dealflow Outreach: Linked to leads
CREATE POLICY "Org members can view dealflow outreach"
    ON dealflow_outreach FOR SELECT
    USING (
        lead_id IN (
            SELECT id FROM dealflow_leads
            WHERE org_id IN (
                SELECT om.org_id FROM org_memberships om
                WHERE om.user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Org admins can manage dealflow outreach"
    ON dealflow_outreach FOR ALL
    USING (
        lead_id IN (
            SELECT id FROM dealflow_leads
            WHERE org_id IN (
                SELECT om.org_id FROM org_memberships om
                WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member')
            )
        )
    );

-- Service role access (for automated tasks)
CREATE POLICY "Service role dealflow_leads" ON dealflow_leads FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role dealflow_research" ON dealflow_research FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role market_analyses" ON market_analyses FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role dealflow_outreach" ON dealflow_outreach FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE dealflow_leads IS 'Inbound leads with AI qualification and pipeline tracking';
COMMENT ON TABLE dealflow_research IS 'AI-generated research reports for qualified leads';
COMMENT ON TABLE market_analyses IS 'Reusable market analysis cache across leads';
COMMENT ON TABLE dealflow_outreach IS 'Automated outreach campaigns with tracking';
