-- ============================================================================
-- MIGRATION 012: ADMIN WHEEL (CLEAN)
-- DV Partner helicopter view, alerts, portfolio health
-- ============================================================================

-- DV partner dashboard configs (NEW)
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

CREATE INDEX IF NOT EXISTS idx_dv_dashboard_configs_user ON dv_dashboard_configs(user_id);

-- Alerts and notifications (NEW)
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
CREATE INDEX IF NOT EXISTS idx_dv_alerts_status ON dv_alerts(status);

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
    SUM(CASE WHEN pt.status = 'behind' THEN 1 ELSE 0 END) as targets_behind,
    AVG(pt.progress_percentage) as avg_progress,
    MAX(pt.last_updated_at) as last_update
FROM portfolio_companies pc
JOIN organizations o ON pc.organization_id = o.id
LEFT JOIN portfolio_targets pt ON pt.portfolio_company_id = pc.id
WHERE pc.status = 'active'
GROUP BY pc.id, pc.organization_id, o.name, pc.investment_stage, pc.qualification_score, pc.qualification_status;

CREATE INDEX IF NOT EXISTS idx_dv_portfolio_health_company ON dv_portfolio_health(portfolio_company_id);

CREATE MATERIALIZED VIEW IF NOT EXISTS dv_dealflow_metrics AS
SELECT
    COUNT(*) as total_leads,
    SUM(CASE WHEN ai_qualification_score >= 70 THEN 1 ELSE 0 END) as qualified_leads,
    SUM(CASE WHEN stage = 'meeting_scheduled' THEN 1 ELSE 0 END) as meetings_scheduled,
    SUM(CASE WHEN stage = 'diligence' THEN 1 ELSE 0 END) as in_diligence,
    SUM(CASE WHEN stage = 'closed_won' THEN 1 ELSE 0 END) as closed_won,
    AVG(ai_qualification_score) as avg_score
FROM dealflow_leads
WHERE created_at >= NOW() - INTERVAL '12 months';

-- ============================================================================
-- TRIGGERS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_admin_wheel_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_dv_dashboard_configs_updated_at ON dv_dashboard_configs;
CREATE TRIGGER update_dv_dashboard_configs_updated_at BEFORE UPDATE ON dv_dashboard_configs FOR EACH ROW EXECUTE FUNCTION update_admin_wheel_updated_at();

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

ALTER TABLE dv_dashboard_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE dv_alerts ENABLE ROW LEVEL SECURITY;

-- Dashboard configs
CREATE POLICY "Users manage own dashboard" ON dv_dashboard_configs FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "Service role dv_dashboard_configs" ON dv_dashboard_configs FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Alerts
CREATE POLICY "Org members view alerts" ON dv_alerts FOR SELECT
    USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid()));

CREATE POLICY "Org members create alerts" ON dv_alerts FOR INSERT
    WITH CHECK (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member')));

CREATE POLICY "Assigned users update alerts" ON dv_alerts FOR UPDATE
    USING (assigned_to IN (SELECT p.id FROM people p JOIN org_memberships om ON om.org_id = p.org_id WHERE om.user_id = auth.uid()) OR org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));

CREATE POLICY "Service role dv_alerts" ON dv_alerts FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

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

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE dv_dashboard_configs IS 'DV partner dashboard preferences and widget configurations';
COMMENT ON TABLE dv_alerts IS 'Alerts and notifications for DV partners across all 4 wheels';
COMMENT ON MATERIALIZED VIEW dv_portfolio_health IS 'Portfolio health metrics for ADMIN dashboard';
COMMENT ON MATERIALIZED VIEW dv_dealflow_metrics IS 'Dealflow pipeline metrics for ADMIN dashboard';
