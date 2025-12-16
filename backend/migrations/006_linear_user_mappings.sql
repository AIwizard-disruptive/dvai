-- Linear User Mappings
-- Maps meeting attendee names to Linear user IDs
-- Ensures "Marcus's tasks" go to Marcus's Linear account

CREATE TABLE IF NOT EXISTS linear_user_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    
    -- Person identification (from meetings)
    person_name TEXT NOT NULL,
    person_email TEXT,
    
    -- Linear user ID
    linear_user_id TEXT NOT NULL,
    
    -- Additional data
    integration_data JSONB DEFAULT '{}'::jsonb,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_synced_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(org_id, person_email),
    UNIQUE(org_id, person_name, linear_user_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_linear_mappings_org_id ON linear_user_mappings(org_id);
CREATE INDEX IF NOT EXISTS idx_linear_mappings_name ON linear_user_mappings(person_name);
CREATE INDEX IF NOT EXISTS idx_linear_mappings_email ON linear_user_mappings(person_email);
CREATE INDEX IF NOT EXISTS idx_linear_mappings_linear_id ON linear_user_mappings(linear_user_id);

-- Enable RLS
ALTER TABLE linear_user_mappings ENABLE ROW LEVEL SECURITY;

-- Org members can view their org's mappings
CREATE POLICY "Org members can view mappings"
    ON linear_user_mappings FOR SELECT
    USING (
        org_id IN (
            SELECT om.org_id 
            FROM org_memberships om 
            WHERE om.user_id = auth.uid()
        )
    );

-- Org admins can manage mappings
CREATE POLICY "Org admins can manage mappings"
    ON linear_user_mappings FOR ALL
    USING (
        org_id IN (
            SELECT om.org_id 
            FROM org_memberships om 
            WHERE om.user_id = auth.uid() 
            AND om.role IN ('owner', 'admin')
        )
    );

-- Service role can access all
CREATE POLICY "Service role can access mappings"
    ON linear_user_mappings FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_linear_mappings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_linear_mappings_updated_at ON linear_user_mappings;
CREATE TRIGGER update_linear_mappings_updated_at
    BEFORE UPDATE ON linear_user_mappings
    FOR EACH ROW
    EXECUTE FUNCTION update_linear_mappings_updated_at();

-- Comments
COMMENT ON TABLE linear_user_mappings IS 'Maps meeting attendee names to Linear user IDs for proper task assignment';
COMMENT ON COLUMN linear_user_mappings.person_name IS 'Name as it appears in meetings (e.g., Marcus, Fanny)';
COMMENT ON COLUMN linear_user_mappings.person_email IS 'Email for reliable matching';
COMMENT ON COLUMN linear_user_mappings.linear_user_id IS 'Linear user ID from Linear API';

