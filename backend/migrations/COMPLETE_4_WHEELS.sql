-- ============================================================================
-- COMPLETE 4-WHEEL VC OPERATING SYSTEM - ALL MIGRATIONS (009-012)
-- Copy this entire file and paste into Supabase SQL Editor
-- Safe to run - no conflicts with existing migrations
-- ============================================================================

-- ============================================================================
-- MIGRATION 009: PEOPLE WHEEL
-- ============================================================================

-- Extend existing policy_documents (from migration 007)
ALTER TABLE policy_documents ADD COLUMN IF NOT EXISTS generated_by_ai BOOLEAN DEFAULT false;
ALTER TABLE policy_documents ADD COLUMN IF NOT EXISTS generation_prompt TEXT;
ALTER TABLE policy_documents ADD COLUMN IF NOT EXISTS policy_content TEXT;

-- Extend existing policy_acknowledgments (from migration 007)
ALTER TABLE policy_acknowledgments ADD COLUMN IF NOT EXISTS version_acknowledged TEXT;
ALTER TABLE policy_acknowledgments ADD COLUMN IF NOT EXISTS meeting_id UUID REFERENCES meetings(id);

-- Contracts (NEW)
CREATE TABLE IF NOT EXISTS contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    contract_type TEXT NOT NULL,
    contract_name TEXT,
    template_id UUID REFERENCES contracts(id),
    party_organization_id UUID REFERENCES organizations(id),
    party_person_id UUID REFERENCES people(id),
    start_date DATE,
    end_date DATE,
    value DECIMAL,
    currency TEXT DEFAULT 'SEK',
    terms JSONB,
    contract_content TEXT,
    google_doc_id TEXT,
    signed_pdf_url TEXT,
    status TEXT DEFAULT 'draft',
    signed_at TIMESTAMPTZ,
    signed_by UUID REFERENCES people(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_contracts_org ON contracts(org_id);

-- Role descriptions (NEW)
CREATE TABLE IF NOT EXISTS role_descriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    role_title TEXT NOT NULL,
    role_level TEXT,
    department TEXT,
    description TEXT,
    responsibilities TEXT[],
    requirements TEXT[],
    nice_to_have TEXT[],
    salary_range_min DECIMAL,
    salary_range_max DECIMAL,
    currency TEXT DEFAULT 'SEK',
    equity_range TEXT,
    is_hiring BOOLEAN DEFAULT false,
    status TEXT DEFAULT 'draft',
    google_doc_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_role_descriptions_org ON role_descriptions(org_id);

-- Recruitment candidates (NEW)
CREATE TABLE IF NOT EXISTS recruitment_candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    role_id UUID REFERENCES role_descriptions(id),
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    linkedin_url TEXT,
    source TEXT,
    referrer_id UUID REFERENCES people(id),
    resume_url TEXT,
    cover_letter TEXT,
    ai_score FLOAT,
    ai_summary TEXT,
    strengths TEXT[],
    concerns TEXT[],
    stage TEXT DEFAULT 'applied',
    stage_changed_at TIMESTAMPTZ DEFAULT NOW(),
    interviews JSONB,
    decision TEXT,
    decision_reason TEXT,
    decision_by UUID REFERENCES people(id),
    decision_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_candidates_org ON recruitment_candidates(org_id);

-- Recruitment notes (NEW)
CREATE TABLE IF NOT EXISTS recruitment_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES recruitment_candidates(id) ON DELETE CASCADE,
    author_id UUID REFERENCES people(id),
    note_type TEXT,
    note_content TEXT,
    meeting_id UUID REFERENCES meetings(id),
    sentiment TEXT,
    key_points TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_recruitment_notes_candidate ON recruitment_notes(candidate_id);

-- Competencies (NEW)
CREATE TABLE IF NOT EXISTS person_competencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    skill_name TEXT NOT NULL,
    skill_category TEXT,
    proficiency_level TEXT,
    source TEXT,
    extracted_by_ai BOOLEAN DEFAULT false,
    evidence TEXT[],
    verified_by UUID REFERENCES people(id),
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_competencies_person ON person_competencies(person_id);

-- CVs (NEW)
CREATE TABLE IF NOT EXISTS person_cvs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    cv_filename TEXT,
    cv_file_url TEXT,
    google_drive_file_id TEXT,
    cv_text TEXT,
    structured_data JSONB,
    extracted_competencies TEXT[],
    ai_generated_summary TEXT,
    is_primary BOOLEAN DEFAULT true,
    parse_status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cvs_person ON person_cvs(person_id);

-- Google profile syncs (NEW)
CREATE TABLE IF NOT EXISTS google_profile_syncs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    google_user_id TEXT,
    google_email TEXT,
    last_sync_at TIMESTAMPTZ,
    sync_status TEXT,
    sync_error TEXT,
    synced_fields JSONB,
    current_profile_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(person_id)
);

