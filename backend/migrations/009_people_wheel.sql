-- ============================================================================
-- MIGRATION 009: PEOPLE WHEEL
-- HR Policies, Contracts, Role Descriptions, Recruitment, Competencies
-- ============================================================================

-- Extend existing policy_documents table with AI fields (from migration 007)
-- Note: policy_documents table already exists from migration 007
ALTER TABLE policy_documents ADD COLUMN IF NOT EXISTS generated_by_ai BOOLEAN DEFAULT false;
ALTER TABLE policy_documents ADD COLUMN IF NOT EXISTS generation_prompt TEXT;
ALTER TABLE policy_documents ADD COLUMN IF NOT EXISTS policy_content TEXT;  -- Full text for AI generation

-- Contracts library
CREATE TABLE IF NOT EXISTS contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    
    -- Contract details
    contract_type TEXT NOT NULL, -- 'employment', 'contractor', 'nda', 'investment'
    contract_name TEXT,
    template_id UUID REFERENCES contracts(id), -- If based on template
    
    -- Parties
    party_organization_id UUID REFERENCES organizations(id),
    party_person_id UUID REFERENCES people(id),
    
    -- Terms
    start_date DATE,
    end_date DATE,
    value DECIMAL,
    currency TEXT DEFAULT 'SEK',
    terms JSONB, -- Structured terms (salary, equity, etc.)
    
    -- Content (AI-generated from template + terms)
    contract_content TEXT, -- Full contract text
    
    -- Storage
    google_doc_id TEXT,
    signed_pdf_url TEXT,
    
    -- Status
    status TEXT DEFAULT 'draft', -- 'draft', 'pending_signature', 'signed', 'terminated'
    signed_at TIMESTAMPTZ,
    signed_by UUID REFERENCES people(id),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_contracts_org ON contracts(org_id);
CREATE INDEX IF NOT EXISTS idx_contracts_type ON contracts(contract_type);
CREATE INDEX IF NOT EXISTS idx_contracts_status ON contracts(status);
CREATE INDEX IF NOT EXISTS idx_contracts_party_person ON contracts(party_person_id);
CREATE INDEX IF NOT EXISTS idx_contracts_party_org ON contracts(party_organization_id);

-- Role descriptions
CREATE TABLE IF NOT EXISTS role_descriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    
    -- Role details
    role_title TEXT NOT NULL,
    role_level TEXT, -- 'junior', 'mid', 'senior', 'lead', 'director'
    department TEXT,
    
    -- Description (AI-generated)
    description TEXT,
    responsibilities TEXT[], -- Array of bullet points
    requirements TEXT[], -- Required skills/experience
    nice_to_have TEXT[], -- Preferred skills
    
    -- Compensation
    salary_range_min DECIMAL,
    salary_range_max DECIMAL,
    currency TEXT DEFAULT 'SEK',
    equity_range TEXT, -- e.g., "0.1%-0.5%"
    
    -- Status
    is_hiring BOOLEAN DEFAULT false,
    status TEXT DEFAULT 'draft', -- 'draft', 'active', 'filled', 'archived'
    
    -- Storage
    google_doc_id TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_role_descriptions_org ON role_descriptions(org_id);
CREATE INDEX IF NOT EXISTS idx_role_descriptions_hiring ON role_descriptions(is_hiring) WHERE is_hiring = true;
CREATE INDEX IF NOT EXISTS idx_role_descriptions_status ON role_descriptions(status);

-- Recruitment pipeline
CREATE TABLE IF NOT EXISTS recruitment_candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    role_id UUID REFERENCES role_descriptions(id),
    
    -- Candidate info
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    linkedin_url TEXT,
    
    -- Application
    source TEXT, -- 'linkedin', 'referral', 'website', 'email'
    referrer_id UUID REFERENCES people(id),
    resume_url TEXT,
    cover_letter TEXT,
    
    -- AI assessment
    ai_score FLOAT, -- 0-100 fit score
    ai_summary TEXT, -- AI-generated candidate summary
    strengths TEXT[],
    concerns TEXT[],
    
    -- Pipeline stage
    stage TEXT DEFAULT 'applied', -- 'applied', 'screening', 'interview', 'offer', 'hired', 'rejected'
    stage_changed_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Interview tracking
    interviews JSONB, -- Array of interview records
    
    -- Decision
    decision TEXT, -- 'hired', 'rejected', 'pending'
    decision_reason TEXT,
    decision_by UUID REFERENCES people(id),
    decision_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_candidates_org ON recruitment_candidates(org_id);
