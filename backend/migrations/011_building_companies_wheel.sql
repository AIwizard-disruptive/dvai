-- ============================================================================
-- MIGRATION 011: BUILDING COMPANIES WHEEL
-- Portfolio support, target tracking, CEO dashboards, next-round qualification
-- ============================================================================

-- Portfolio companies (extends existing organizations)
CREATE TABLE IF NOT EXISTS portfolio_companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    dv_org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    
    -- Investment details
    investment_date DATE,
    investment_amount DECIMAL,
    investment_stage TEXT, -- 'seed', 'series-a', 'series-b'
    current_valuation DECIMAL,
    ownership_percentage FLOAT,
    
    -- Relationship
    lead_partner_id UUID REFERENCES people(id),
    board_seat BOOLEAN DEFAULT false,
    
    -- Next round targets
    target_stage TEXT, -- 'series-a', 'series-b', etc.
    target_date DATE,
    target_valuation DECIMAL,
    
    -- Qualification for next round
    qualification_score FLOAT, -- 0-100, auto-calculated
    qualification_status TEXT, -- 'green', 'yellow', 'red'
    last_qualification_check TIMESTAMPTZ,
    
    -- CEO dashboard access
    ceo_dashboard_enabled BOOLEAN DEFAULT true,
    dashboard_url TEXT, -- Unique URL for CEO
    
    -- Status
    status TEXT DEFAULT 'active', -- 'active', 'exited', 'shut_down'
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(organization_id)
);