CREATE INDEX IF NOT EXISTS idx_google_syncs_person ON google_profile_syncs(person_id);

-- Google contacts syncs (NEW)
CREATE TABLE IF NOT EXISTS google_contacts_syncs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    google_resource_name TEXT,
    google_contact_groups TEXT[],
    last_sync_at TIMESTAMPTZ,
    sync_status TEXT,
    sync_error TEXT,
    synced_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(entity_type, entity_id)
);

CREATE INDEX IF NOT EXISTS idx_google_contacts_syncs_entity ON google_contacts_syncs(entity_type, entity_id);

-- ============================================================================
-- MIGRATION 010: DEALFLOW WHEEL
-- ============================================================================

-- Dealflow leads (NEW)
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

-- Dealflow research (NEW)
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

-- Market analyses (NEW)
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

-- Dealflow outreach (NEW)
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
-- MIGRATION 011: BUILDING COMPANIES WHEEL
-- ============================================================================

-- Portfolio companies (NEW)
CREATE TABLE IF NOT EXISTS portfolio_companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    dv_org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    investment_date DATE,
    investment_amount DECIMAL,
    investment_stage TEXT,
    current_valuation DECIMAL,
    ownership_percentage FLOAT,
    lead_partner_id UUID REFERENCES people(id),
    board_seat BOOLEAN DEFAULT false,
    target_stage TEXT,
    target_date DATE,
    target_valuation DECIMAL,
    qualification_score FLOAT,
    qualification_status TEXT,
    last_qualification_check TIMESTAMPTZ,
    ceo_dashboard_enabled BOOLEAN DEFAULT true,
    dashboard_url TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organization_id)
);

CREATE INDEX IF NOT EXISTS idx_portfolio_companies_dv_org ON portfolio_companies(dv_org_id);

-- Portfolio targets (NEW)
CREATE TABLE IF NOT EXISTS portfolio_targets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_company_id UUID NOT NULL REFERENCES portfolio_companies(id) ON DELETE CASCADE,
    target_category TEXT NOT NULL,
    target_name TEXT NOT NULL,
    target_description TEXT,
    metric_name TEXT,
    target_value DECIMAL,
    current_value DECIMAL,
    unit TEXT,
    deadline DATE,
    is_critical BOOLEAN DEFAULT false,
    progress_percentage FLOAT,
    status TEXT,
    last_updated_at TIMESTAMPTZ,
    last_updated_by UUID REFERENCES people(id),
    update_frequency TEXT DEFAULT 'weekly',
    ai_prediction TEXT,
    ai_recommendations TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_portfolio_targets_company ON portfolio_targets(portfolio_company_id);

-- Target updates (NEW)
CREATE TABLE IF NOT EXISTS target_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_id UUID NOT NULL REFERENCES portfolio_targets(id) ON DELETE CASCADE,
    new_value DECIMAL,
    previous_value DECIMAL,
    change DECIMAL,
    change_percentage FLOAT,
    update_note TEXT,
    updated_by UUID REFERENCES people(id),
    update_source TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_target_updates_target ON target_updates(target_id);

