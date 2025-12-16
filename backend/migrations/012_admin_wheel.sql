-- ============================================================================
-- MIGRATION 012: ADMIN WHEEL
-- DV Partner helicopter view, alerts, portfolio health
-- ============================================================================

-- DV partner dashboard configurations
CREATE TABLE IF NOT EXISTS dv_dashboard_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    
    -- Dashboard preferences
    visible_wheels TEXT[], -- ['people', 'dealflow', 'building', 'admin']
    default_view TEXT, -- 'overview', 'portfolio', 'pipeline'
    
    -- Widgets configuration
    widgets JSONB, -- Array of widget configs
    
    -- Filters
    saved_filters JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id, org_id)
);

CREATE INDEX IF NOT EXISTS idx_dv_dashboard_configs_user ON dv_dashboard_configs(user_id);
CREATE INDEX IF NOT EXISTS idx_dv_dashboard_configs_org ON dv_dashboard_configs(org_id);

-- Alerts and notifications
CREATE TABLE IF NOT EXISTS dv_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    
    -- Alert details
    alert_type TEXT NOT NULL, -- 'target_at_risk', 'high_score_lead', 'candidate_ready', 'support_request'
    severity TEXT DEFAULT 'info', -- 'info', 'warning', 'critical'
    title TEXT NOT NULL,
    description TEXT,
    
    -- Context
    related_entity_type TEXT, -- 'portfolio_company', 'lead', 'candidate', etc.
    related_entity_id UUID,
    
    -- Routing
    assigned_to UUID REFERENCES people(id),
    
    -- Status
    status TEXT DEFAULT 'new', -- 'new', 'acknowledged', 'resolved', 'dismissed'
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    
    -- Actions
    suggested_actions TEXT[],
    action_taken TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dv_alerts_org ON dv_alerts(org_id);
CREATE INDEX IF NOT EXISTS idx_dv_alerts_type ON dv_alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_dv_alerts_severity ON dv_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_dv_alerts_status ON dv_alerts(status);
CREATE INDEX IF NOT EXISTS idx_dv_alerts_assigned ON dv_alerts(assigned_to);
CREATE INDEX IF NOT EXISTS idx_dv_alerts_entity ON dv_alerts(related_entity_type, related_entity_id);

-- Materialized views for performance
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
    SUM(CASE WHEN pt.status = 'behind' THEN 1 ELSE 0 END) as targets_behind,
    AVG(pt.progress_percentage) as avg_progress,
    MAX(pt.last_updated_at) as last_update
FROM portfolio_companies pc
JOIN organizations o ON pc.organization_id = o.id
LEFT JOIN portfolio_targets pt ON pt.portfolio_company_id = pc.id
WHERE pc.status = 'active'
GROUP BY pc.id, pc.organization_id, o.name, pc.investment_stage, pc.qualification_score, pc.qualification_status;

CREATE INDEX IF NOT EXISTS idx_dv_portfolio_health_company ON dv_portfolio_health(portfolio_company_id);
CREATE INDEX IF NOT EXISTS idx_dv_portfolio_health_status ON dv_portfolio_health(qualification_status);

CREATE MATERIALIZED VIEW IF NOT EXISTS dv_dealflow_metrics AS
SELECT
    COUNT(*) as total_leads,
    SUM(CASE WHEN ai_qualification_score >= 70 THEN 1 ELSE 0 END) as qualified_leads,
    SUM(CASE WHEN stage = 'meeting_scheduled' THEN 1 ELSE 0 END) as meetings_scheduled,
    SUM(CASE WHEN stage = 'diligence' THEN 1 ELSE 0 END) as in_diligence,
    SUM(CASE WHEN stage = 'closed_won' THEN 1 ELSE 0 END) as closed_won,
    AVG(ai_qualification_score) as avg_score,
    COUNT(DISTINCT DATE_TRUNC('month', created_at)) as months_active
FROM dealflow_leads
WHERE created_at >= NOW() - INTERVAL '12 months';

-- Refresh functions for materialized views
CREATE OR REPLACE FUNCTION refresh_dv_portfolio_health()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY dv_portfolio_health;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION refresh_dv_dealflow_metrics()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY dv_dealflow_metrics;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_admin_wheel_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_dv_dashboard_configs_updated_at
    BEFORE UPDATE ON dv_dashboard_configs
    FOR EACH ROW
    EXECUTE FUNCTION update_admin_wheel_updated_at();

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE dv_dashboard_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE dv_alerts ENABLE ROW LEVEL SECURITY;

-- DV Dashboard Configs: Users can manage their own
CREATE POLICY "Users can manage own dashboard config"
    ON dv_dashboard_configs FOR ALL
    USING (auth.uid() = user_id);

-- DV Alerts: Org members can view, assigned users can update
CREATE POLICY "Org members can view dv alerts"
    ON dv_alerts FOR SELECT
    USING (
        org_id IN (
            SELECT om.org_id FROM org_memberships om
            WHERE om.user_id = auth.uid()
        )
    );

CREATE POLICY "Org admins can create dv alerts"
    ON dv_alerts FOR INSERT
    WITH CHECK (
        org_id IN (
            SELECT om.org_id FROM org_memberships om
            WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member')
        )
    );

CREATE POLICY "Assigned users can update dv alerts"
    ON dv_alerts FOR UPDATE
    USING (
        assigned_to IN (
            SELECT p.id FROM people p
            JOIN org_memberships om ON om.org_id = p.org_id
            WHERE om.user_id = auth.uid()
        )
        OR
        org_id IN (
            SELECT om.org_id FROM org_memberships om
            WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')
        )
    );

-- Service role access (for automated tasks)
CREATE POLICY "Service role dv_dashboard_configs" ON dv_dashboard_configs FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role dv_alerts" ON dv_alerts FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE dv_dashboard_configs IS 'DV partner dashboard preferences and widget configurations';
COMMENT ON TABLE dv_alerts IS 'Alerts and notifications for DV partners across all 4 wheels';
COMMENT ON MATERIALIZED VIEW dv_portfolio_health IS 'Portfolio health metrics for ADMIN dashboard';
COMMENT ON MATERIALIZED VIEW dv_dealflow_metrics IS 'Dealflow pipeline metrics for ADMIN dashboard';
