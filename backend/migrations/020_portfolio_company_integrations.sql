-- ============================================================================
-- MIGRATION 020: PORTFOLIO COMPANY INTEGRATIONS
-- Store API credentials for each portfolio company (Pipedrive, Fortnox, etc.)
-- ============================================================================

-- Portfolio company integrations (encrypted API credentials per company)
CREATE TABLE IF NOT EXISTS portfolio_company_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_company_id UUID NOT NULL REFERENCES portfolio_companies(id) ON DELETE CASCADE,
    
    -- Integration type
    integration_type TEXT NOT NULL, -- 'pipedrive', 'fortnox', 'google_sheets', 'google_workspace', 'office365', 'custom'
    integration_name TEXT, -- For custom integrations
    
    -- API Credentials (encrypted)
    api_token_encrypted TEXT,
    client_id TEXT,
    client_secret_encrypted TEXT,
    refresh_token_encrypted TEXT,
    
    -- Configuration
    api_url TEXT,
    company_domain TEXT,
    additional_config JSONB DEFAULT '{}'::jsonb,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMPTZ,
    last_sync_status TEXT, -- 'success', 'failed', 'pending'
    sync_error TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES people(id),
    
    UNIQUE(portfolio_company_id, integration_type)
);

CREATE INDEX IF NOT EXISTS idx_portfolio_integrations_company ON portfolio_company_integrations(portfolio_company_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_integrations_type ON portfolio_company_integrations(integration_type);
CREATE INDEX IF NOT EXISTS idx_portfolio_integrations_active ON portfolio_company_integrations(is_active);

-- Comments
COMMENT ON TABLE portfolio_company_integrations IS 'Encrypted API credentials for each portfolio company';
COMMENT ON COLUMN portfolio_company_integrations.api_token_encrypted IS 'Encrypted using pgcrypto with ENCRYPTION_KEY';
COMMENT ON COLUMN portfolio_company_integrations.client_secret_encrypted IS 'Encrypted OAuth client secret';
COMMENT ON COLUMN portfolio_company_integrations.refresh_token_encrypted IS 'Encrypted OAuth refresh token';