-- Qualification criteria (NEW)
CREATE TABLE IF NOT EXISTS qualification_criteria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dv_org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    stage TEXT NOT NULL,
    criteria_name TEXT NOT NULL,
    criteria_category TEXT,
    requirement_type TEXT,
    minimum_value DECIMAL,
    target_value DECIMAL,
    weight FLOAT,
    is_mandatory BOOLEAN DEFAULT false,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_qualification_criteria_org ON qualification_criteria(dv_org_id);

-- CEO dashboard configs (NEW)
CREATE TABLE IF NOT EXISTS ceo_dashboard_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_company_id UUID NOT NULL REFERENCES portfolio_companies(id) ON DELETE CASCADE,
    visible_sections TEXT[],
    custom_metrics JSONB,
    can_update_targets BOOLEAN DEFAULT true,
    can_request_support BOOLEAN DEFAULT true,
    can_view_dv_notes BOOLEAN DEFAULT false,
    logo_url TEXT,
    theme_color TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(portfolio_company_id)
);

-- Support requests (NEW)
CREATE TABLE IF NOT EXISTS portfolio_support_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_company_id UUID NOT NULL REFERENCES portfolio_companies(id) ON DELETE CASCADE,
    requested_by UUID REFERENCES people(id),
    request_type TEXT,
    subject TEXT NOT NULL,
    description TEXT,
    urgency TEXT DEFAULT 'normal',
    assigned_to UUID REFERENCES people(id),
    status TEXT DEFAULT 'new',
    response TEXT,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_support_requests_company ON portfolio_support_requests(portfolio_company_id);

-- ============================================================================
-- MIGRATION 012: ADMIN WHEEL
-- ============================================================================

-- DV dashboard configs (NEW)
CREATE TABLE IF NOT EXISTS dv_dashboard_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    visible_wheels TEXT[],
    default_view TEXT,
    widgets JSONB,
    saved_filters JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, org_id)
);

-- DV alerts (NEW)
CREATE TABLE IF NOT EXISTS dv_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    alert_type TEXT NOT NULL,
    severity TEXT DEFAULT 'info',
    title TEXT NOT NULL,
    description TEXT,
    related_entity_type TEXT,
    related_entity_id UUID,
    assigned_to UUID REFERENCES people(id),
    status TEXT DEFAULT 'new',
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    suggested_actions TEXT[],
    action_taken TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dv_alerts_org ON dv_alerts(org_id);

-- Materialized views (NEW)
CREATE MATERIALIZED VIEW IF NOT EXISTS dv_portfolio_health AS
SELECT
    pc.id as portfolio_company_id,
    pc.organization_id,
    o.name as company_name,
    pc.investment_stage,
    pc.qualification_score,
    pc.qualification_status,
    COUNT(DISTINCT pt.id) as total_targets,
    SUM(CASE WHEN pt.status = 'achieved' THEN 1 ELSE 0 END) as targets_achieved,
    SUM(CASE WHEN pt.status = 'at_risk' THEN 1 ELSE 0 END) as targets_at_risk,
    AVG(pt.progress_percentage) as avg_progress
FROM portfolio_companies pc
JOIN organizations o ON pc.organization_id = o.id
LEFT JOIN portfolio_targets pt ON pt.portfolio_company_id = pc.id
WHERE pc.status = 'active'
GROUP BY pc.id, pc.organization_id, o.name, pc.investment_stage, pc.qualification_score, pc.qualification_status;

CREATE MATERIALIZED VIEW IF NOT EXISTS dv_dealflow_metrics AS
SELECT
    COUNT(*) as total_leads,
    SUM(CASE WHEN ai_qualification_score >= 70 THEN 1 ELSE 0 END) as qualified_leads,
    SUM(CASE WHEN stage = 'meeting_scheduled' THEN 1 ELSE 0 END) as meetings_scheduled,
    AVG(ai_qualification_score) as avg_score
FROM dealflow_leads
WHERE created_at >= NOW() - INTERVAL '12 months';

-- ============================================================================
-- TRIGGERS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_four_wheels_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_contracts_updated_at ON contracts;
CREATE TRIGGER update_contracts_updated_at BEFORE UPDATE ON contracts FOR EACH ROW EXECUTE FUNCTION update_four_wheels_updated_at();

