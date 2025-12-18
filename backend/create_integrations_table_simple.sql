-- Simple version - Create portfolio_company_integrations table
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/editor

CREATE TABLE IF NOT EXISTS portfolio_company_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_company_id UUID NOT NULL,
    integration_type TEXT NOT NULL,
    integration_name TEXT,
    api_token_encrypted TEXT,
    client_id TEXT,
    client_secret_encrypted TEXT,
    refresh_token_encrypted TEXT,
    api_url TEXT,
    company_domain TEXT,
    additional_config JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMPTZ,
    last_sync_status TEXT,
    sync_error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID,
    UNIQUE(portfolio_company_id, integration_type)
);

CREATE INDEX IF NOT EXISTS idx_portfolio_integrations_company ON portfolio_company_integrations(portfolio_company_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_integrations_type ON portfolio_company_integrations(integration_type);