CREATE INDEX IF NOT EXISTS idx_candidates_role ON recruitment_candidates(role_id);
CREATE INDEX IF NOT EXISTS idx_candidates_stage ON recruitment_candidates(stage);
CREATE INDEX IF NOT EXISTS idx_candidates_email ON recruitment_candidates(email);

-- Candidate notes (from interviews)
CREATE TABLE IF NOT EXISTS recruitment_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES recruitment_candidates(id) ON DELETE CASCADE,
    author_id UUID REFERENCES people(id),
    
    -- Note content
    note_type TEXT, -- 'interview', 'reference_check', 'general'
    note_content TEXT,
    
    -- If from meeting (reuse existing meeting intelligence)
    meeting_id UUID REFERENCES meetings(id),
    
    -- AI extracted insights
    sentiment TEXT, -- 'positive', 'neutral', 'negative'
    key_points TEXT[],
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_recruitment_notes_candidate ON recruitment_notes(candidate_id);
CREATE INDEX IF NOT EXISTS idx_recruitment_notes_author ON recruitment_notes(author_id);

-- Competencies/Skills tracking
CREATE TABLE IF NOT EXISTS person_competencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    
    -- Competency details
    skill_name TEXT NOT NULL,
    skill_category TEXT, -- 'technical', 'business', 'language', 'domain'
    proficiency_level TEXT, -- 'beginner', 'intermediate', 'advanced', 'expert'
    
    -- Source of competency
    source TEXT, -- 'cv_extracted', 'self_reported', 'verified', 'inferred'
    extracted_by_ai BOOLEAN DEFAULT false,
    
    -- Evidence
    evidence TEXT[], -- Projects, roles, certifications
    
    -- Verification
    verified_by UUID REFERENCES people(id),
    verified_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_competencies_person ON person_competencies(person_id);
CREATE INDEX IF NOT EXISTS idx_competencies_skill ON person_competencies(skill_name);
CREATE INDEX IF NOT EXISTS idx_competencies_category ON person_competencies(skill_category);

-- CV storage and parsing
CREATE TABLE IF NOT EXISTS person_cvs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    
    -- Storage
    cv_filename TEXT,
    cv_file_url TEXT, -- Supabase Storage or Google Drive
    google_drive_file_id TEXT,
    
    -- Parsed content (AI extracted)
    cv_text TEXT,
    structured_data JSONB, -- {education: [], experience: [], skills: []}
    
    -- AI extraction
    extracted_competencies TEXT[], -- Skills found in CV
    ai_generated_summary TEXT, -- 2-3 sentence professional summary
    
    -- Status
    is_primary BOOLEAN DEFAULT true,
    parse_status TEXT DEFAULT 'pending', -- 'pending', 'parsed', 'failed'
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cvs_person ON person_cvs(person_id);
CREATE INDEX IF NOT EXISTS idx_cvs_primary ON person_cvs(person_id, is_primary) WHERE is_primary = true;

-- Google Workspace profile sync tracking
CREATE TABLE IF NOT EXISTS google_profile_syncs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    
    -- Google identity
    google_user_id TEXT, -- Google Workspace user ID
    google_email TEXT,
    
    -- Sync status
    last_sync_at TIMESTAMPTZ,
    sync_status TEXT, -- 'success', 'failed', 'pending'
    sync_error TEXT,
    
    -- What was synced
    synced_fields JSONB, -- {bio: true, skills: true, cv_link: true}
    
    -- Profile data snapshot
    current_profile_data JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(person_id)
);

CREATE INDEX IF NOT EXISTS idx_google_syncs_person ON google_profile_syncs(person_id);
CREATE INDEX IF NOT EXISTS idx_google_syncs_status ON google_profile_syncs(sync_status);

-- Note: policy_acknowledgments table already exists from migration 007
-- Extend it with additional fields for tracking
ALTER TABLE policy_acknowledgments ADD COLUMN IF NOT EXISTS version_acknowledged TEXT;
ALTER TABLE policy_acknowledgments ADD COLUMN IF NOT EXISTS meeting_id UUID REFERENCES meetings(id);

-- Google Contacts sync tracking (for all contacts)
CREATE TABLE IF NOT EXISTS google_contacts_syncs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL, -- 'person', 'lead', 'portfolio_company'
    entity_id UUID NOT NULL,
    
    -- Google Contacts
    google_resource_name TEXT, -- people/c12345...
    google_contact_groups TEXT[], -- Resource names of groups
    
    -- Sync status
    last_sync_at TIMESTAMPTZ,
    sync_status TEXT, -- 'success', 'failed'
    sync_error TEXT,
    
    -- Snapshot
    synced_data JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(entity_type, entity_id)
);