DROP TRIGGER IF EXISTS update_role_descriptions_updated_at ON role_descriptions;
CREATE TRIGGER update_role_descriptions_updated_at BEFORE UPDATE ON role_descriptions FOR EACH ROW EXECUTE FUNCTION update_four_wheels_updated_at();

DROP TRIGGER IF EXISTS update_recruitment_candidates_updated_at ON recruitment_candidates;
CREATE TRIGGER update_recruitment_candidates_updated_at BEFORE UPDATE ON recruitment_candidates FOR EACH ROW EXECUTE FUNCTION update_four_wheels_updated_at();

DROP TRIGGER IF EXISTS update_person_competencies_updated_at ON person_competencies;
CREATE TRIGGER update_person_competencies_updated_at BEFORE UPDATE ON person_competencies FOR EACH ROW EXECUTE FUNCTION update_four_wheels_updated_at();

DROP TRIGGER IF EXISTS update_person_cvs_updated_at ON person_cvs;
CREATE TRIGGER update_person_cvs_updated_at BEFORE UPDATE ON person_cvs FOR EACH ROW EXECUTE FUNCTION update_four_wheels_updated_at();

DROP TRIGGER IF EXISTS update_google_profile_syncs_updated_at ON google_profile_syncs;
CREATE TRIGGER update_google_profile_syncs_updated_at BEFORE UPDATE ON google_profile_syncs FOR EACH ROW EXECUTE FUNCTION update_four_wheels_updated_at();

DROP TRIGGER IF EXISTS update_google_contacts_syncs_updated_at ON google_contacts_syncs;
CREATE TRIGGER update_google_contacts_syncs_updated_at BEFORE UPDATE ON google_contacts_syncs FOR EACH ROW EXECUTE FUNCTION update_four_wheels_updated_at();

DROP TRIGGER IF EXISTS update_dealflow_leads_updated_at ON dealflow_leads;
CREATE TRIGGER update_dealflow_leads_updated_at BEFORE UPDATE ON dealflow_leads FOR EACH ROW EXECUTE FUNCTION update_four_wheels_updated_at();

DROP TRIGGER IF EXISTS update_portfolio_companies_updated_at ON portfolio_companies;
CREATE TRIGGER update_portfolio_companies_updated_at BEFORE UPDATE ON portfolio_companies FOR EACH ROW EXECUTE FUNCTION update_four_wheels_updated_at();

DROP TRIGGER IF EXISTS update_portfolio_targets_updated_at ON portfolio_targets;
CREATE TRIGGER update_portfolio_targets_updated_at BEFORE UPDATE ON portfolio_targets FOR EACH ROW EXECUTE FUNCTION update_four_wheels_updated_at();

DROP TRIGGER IF EXISTS update_ceo_dashboard_configs_updated_at ON ceo_dashboard_configs;
CREATE TRIGGER update_ceo_dashboard_configs_updated_at BEFORE UPDATE ON ceo_dashboard_configs FOR EACH ROW EXECUTE FUNCTION update_four_wheels_updated_at();

DROP TRIGGER IF EXISTS update_portfolio_support_requests_updated_at ON portfolio_support_requests;
CREATE TRIGGER update_portfolio_support_requests_updated_at BEFORE UPDATE ON portfolio_support_requests FOR EACH ROW EXECUTE FUNCTION update_four_wheels_updated_at();

DROP TRIGGER IF EXISTS update_dv_dashboard_configs_updated_at ON dv_dashboard_configs;
CREATE TRIGGER update_dv_dashboard_configs_updated_at BEFORE UPDATE ON dv_dashboard_configs FOR EACH ROW EXECUTE FUNCTION update_four_wheels_updated_at();

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

