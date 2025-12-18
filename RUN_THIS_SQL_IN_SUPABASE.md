# Run This SQL in Supabase Dashboard

To enable the portfolio company integrations feature, please run this SQL:

## Steps:

1. Go to: https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/editor

2. Click "New Query"

3. Copy and paste this SQL:

```sql
-- Portfolio company integrations table
CREATE TABLE IF NOT EXISTS portfolio_company_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_company_id UUID NOT NULL REFERENCES portfolio_companies(id) ON DELETE CASCADE,
    
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
    created_by UUID REFERENCES people(id),
    
    UNIQUE(portfolio_company_id, integration_type)
);

CREATE INDEX IF NOT EXISTS idx_portfolio_integrations_company ON portfolio_company_integrations(portfolio_company_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_integrations_type ON portfolio_company_integrations(integration_type);
CREATE INDEX IF NOT EXISTS idx_portfolio_integrations_active ON portfolio_company_integrations(is_active);
```

4. Click "Run"

5. You should see: "Success. No rows returned"

6. Then run: `python add_coeo_pipedrive_to_db.py`

This will enable the Settings page to show "✅ Connected" for Coeo!