CREATE INDEX IF NOT EXISTS idx_google_contacts_syncs_entity ON google_contacts_syncs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_google_contacts_syncs_status ON google_contacts_syncs(sync_status);

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_people_wheel_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_hr_policies_updated_at
    BEFORE UPDATE ON hr_policies
    FOR EACH ROW
    EXECUTE FUNCTION update_people_wheel_updated_at();

CREATE TRIGGER update_contracts_updated_at
    BEFORE UPDATE ON contracts
    FOR EACH ROW
    EXECUTE FUNCTION update_people_wheel_updated_at();

CREATE TRIGGER update_role_descriptions_updated_at
    BEFORE UPDATE ON role_descriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_people_wheel_updated_at();

CREATE TRIGGER update_recruitment_candidates_updated_at
    BEFORE UPDATE ON recruitment_candidates
    FOR EACH ROW
    EXECUTE FUNCTION update_people_wheel_updated_at();

CREATE TRIGGER update_person_competencies_updated_at
    BEFORE UPDATE ON person_competencies
    FOR EACH ROW
    EXECUTE FUNCTION update_people_wheel_updated_at();

CREATE TRIGGER update_person_cvs_updated_at
    BEFORE UPDATE ON person_cvs
    FOR EACH ROW
    EXECUTE FUNCTION update_people_wheel_updated_at();

CREATE TRIGGER update_google_profile_syncs_updated_at
    BEFORE UPDATE ON google_profile_syncs
    FOR EACH ROW
    EXECUTE FUNCTION update_people_wheel_updated_at();

CREATE TRIGGER update_google_contacts_syncs_updated_at
    BEFORE UPDATE ON google_contacts_syncs
    FOR EACH ROW
    EXECUTE FUNCTION update_people_wheel_updated_at();

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE hr_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE contracts ENABLE ROW LEVEL SECURITY;
ALTER TABLE role_descriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE recruitment_candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE recruitment_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE person_competencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE person_cvs ENABLE ROW LEVEL SECURITY;
ALTER TABLE google_profile_syncs ENABLE ROW LEVEL SECURITY;
ALTER TABLE policy_acknowledgments ENABLE ROW LEVEL SECURITY;
ALTER TABLE google_contacts_syncs ENABLE ROW LEVEL SECURITY;

-- HR Policies: All org members can read active policies, admins can manage
CREATE POLICY "Org members can view active hr policies"
    ON hr_policies FOR SELECT
    USING (
        org_id IN (
            SELECT om.org_id FROM org_memberships om
            WHERE om.user_id = auth.uid()
        )
        AND status = 'active'
    );

CREATE POLICY "Org admins can manage hr policies"
    ON hr_policies FOR ALL
    USING (
        org_id IN (
            SELECT om.org_id FROM org_memberships om
            WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')
        )
    );

-- Contracts: Admins can manage, involved parties can view
CREATE POLICY "Org admins can manage contracts"
    ON contracts FOR ALL
    USING (
        org_id IN (
            SELECT om.org_id FROM org_memberships om
            WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')
        )
    );

CREATE POLICY "Contract parties can view their contracts"
    ON contracts FOR SELECT
    USING (
        party_person_id IN (
            SELECT p.id FROM people p
            JOIN org_memberships om ON om.org_id = p.org_id
            WHERE om.user_id = auth.uid()
        )
    );

-- Role Descriptions: All org members can view active roles
CREATE POLICY "Org members can view active roles"
    ON role_descriptions FOR SELECT
    USING (
        org_id IN (
            SELECT om.org_id FROM org_memberships om
            WHERE om.user_id = auth.uid()
        )
        AND status = 'active'
    );

CREATE POLICY "Org admins can manage roles"
    ON role_descriptions FOR ALL
    USING (
        org_id IN (
            SELECT om.org_id FROM org_memberships om
            WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')
        )
    );

-- Recruitment Candidates: Only admins can access
CREATE POLICY "Org admins can manage candidates"
    ON recruitment_candidates FOR ALL
    USING (
        org_id IN (
            SELECT om.org_id FROM org_memberships om
            WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')
        )
    );