ALTER TABLE contracts ENABLE ROW LEVEL SECURITY;
ALTER TABLE role_descriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE recruitment_candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE recruitment_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE person_competencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE person_cvs ENABLE ROW LEVEL SECURITY;
ALTER TABLE google_profile_syncs ENABLE ROW LEVEL SECURITY;
ALTER TABLE google_contacts_syncs ENABLE ROW LEVEL SECURITY;
ALTER TABLE dealflow_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE dealflow_research ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE dealflow_outreach ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_targets ENABLE ROW LEVEL SECURITY;
ALTER TABLE target_updates ENABLE ROW LEVEL SECURITY;
ALTER TABLE qualification_criteria ENABLE ROW LEVEL SECURITY;
ALTER TABLE ceo_dashboard_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_support_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE dv_dashboard_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE dv_alerts ENABLE ROW LEVEL SECURITY;

-- PEOPLE Wheel policies
CREATE POLICY "contracts_admin" ON contracts FOR ALL USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));
CREATE POLICY "contracts_service" ON contracts FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "roles_view" ON role_descriptions FOR SELECT USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid()) AND status = 'active');
CREATE POLICY "roles_admin" ON role_descriptions FOR ALL USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));
CREATE POLICY "roles_service" ON role_descriptions FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "candidates_admin" ON recruitment_candidates FOR ALL USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));
CREATE POLICY "candidates_service" ON recruitment_candidates FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "notes_admin" ON recruitment_notes FOR ALL USING (candidate_id IN (SELECT rc.id FROM recruitment_candidates rc JOIN org_memberships om ON om.org_id = rc.org_id WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));
CREATE POLICY "notes_service" ON recruitment_notes FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "comp_view" ON person_competencies FOR SELECT USING (person_id IN (SELECT p.id FROM people p JOIN org_memberships om ON om.org_id = p.org_id WHERE om.user_id = auth.uid()));
CREATE POLICY "comp_admin" ON person_competencies FOR ALL USING (person_id IN (SELECT p.id FROM people p JOIN org_memberships om ON om.org_id = p.org_id WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));
CREATE POLICY "comp_service" ON person_competencies FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "cvs_view" ON person_cvs FOR SELECT USING (person_id IN (SELECT p.id FROM people p JOIN org_memberships om ON om.org_id = p.org_id WHERE om.user_id = auth.uid()));
CREATE POLICY "cvs_admin" ON person_cvs FOR ALL USING (person_id IN (SELECT p.id FROM people p JOIN org_memberships om ON om.org_id = p.org_id WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));
CREATE POLICY "cvs_service" ON person_cvs FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "profile_sync_admin" ON google_profile_syncs FOR ALL USING (person_id IN (SELECT p.id FROM people p JOIN org_memberships om ON om.org_id = p.org_id WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));
CREATE POLICY "profile_sync_service" ON google_profile_syncs FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "contacts_sync_admin" ON google_contacts_syncs FOR ALL USING (EXISTS (SELECT 1 FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));
CREATE POLICY "contacts_sync_service" ON google_contacts_syncs FOR ALL USING (auth.jwt()->>'role' = 'service_role');