CREATE INDEX IF NOT EXISTS idx_portfolio_companies_dv_org ON portfolio_companies(dv_org_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_companies_lead_partner ON portfolio_companies(lead_partner_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_companies_status ON portfolio_companies(status);
CREATE INDEX IF NOT EXISTS idx_portfolio_companies_qualification ON portfolio_companies(qualification_status);

-- Target definitions (what company needs to achieve for next round)
CREATE TABLE IF NOT EXISTS portfolio_targets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_company_id UUID NOT NULL REFERENCES portfolio_companies(id) ON DELETE CASCADE,
    
    -- Target details
    target_category TEXT NOT NULL, -- 'revenue', 'growth', 'product', 'team', 'operational'
    target_name TEXT NOT NULL,
    target_description TEXT,
    
    -- Target values
    metric_name TEXT, -- 'MRR', 'churn', 'NPS', etc.
    target_value DECIMAL,
    current_value DECIMAL,
    unit TEXT, -- 'SEK', '%', 'count', etc.
    
    -- Timeline
    deadline DATE,
    is_critical BOOLEAN DEFAULT false, -- Must hit this to qualify
    
    -- Progress tracking
    progress_percentage FLOAT, -- Auto-calculated
    status TEXT, -- 'on_track', 'at_risk', 'behind', 'achieved'
    
    -- Updates (from CEO or auto-synced)
    last_updated_at TIMESTAMPTZ,
    last_updated_by UUID REFERENCES people(id),
    update_frequency TEXT DEFAULT 'weekly', -- How often to update
    
    -- AI insights
    ai_prediction TEXT, -- GPT prediction if target will be met
    ai_recommendations TEXT[], -- Suggestions to get back on track
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_portfolio_targets_company ON portfolio_targets(portfolio_company_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_targets_status ON portfolio_targets(status);
CREATE INDEX IF NOT EXISTS idx_portfolio_targets_critical ON portfolio_targets(is_critical) WHERE is_critical = true;
CREATE INDEX IF NOT EXISTS idx_portfolio_targets_deadline ON portfolio_targets(deadline);

-- Target updates (history)
CREATE TABLE IF NOT EXISTS target_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_id UUID NOT NULL REFERENCES portfolio_targets(id) ON DELETE CASCADE,
    
    -- Update data
    new_value DECIMAL,
    previous_value DECIMAL,
    change DECIMAL,
    change_percentage FLOAT,
    
    -- Context
    update_note TEXT,
    updated_by UUID REFERENCES people(id),
    update_source TEXT, -- 'manual', 'automated', 'integrated_system'
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_target_updates_target ON target_updates(target_id);
CREATE INDEX IF NOT EXISTS idx_target_updates_created ON target_updates(created_at);

-- Qualification criteria (rules for next round)
CREATE TABLE IF NOT EXISTS qualification_criteria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dv_org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    
    -- Criteria definition
    stage TEXT NOT NULL, -- 'seed_to_series_a', 'series_a_to_b', etc.
    criteria_name TEXT NOT NULL,
    criteria_category TEXT, -- 'revenue', 'growth', 'product', 'team'
    
    -- Requirements
    requirement_type TEXT, -- 'minimum', 'range', 'boolean'
    minimum_value DECIMAL,
    target_value DECIMAL,
    weight FLOAT, -- Importance weight (0-1)
    
    -- Evaluation
    is_mandatory BOOLEAN DEFAULT false,
    
    description TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_qualification_criteria_org ON qualification_criteria(dv_org_id);
CREATE INDEX IF NOT EXISTS idx_qualification_criteria_stage ON qualification_criteria(stage);

-- CEO dashboard configuration
CREATE TABLE IF NOT EXISTS ceo_dashboard_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_company_id UUID NOT NULL REFERENCES portfolio_companies(id) ON DELETE CASCADE,
    
    -- Dashboard settings
    visible_sections TEXT[], -- ['targets', 'metrics', 'support_requests']
    custom_metrics JSONB, -- CEO can define custom metrics
    
    -- Permissions
    can_update_targets BOOLEAN DEFAULT true,
    can_request_support BOOLEAN DEFAULT true,
    can_view_dv_notes BOOLEAN DEFAULT false,
    
    -- Branding
    logo_url TEXT,
    theme_color TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(portfolio_company_id)
);

CREATE INDEX IF NOT EXISTS idx_ceo_dashboard_configs_company ON ceo_dashboard_configs(portfolio_company_id);

-- Support requests from portfolio companies
CREATE TABLE IF NOT EXISTS portfolio_support_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_company_id UUID NOT NULL REFERENCES portfolio_companies(id) ON DELETE CASCADE,
    requested_by UUID REFERENCES people(id),
    
    -- Request details
    request_type TEXT, -- 'advice', 'intro', 'hiring', 'fundraising', 'technical'
    subject TEXT NOT NULL,
    description TEXT,
    urgency TEXT DEFAULT 'normal', -- 'low', 'normal', 'high', 'critical'
    
    -- Routing
    assigned_to UUID REFERENCES people(id), -- DV team member
    status TEXT DEFAULT 'new', -- 'new', 'in_progress', 'resolved', 'closed'
    
    -- Resolution
    response TEXT,
    resolved_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_support_requests_company ON portfolio_support_requests(portfolio_company_id);
CREATE INDEX IF NOT EXISTS idx_support_requests_status ON portfolio_support_requests(status);
CREATE INDEX IF NOT EXISTS idx_support_requests_assigned ON portfolio_support_requests(assigned_to);
CREATE INDEX IF NOT EXISTS idx_support_requests_urgency ON portfolio_support_requests(urgency);

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_building_companies_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_portfolio_companies_updated_at
    BEFORE UPDATE ON portfolio_companies
    FOR EACH ROW
    EXECUTE FUNCTION update_building_companies_updated_at();

CREATE TRIGGER update_portfolio_targets_updated_at
    BEFORE UPDATE ON portfolio_targets
    FOR EACH ROW
    EXECUTE FUNCTION update_building_companies_updated_at();

CREATE TRIGGER update_ceo_dashboard_configs_updated_at
    BEFORE UPDATE ON ceo_dashboard_configs
    FOR EACH ROW
    EXECUTE FUNCTION update_building_companies_updated_at();

CREATE TRIGGER update_portfolio_support_requests_updated_at
    BEFORE UPDATE ON portfolio_support_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_building_companies_updated_at();

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE portfolio_companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_targets ENABLE ROW LEVEL SECURITY;
ALTER TABLE target_updates ENABLE ROW LEVEL SECURITY;
ALTER TABLE qualification_criteria ENABLE ROW LEVEL SECURITY;
ALTER TABLE ceo_dashboard_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_support_requests ENABLE ROW LEVEL SECURITY;

-- Portfolio Companies: DV admins can manage all, CEOs can view their own
CREATE POLICY "DV admins can manage portfolio companies"
    ON portfolio_companies FOR ALL
    USING (
        dv_org_id IN (
            SELECT om.org_id FROM org_memberships om
            WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member')
        )
    );

CREATE POLICY "CEOs can view own portfolio company"
    ON portfolio_companies FOR SELECT
    USING (
        organization_id IN (
            SELECT p.primary_organization_id FROM people p
            WHERE p.email = auth.email()
        )
    );

-- Portfolio Targets: DV admins can manage, CEOs can view and update their own
CREATE POLICY "DV admins can manage portfolio targets"
    ON portfolio_targets FOR ALL
    USING (
        portfolio_company_id IN (
            SELECT id FROM portfolio_companies
            WHERE dv_org_id IN (
                SELECT om.org_id FROM org_memberships om
                WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member')
            )
        )
    );

CREATE POLICY "CEOs can view own targets"
    ON portfolio_targets FOR SELECT
    USING (
        portfolio_company_id IN (
            SELECT pc.id FROM portfolio_companies pc
            JOIN people p ON p.primary_organization_id = pc.organization_id
            WHERE p.email = auth.email()
        )
    );

CREATE POLICY "CEOs can update own targets"
    ON portfolio_targets FOR UPDATE
    USING (
        portfolio_company_id IN (
            SELECT pc.id FROM portfolio_companies pc
            JOIN people p ON p.primary_organization_id = pc.organization_id
            WHERE p.email = auth.email()
        )
    );

-- Target Updates: Follow target permissions
CREATE POLICY "Users can view target updates for accessible targets"
    ON target_updates FOR SELECT
    USING (
        target_id IN (
            SELECT id FROM portfolio_targets
            -- Inherit permissions from portfolio_targets
        )
    );

CREATE POLICY "Users can create target updates for accessible targets"
    ON target_updates FOR INSERT
    WITH CHECK (
        target_id IN (
            SELECT id FROM portfolio_targets
            -- Inherit permissions from portfolio_targets
        )
    );

-- Qualification Criteria: DV admins can manage, all can view
CREATE POLICY "Org members can view qualification criteria"
    ON qualification_criteria FOR SELECT
    USING (
        dv_org_id IN (
            SELECT om.org_id FROM org_memberships om
            WHERE om.user_id = auth.uid()
        )
    );

CREATE POLICY "DV admins can manage qualification criteria"
    ON qualification_criteria FOR ALL
    USING (
        dv_org_id IN (
            SELECT om.org_id FROM org_memberships om
            WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')
        )
    );

-- CEO Dashboard Configs: CEOs can view/update their own, DV admins can manage all
CREATE POLICY "CEOs can manage own dashboard config"
    ON ceo_dashboard_configs FOR ALL
    USING (
        portfolio_company_id IN (
            SELECT pc.id FROM portfolio_companies pc
            JOIN people p ON p.primary_organization_id = pc.organization_id
            WHERE p.email = auth.email()
        )
    );

CREATE POLICY "DV admins can manage dashboard configs"
    ON ceo_dashboard_configs FOR ALL
    USING (
        portfolio_company_id IN (
            SELECT id FROM portfolio_companies
            WHERE dv_org_id IN (
                SELECT om.org_id FROM org_memberships om
                WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member')
            )
        )
    );

-- Portfolio Support Requests: CEOs can create and view their own, DV team can manage all
CREATE POLICY "CEOs can create support requests"
    ON portfolio_support_requests FOR INSERT
    WITH CHECK (
        portfolio_company_id IN (
            SELECT pc.id FROM portfolio_companies pc
            JOIN people p ON p.primary_organization_id = pc.organization_id
            WHERE p.email = auth.email()
        )
    );

CREATE POLICY "CEOs can view own support requests"
    ON portfolio_support_requests FOR SELECT
    USING (
        portfolio_company_id IN (
            SELECT pc.id FROM portfolio_companies pc
            JOIN people p ON p.primary_organization_id = pc.organization_id
            WHERE p.email = auth.email()
        )
    );

CREATE POLICY "DV team can manage all support requests"
    ON portfolio_support_requests FOR ALL
    USING (
        portfolio_company_id IN (
            SELECT id FROM portfolio_companies
            WHERE dv_org_id IN (
                SELECT om.org_id FROM org_memberships om
                WHERE om.user_id = auth.uid()
            )
        )
    );

-- Service role access (for automated tasks)
CREATE POLICY "Service role portfolio_companies" ON portfolio_companies FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role portfolio_targets" ON portfolio_targets FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role target_updates" ON target_updates FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role qualification_criteria" ON qualification_criteria FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role ceo_dashboard_configs" ON ceo_dashboard_configs FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role portfolio_support_requests" ON portfolio_support_requests FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE portfolio_companies IS 'Portfolio companies with investment details and qualification tracking';
COMMENT ON TABLE portfolio_targets IS 'Targets portfolio companies must achieve for next round qualification';
COMMENT ON TABLE target_updates IS 'Historical record of target value changes';
COMMENT ON TABLE qualification_criteria IS 'Rules defining what companies need to qualify for next round';
COMMENT ON TABLE ceo_dashboard_configs IS 'Configuration for CEO-facing dashboards per portfolio company';
COMMENT ON TABLE portfolio_support_requests IS 'Support requests from portfolio companies to DV team';