-- Recruitment Notes: Authors can view own, admins can view all
CREATE POLICY "Authors can view own recruitment notes"
    ON recruitment_notes FOR SELECT
    USING (
        author_id IN (
            SELECT p.id FROM people p
            JOIN org_memberships om ON om.org_id = p.org_id
            WHERE om.user_id = auth.uid()
        )
    );

CREATE POLICY "Org admins can manage recruitment notes"
    ON recruitment_notes FOR ALL
    USING (
        candidate_id IN (
            SELECT rc.id FROM recruitment_candidates rc
            JOIN org_memberships om ON om.org_id = rc.org_id
            WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')
        )
    );

-- Person Competencies: Users can view their own, admins can manage all
CREATE POLICY "Users can view own competencies"
    ON person_competencies FOR SELECT
    USING (
        person_id IN (
            SELECT p.id FROM people p
            JOIN org_memberships om ON om.org_id = p.org_id
            WHERE om.user_id = auth.uid()
        )
    );

CREATE POLICY "Org admins can manage competencies"
    ON person_competencies FOR ALL
    USING (
        person_id IN (
            SELECT p.id FROM people p
            JOIN org_memberships om ON om.org_id = p.org_id
            WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')
        )
    );

-- Person CVs: Users can view their own, admins can view all
CREATE POLICY "Users can view own cvs"
    ON person_cvs FOR SELECT
    USING (
        person_id IN (
            SELECT p.id FROM people p
            JOIN org_memberships om ON om.org_id = p.org_id
            WHERE om.user_id = auth.uid()
        )
    );

CREATE POLICY "Org admins can manage cvs"
    ON person_cvs FOR ALL
    USING (
        person_id IN (
            SELECT p.id FROM people p
            JOIN org_memberships om ON om.org_id = p.org_id
            WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')
        )
    );

-- Google Profile Syncs: Admins only
CREATE POLICY "Org admins can manage profile syncs"
    ON google_profile_syncs FOR ALL
    USING (
        person_id IN (
            SELECT p.id FROM people p
            JOIN org_memberships om ON om.org_id = p.org_id
            WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')
        )
    );

-- Policy Acknowledgments: Users can acknowledge and view own
CREATE POLICY "Users can acknowledge hr policies"
    ON policy_acknowledgments FOR INSERT
    WITH CHECK (
        person_id IN (
            SELECT p.id FROM people p
            JOIN org_memberships om ON om.org_id = p.org_id
            WHERE om.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can view own policy acknowledgments"
    ON policy_acknowledgments FOR SELECT
    USING (
        person_id IN (
            SELECT p.id FROM people p
            JOIN org_memberships om ON om.org_id = p.org_id
            WHERE om.user_id = auth.uid()
        )
    );

-- Google Contacts Syncs: Admins only
CREATE POLICY "Org admins can manage contacts syncs"
    ON google_contacts_syncs FOR ALL
    USING (
        -- This table tracks syncs for people, leads, and portfolio companies
        -- Admins of the org can manage all syncs
        EXISTS (
            SELECT 1 FROM org_memberships om
            WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')
        )
    );

-- Service role access (for automated tasks)
CREATE POLICY "Service role hr_policies" ON hr_policies FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role contracts" ON contracts FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role role_descriptions" ON role_descriptions FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role recruitment_candidates" ON recruitment_candidates FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role recruitment_notes" ON recruitment_notes FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role person_competencies" ON person_competencies FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role person_cvs" ON person_cvs FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role google_profile_syncs" ON google_profile_syncs FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role policy_acknowledgments" ON policy_acknowledgments FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role google_contacts_syncs" ON google_contacts_syncs FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE hr_policies IS 'HR policies library with AI generation and Google Docs storage';
COMMENT ON TABLE contracts IS 'Contracts library (employment, NDA, investment) with AI generation';
COMMENT ON TABLE role_descriptions IS 'Job role descriptions with AI generation for recruitment';
COMMENT ON TABLE recruitment_candidates IS 'Recruitment pipeline with AI screening';
COMMENT ON TABLE recruitment_notes IS 'Interview notes and feedback with AI extraction';
COMMENT ON TABLE person_competencies IS 'Skills and competencies per person for searchability';
COMMENT ON TABLE person_cvs IS 'CV storage and AI parsing for competency extraction';
COMMENT ON TABLE google_profile_syncs IS 'Sync tracking for Google Workspace Directory profiles';
COMMENT ON TABLE policy_acknowledgments IS 'Track which policies each person has read';
COMMENT ON TABLE google_contacts_syncs IS 'Sync tracking for Google Contacts CRM integration';