-- DEALFLOW Wheel policies
CREATE POLICY "leads_view" ON dealflow_leads FOR SELECT USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid()));
CREATE POLICY "leads_manage" ON dealflow_leads FOR ALL USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member')));
CREATE POLICY "leads_service" ON dealflow_leads FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "research_view" ON dealflow_research FOR SELECT USING (lead_id IN (SELECT id FROM dealflow_leads WHERE org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid())));
CREATE POLICY "research_manage" ON dealflow_research FOR ALL USING (lead_id IN (SELECT id FROM dealflow_leads WHERE org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member'))));
CREATE POLICY "research_service" ON dealflow_research FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "market_view" ON market_analyses FOR SELECT USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid()));
CREATE POLICY "market_manage" ON market_analyses FOR ALL USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member')));
CREATE POLICY "market_service" ON market_analyses FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "outreach_view" ON dealflow_outreach FOR SELECT USING (lead_id IN (SELECT id FROM dealflow_leads WHERE org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid())));
CREATE POLICY "outreach_manage" ON dealflow_outreach FOR ALL USING (lead_id IN (SELECT id FROM dealflow_leads WHERE org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member'))));
CREATE POLICY "outreach_service" ON dealflow_outreach FOR ALL USING (auth.jwt()->>'role' = 'service_role');

-- BUILDING Wheel policies
CREATE POLICY "portfolio_admin" ON portfolio_companies FOR ALL USING (dv_org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member')));
CREATE POLICY "portfolio_ceo_view" ON portfolio_companies FOR SELECT USING (organization_id IN (SELECT p.primary_organization_id FROM people p WHERE p.email = auth.email()));
CREATE POLICY "portfolio_service" ON portfolio_companies FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "targets_admin" ON portfolio_targets FOR ALL USING (portfolio_company_id IN (SELECT id FROM portfolio_companies WHERE dv_org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member'))));
CREATE POLICY "targets_ceo_view" ON portfolio_targets FOR SELECT USING (portfolio_company_id IN (SELECT pc.id FROM portfolio_companies pc JOIN people p ON p.primary_organization_id = pc.organization_id WHERE p.email = auth.email()));
CREATE POLICY "targets_ceo_update" ON portfolio_targets FOR UPDATE USING (portfolio_company_id IN (SELECT pc.id FROM portfolio_companies pc JOIN people p ON p.primary_organization_id = pc.organization_id WHERE p.email = auth.email()));
CREATE POLICY "targets_service" ON portfolio_targets FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "updates_view" ON target_updates FOR SELECT USING (target_id IN (SELECT id FROM portfolio_targets));
CREATE POLICY "updates_create" ON target_updates FOR INSERT WITH CHECK (target_id IN (SELECT id FROM portfolio_targets));
CREATE POLICY "updates_service" ON target_updates FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "criteria_view" ON qualification_criteria FOR SELECT USING (dv_org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid()));
CREATE POLICY "criteria_admin" ON qualification_criteria FOR ALL USING (dv_org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));
CREATE POLICY "criteria_service" ON qualification_criteria FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "ceo_dash_ceo" ON ceo_dashboard_configs FOR ALL USING (portfolio_company_id IN (SELECT pc.id FROM portfolio_companies pc JOIN people p ON p.primary_organization_id = pc.organization_id WHERE p.email = auth.email()));
CREATE POLICY "ceo_dash_admin" ON ceo_dashboard_configs FOR ALL USING (portfolio_company_id IN (SELECT id FROM portfolio_companies WHERE dv_org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member'))));
CREATE POLICY "ceo_dash_service" ON ceo_dashboard_configs FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "support_ceo_create" ON portfolio_support_requests FOR INSERT WITH CHECK (portfolio_company_id IN (SELECT pc.id FROM portfolio_companies pc JOIN people p ON p.primary_organization_id = pc.organization_id WHERE p.email = auth.email()));
CREATE POLICY "support_ceo_view" ON portfolio_support_requests FOR SELECT USING (portfolio_company_id IN (SELECT pc.id FROM portfolio_companies pc JOIN people p ON p.primary_organization_id = pc.organization_id WHERE p.email = auth.email()));
CREATE POLICY "support_dv_manage" ON portfolio_support_requests FOR ALL USING (portfolio_company_id IN (SELECT id FROM portfolio_companies WHERE dv_org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid())));
CREATE POLICY "support_service" ON portfolio_support_requests FOR ALL USING (auth.jwt()->>'role' = 'service_role');

-- ADMIN Wheel policies
CREATE POLICY "dash_config_own" ON dv_dashboard_configs FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "dash_config_service" ON dv_dashboard_configs FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "alerts_view" ON dv_alerts FOR SELECT USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid()));
CREATE POLICY "alerts_create" ON dv_alerts FOR INSERT WITH CHECK (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member')));
CREATE POLICY "alerts_update" ON dv_alerts FOR UPDATE USING (assigned_to IN (SELECT p.id FROM people p JOIN org_memberships om ON om.org_id = p.org_id WHERE om.user_id = auth.uid()) OR org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));
CREATE POLICY "alerts_service" ON dv_alerts FOR ALL USING (auth.jwt()->>'role' = 'service_role');

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

SELECT '4-Wheel VC Operating System migrations completed!' AS status;
SELECT 'Created: 18 new tables + 2 materialized views' AS summary;


