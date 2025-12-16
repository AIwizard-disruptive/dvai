-- ============================================================================
-- MIGRATION 011: BUILDING COMPANIES WHEEL (CLEAN)
-- Portfolio support, target tracking, CEO dashboards, qualification
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
CREATE INDEX IF NOT EXISTS idx_portfolio_companies_status ON portfolio_companies(status);

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
CREATE INDEX IF NOT EXISTS idx_portfolio_targets_status ON portfolio_targets(status);

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
CREATE INDEX IF NOT EXISTS idx_support_requests_status ON portfolio_support_requests(status);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_building_companies_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_portfolio_companies_updated_at ON portfolio_companies;
CREATE TRIGGER update_portfolio_companies_updated_at BEFORE UPDATE ON portfolio_companies FOR EACH ROW EXECUTE FUNCTION update_building_companies_updated_at();

DROP TRIGGER IF EXISTS update_portfolio_targets_updated_at ON portfolio_targets;
CREATE TRIGGER update_portfolio_targets_updated_at BEFORE UPDATE ON portfolio_targets FOR EACH ROW EXECUTE FUNCTION update_building_companies_updated_at();

DROP TRIGGER IF EXISTS update_ceo_dashboard_configs_updated_at ON ceo_dashboard_configs;
CREATE TRIGGER update_ceo_dashboard_configs_updated_at BEFORE UPDATE ON ceo_dashboard_configs FOR EACH ROW EXECUTE FUNCTION update_building_companies_updated_at();

DROP TRIGGER IF EXISTS update_portfolio_support_requests_updated_at ON portfolio_support_requests;
CREATE TRIGGER update_portfolio_support_requests_updated_at BEFORE UPDATE ON portfolio_support_requests FOR EACH ROW EXECUTE FUNCTION update_building_companies_updated_at();

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

ALTER TABLE portfolio_companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_targets ENABLE ROW LEVEL SECURITY;
ALTER TABLE target_updates ENABLE ROW LEVEL SECURITY;
ALTER TABLE qualification_criteria ENABLE ROW LEVEL SECURITY;
ALTER TABLE ceo_dashboard_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_support_requests ENABLE ROW LEVEL SECURITY;

-- Portfolio companies
CREATE POLICY "DV admins manage portfolio" ON portfolio_companies FOR ALL
    USING (dv_org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member')));

CREATE POLICY "CEOs view own company" ON portfolio_companies FOR SELECT
    USING (organization_id IN (SELECT p.primary_organization_id FROM people p WHERE p.email = auth.email()));

CREATE POLICY "Service role portfolio_companies" ON portfolio_companies FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Portfolio targets
CREATE POLICY "DV admins manage targets" ON portfolio_targets FOR ALL
    USING (portfolio_company_id IN (SELECT id FROM portfolio_companies WHERE dv_org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member'))));

CREATE POLICY "CEOs view own targets" ON portfolio_targets FOR SELECT
    USING (portfolio_company_id IN (SELECT pc.id FROM portfolio_companies pc JOIN people p ON p.primary_organization_id = pc.organization_id WHERE p.email = auth.email()));

CREATE POLICY "CEOs update own targets" ON portfolio_targets FOR UPDATE
    USING (portfolio_company_id IN (SELECT pc.id FROM portfolio_companies pc JOIN people p ON p.primary_organization_id = pc.organization_id WHERE p.email = auth.email()));

CREATE POLICY "Service role portfolio_targets" ON portfolio_targets FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Target updates
CREATE POLICY "View target updates" ON target_updates FOR SELECT
    USING (target_id IN (SELECT id FROM portfolio_targets));

CREATE POLICY "Create target updates" ON target_updates FOR INSERT
    WITH CHECK (target_id IN (SELECT id FROM portfolio_targets));

CREATE POLICY "Service role target_updates" ON target_updates FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Qualification criteria
CREATE POLICY "Org members view criteria" ON qualification_criteria FOR SELECT
    USING (dv_org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid()));

CREATE POLICY "DV admins manage criteria" ON qualification_criteria FOR ALL
    USING (dv_org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));

CREATE POLICY "Service role qualification_criteria" ON qualification_criteria FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- CEO dashboard configs
CREATE POLICY "CEOs manage own dashboard" ON ceo_dashboard_configs FOR ALL
    USING (portfolio_company_id IN (SELECT pc.id FROM portfolio_companies pc JOIN people p ON p.primary_organization_id = pc.organization_id WHERE p.email = auth.email()));

CREATE POLICY "DV admins manage dashboards" ON ceo_dashboard_configs FOR ALL
    USING (portfolio_company_id IN (SELECT id FROM portfolio_companies WHERE dv_org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member'))));

CREATE POLICY "Service role ceo_dashboard_configs" ON ceo_dashboard_configs FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Support requests
CREATE POLICY "CEOs create requests" ON portfolio_support_requests FOR INSERT
    WITH CHECK (portfolio_company_id IN (SELECT pc.id FROM portfolio_companies pc JOIN people p ON p.primary_organization_id = pc.organization_id WHERE p.email = auth.email()));

CREATE POLICY "CEOs view own requests" ON portfolio_support_requests FOR SELECT
    USING (portfolio_company_id IN (SELECT pc.id FROM portfolio_companies pc JOIN people p ON p.primary_organization_id = pc.organization_id WHERE p.email = auth.email()));

CREATE POLICY "DV team manage requests" ON portfolio_support_requests FOR ALL
    USING (portfolio_company_id IN (SELECT id FROM portfolio_companies WHERE dv_org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid())));

CREATE POLICY "Service role portfolio_support_requests" ON portfolio_support_requests FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE portfolio_companies IS 'Portfolio companies with investment details and qualification tracking';
COMMENT ON TABLE portfolio_targets IS 'Targets portfolio companies must achieve for next round qualification';
COMMENT ON TABLE target_updates IS 'Historical record of target value changes';
COMMENT ON TABLE qualification_criteria IS 'Rules defining what companies need to qualify for next round';
COMMENT ON TABLE ceo_dashboard_configs IS 'CEO-facing dashboards per portfolio company';
COMMENT ON TABLE portfolio_support_requests IS 'Support requests from portfolio companies to DV team';
