-- User-Level Integrations
-- Allows each user to connect their own Linear, Google, Slack accounts
-- No more global .env configuration needed!

-- Create user_integrations table
CREATE TABLE IF NOT EXISTS user_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    
    -- Integration type: 'linear', 'google', 'slack', etc.
    integration_type TEXT NOT NULL,
    
    -- OAuth tokens (will be encrypted in application layer)
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMPTZ,
    
    -- Integration-specific data (team IDs, workspace info, etc.)
    integration_data JSONB DEFAULT '{}'::jsonb,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    connected_at TIMESTAMPTZ DEFAULT NOW(),
    last_used_at TIMESTAMPTZ,
    last_synced_at TIMESTAMPTZ,
    
    -- Error tracking
    last_error TEXT,
    error_count INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id, integration_type)
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_integrations_user_id ON user_integrations(user_id);
CREATE INDEX IF NOT EXISTS idx_user_integrations_org_id ON user_integrations(org_id);
CREATE INDEX IF NOT EXISTS idx_user_integrations_type ON user_integrations(integration_type);
CREATE INDEX IF NOT EXISTS idx_user_integrations_active ON user_integrations(is_active) WHERE is_active = true;

-- Enable RLS
ALTER TABLE user_integrations ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Users can only access their own integrations
CREATE POLICY "Users can view own integrations"
    ON user_integrations FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own integrations"
    ON user_integrations FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own integrations"
    ON user_integrations FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own integrations"
    ON user_integrations FOR DELETE
    USING (auth.uid() = user_id);

-- Service role can access all (for automated tasks)
CREATE POLICY "Service role can access all integrations"
    ON user_integrations FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Org admins can view org members' integrations
CREATE POLICY "Org admins can view org integrations"
    ON user_integrations FOR SELECT
    USING (
        org_id IN (
            SELECT om.org_id 
            FROM org_memberships om 
            WHERE om.user_id = auth.uid() 
            AND om.role IN ('owner', 'admin')
        )
    );

-- Create function to update updated_at
CREATE OR REPLACE FUNCTION update_user_integrations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS update_user_integrations_updated_at ON user_integrations;
CREATE TRIGGER update_user_integrations_updated_at
    BEFORE UPDATE ON user_integrations
    FOR EACH ROW
    EXECUTE FUNCTION update_user_integrations_updated_at();

-- Optional: Org-level integrations (admin configures for whole org)
CREATE TABLE IF NOT EXISTS org_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    
    -- Integration type
    integration_type TEXT NOT NULL,
    
    -- OAuth tokens (encrypted)
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMPTZ,
    
    -- Integration data
    integration_data JSONB DEFAULT '{}'::jsonb,
    
    -- Who configured it
    configured_by UUID REFERENCES auth.users(id),
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    connected_at TIMESTAMPTZ DEFAULT NOW(),
    last_used_at TIMESTAMPTZ,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(org_id, integration_type)
);

-- Enable RLS for org integrations
ALTER TABLE org_integrations ENABLE ROW LEVEL SECURITY;

-- Only org owners/admins can manage org integrations
CREATE POLICY "Org admins can manage org integrations"
    ON org_integrations FOR ALL
    USING (
        org_id IN (
            SELECT om.org_id 
            FROM org_memberships om 
            WHERE om.user_id = auth.uid() 
            AND om.role IN ('owner', 'admin')
        )
    );

-- Service role can access all
CREATE POLICY "Service role can access org integrations"
    ON org_integrations FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_org_integrations_org_id ON org_integrations(org_id);
CREATE INDEX IF NOT EXISTS idx_org_integrations_type ON org_integrations(integration_type);

-- Comments for documentation
COMMENT ON TABLE user_integrations IS 'User-level OAuth integrations for Linear, Google, Slack, etc.';
COMMENT ON COLUMN user_integrations.integration_type IS 'Type of integration: linear, google, slack';
COMMENT ON COLUMN user_integrations.access_token IS 'OAuth access token (encrypted by application)';
COMMENT ON COLUMN user_integrations.integration_data IS 'Integration-specific data like team_id, workspace_id';

COMMENT ON TABLE org_integrations IS 'Organization-level integrations configured by admins for all members';

