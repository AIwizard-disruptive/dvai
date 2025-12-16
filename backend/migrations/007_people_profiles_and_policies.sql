-- People Profiles & Policy Documents Extension
-- Expands from meetings to complete organizational knowledge

-- ============================================================================
-- ENHANCE PEOPLE TABLE WITH PROFILES
-- ============================================================================

-- Add profile fields to existing people table
ALTER TABLE people ADD COLUMN IF NOT EXISTS title VARCHAR(100);  -- Job title
ALTER TABLE people ADD COLUMN IF NOT EXISTS department VARCHAR(100);
ALTER TABLE people ADD COLUMN IF NOT EXISTS bio TEXT;  -- Short CV/bio
ALTER TABLE people ADD COLUMN IF NOT EXISTS competences TEXT[];  -- Array of skills
ALTER TABLE people ADD COLUMN IF NOT EXISTS linkedin_url TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS github_url TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS photo_url TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS start_date DATE;
ALTER TABLE people ADD COLUMN IF NOT EXISTS employment_type VARCHAR(50);  -- Full-time, Part-time, Contractor
ALTER TABLE people ADD COLUMN IF NOT EXISTS location VARCHAR(100);
ALTER TABLE people ADD COLUMN IF NOT EXISTS timezone VARCHAR(50);

-- Documents linked to this person (contracts, policies they own, etc.)
CREATE TABLE IF NOT EXISTS person_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    
    -- Document info
    document_type TEXT NOT NULL,  -- 'employment_contract', 'nda', 'policy', 'cv', 'certificate'
    title TEXT NOT NULL,
    google_drive_url TEXT,
    file_path TEXT,
    
    -- Metadata
    uploaded_by UUID REFERENCES auth.users(id),
    valid_from DATE,
    valid_until DATE,
    is_active BOOLEAN DEFAULT true,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_person_documents_person ON person_documents(person_id);
CREATE INDEX IF NOT EXISTS idx_person_documents_type ON person_documents(document_type);

-- ============================================================================
-- POLICY DOCUMENTS (Company-wide)
-- ============================================================================

CREATE TABLE IF NOT EXISTS policy_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    
    -- Policy info
    policy_type TEXT NOT NULL,  -- 'culture', 'hr', 'security', 'gdpr', 'code_of_conduct'
    title TEXT NOT NULL,
    description TEXT,
    google_drive_url TEXT NOT NULL,
    
    -- Ownership
    owner_id UUID REFERENCES people(id),  -- Who owns this policy
    approved_by UUID REFERENCES auth.users(id),
    
    -- Versioning
    version VARCHAR(20),
    effective_date DATE,
    review_date DATE,
    
    -- Status
    status TEXT DEFAULT 'draft',  -- draft, active, archived
    is_required_reading BOOLEAN DEFAULT false,
    
    -- Tags
    tags TEXT[],
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_policy_documents_org ON policy_documents(org_id);
CREATE INDEX IF NOT EXISTS idx_policy_documents_type ON policy_documents(policy_type);
CREATE INDEX IF NOT EXISTS idx_policy_documents_status ON policy_documents(status);

-- Track who has read which policies
CREATE TABLE IF NOT EXISTS policy_acknowledgments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id UUID NOT NULL REFERENCES policy_documents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    person_id UUID REFERENCES people(id),
    
    -- Acknowledgment
    acknowledged_at TIMESTAMPTZ DEFAULT NOW(),
    ip_address INET,
    
    -- Unique constraint
    UNIQUE(policy_id, user_id)
);

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

ALTER TABLE person_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE policy_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE policy_acknowledgments ENABLE ROW LEVEL SECURITY;

-- Person documents: Users can see their own, admins can see all in org
CREATE POLICY "Users can view own person documents"
    ON person_documents FOR SELECT
    USING (
        person_id IN (
            SELECT p.id FROM people p
            JOIN org_memberships om ON om.org_id = p.org_id
            WHERE om.user_id = auth.uid()
        )
    );

CREATE POLICY "Org admins can view all person documents"
    ON person_documents FOR ALL
    USING (
        org_id IN (
            SELECT om.org_id FROM org_memberships om
            WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')
        )
    );

-- Policy documents: All org members can read active policies
CREATE POLICY "Org members can view active policies"
    ON policy_documents FOR SELECT
    USING (
        org_id IN (
            SELECT om.org_id FROM org_memberships om
            WHERE om.user_id = auth.uid()
        )
        AND status = 'active'
    );

CREATE POLICY "Org admins can manage policies"
    ON policy_documents FOR ALL
    USING (
        org_id IN (
            SELECT om.org_id FROM org_memberships om
            WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')
        )
    );

-- Policy acknowledgments: Users can acknowledge and view own
CREATE POLICY "Users can acknowledge policies"
    ON policy_acknowledgments FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own acknowledgments"
    ON policy_acknowledgments FOR SELECT
    USING (auth.uid() = user_id);

-- Service role access
CREATE POLICY "Service role person_documents" ON person_documents FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role policy_documents" ON policy_documents FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role policy_acknowledgments" ON policy_acknowledgments FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE person_documents IS 'Documents linked to people (contracts, CVs, certificates)';
COMMENT ON TABLE policy_documents IS 'Company-wide policy documents (culture, HR, security, etc.)';
COMMENT ON TABLE policy_acknowledgments IS 'Track who has read and acknowledged which policies';

COMMENT ON COLUMN people.competences IS 'Array of skills/competences';
COMMENT ON COLUMN policy_documents.is_required_reading IS 'If true, all org members must acknowledge';

