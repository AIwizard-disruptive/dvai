-- ============================================================================
-- MIGRATION 009: PEOPLE WHEEL (CLEAN - No conflicts)
-- Extends existing tables + adds NEW tables only
-- ============================================================================

-- ============================================================================
-- EXTEND PEOPLE TABLE WITH DOMAIN & EMPLOYMENT INFO
-- ============================================================================

-- Add domain and work email for @disruptiveventures.se employees
ALTER TABLE people ADD COLUMN IF NOT EXISTS work_email TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS email_domain TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS employee_number TEXT;

-- Google Workspace sync
ALTER TABLE people ADD COLUMN IF NOT EXISTS google_workspace_id TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS google_directory_synced_at TIMESTAMPTZ;

-- Note: employment_contract_id will be added AFTER contracts table is created (see below)

-- Create index for work email and domain lookups
CREATE INDEX IF NOT EXISTS idx_people_work_email ON people(work_email);
CREATE INDEX IF NOT EXISTS idx_people_email_domain ON people(email_domain);
CREATE INDEX IF NOT EXISTS idx_people_google_workspace_id ON people(google_workspace_id);

-- Extend existing policy_documents table (from migration 007) with AI fields
ALTER TABLE policy_documents ADD COLUMN IF NOT EXISTS generated_by_ai BOOLEAN DEFAULT false;
ALTER TABLE policy_documents ADD COLUMN IF NOT EXISTS generation_prompt TEXT;
ALTER TABLE policy_documents ADD COLUMN IF NOT EXISTS policy_content TEXT;

-- Extend existing policy_acknowledgments table with tracking fields
ALTER TABLE policy_acknowledgments ADD COLUMN IF NOT EXISTS version_acknowledged TEXT;
ALTER TABLE policy_acknowledgments ADD COLUMN IF NOT EXISTS meeting_id UUID REFERENCES meetings(id);

-- ============================================================================
-- NEW TABLES (don't exist yet)
-- ============================================================================

-- Contracts library (NEW) - Enhanced for employment contracts
CREATE TABLE IF NOT EXISTS contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    contract_type TEXT NOT NULL,  -- 'employment', 'nda', 'investment', 'service_agreement'
    contract_name TEXT,
    template_id UUID REFERENCES contracts(id),
    party_organization_id UUID REFERENCES organizations(id),
    party_person_id UUID REFERENCES people(id),
    start_date DATE,
    end_date DATE,
    value DECIMAL,  -- For employment: annual salary
    currency TEXT DEFAULT 'SEK',
    terms JSONB,  -- For employment: {salary_breakdown, benefits, vacation_days, notice_period, etc.}
    contract_content TEXT,  -- Full contract text (AI-generated or template-based)
    google_doc_id TEXT,  -- Link to Google Docs version
    signed_pdf_url TEXT,  -- Link to signed PDF in storage
    status TEXT DEFAULT 'draft',  -- 'draft', 'sent', 'signed', 'active', 'expired', 'terminated'
    signed_at TIMESTAMPTZ,
    signed_by UUID REFERENCES people(id),
    
    -- Employment-specific fields
    employment_type TEXT,  -- 'full-time', 'part-time', 'contractor', 'consultant'
    probation_end_date DATE,  -- Probation period end
    notice_period_days INTEGER,  -- Notice period in days
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_contracts_org ON contracts(org_id);
CREATE INDEX IF NOT EXISTS idx_contracts_type ON contracts(contract_type);
CREATE INDEX IF NOT EXISTS idx_contracts_status ON contracts(status);
CREATE INDEX IF NOT EXISTS idx_contracts_party_person ON contracts(party_person_id);

-- Check constraint for contract types
ALTER TABLE contracts ADD CONSTRAINT check_contract_type 
    CHECK (contract_type IN ('employment', 'nda', 'investment', 'service_agreement', 'advisory', 'consulting'));

-- NOW add employment contract link to people table (AFTER contracts table exists)
ALTER TABLE people ADD COLUMN IF NOT EXISTS employment_contract_id UUID REFERENCES contracts(id);
ALTER TABLE people ADD COLUMN IF NOT EXISTS contract_start_date DATE;
ALTER TABLE people ADD COLUMN IF NOT EXISTS contract_end_date DATE;

-- Role descriptions (NEW)
CREATE TABLE IF NOT EXISTS role_descriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    role_title TEXT NOT NULL,
    role_level TEXT,
    department TEXT,
    description TEXT,
    responsibilities TEXT[],
    requirements TEXT[],
    nice_to_have TEXT[],
    salary_range_min DECIMAL,
    salary_range_max DECIMAL,
    currency TEXT DEFAULT 'SEK',
    equity_range TEXT,
    is_hiring BOOLEAN DEFAULT false,
    status TEXT DEFAULT 'draft',
    google_doc_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_role_descriptions_org ON role_descriptions(org_id);
CREATE INDEX IF NOT EXISTS idx_role_descriptions_hiring ON role_descriptions(is_hiring) WHERE is_hiring = true;

-- Recruitment pipeline (NEW)
CREATE TABLE IF NOT EXISTS recruitment_candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    role_id UUID REFERENCES role_descriptions(id),
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    linkedin_url TEXT,
    source TEXT,
    referrer_id UUID REFERENCES people(id),
    resume_url TEXT,
    cover_letter TEXT,
    ai_score FLOAT,
    ai_summary TEXT,
    strengths TEXT[],
    concerns TEXT[],
    stage TEXT DEFAULT 'applied',
    stage_changed_at TIMESTAMPTZ DEFAULT NOW(),
    interviews JSONB,
    decision TEXT,
    decision_reason TEXT,
    decision_by UUID REFERENCES people(id),
    decision_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_candidates_org ON recruitment_candidates(org_id);
CREATE INDEX IF NOT EXISTS idx_candidates_email ON recruitment_candidates(email);

-- Recruitment notes (NEW)
CREATE TABLE IF NOT EXISTS recruitment_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES recruitment_candidates(id) ON DELETE CASCADE,
    author_id UUID REFERENCES people(id),
    note_type TEXT,
    note_content TEXT,
    meeting_id UUID REFERENCES meetings(id),
    sentiment TEXT,
    key_points TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_recruitment_notes_candidate ON recruitment_notes(candidate_id);

-- Competencies/Skills (NEW)
CREATE TABLE IF NOT EXISTS person_competencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    skill_name TEXT NOT NULL,
    skill_category TEXT,
    proficiency_level TEXT,
    source TEXT,
    extracted_by_ai BOOLEAN DEFAULT false,
    evidence TEXT[],
    verified_by UUID REFERENCES people(id),
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_competencies_person ON person_competencies(person_id);
CREATE INDEX IF NOT EXISTS idx_competencies_skill ON person_competencies(skill_name);

-- CV storage (NEW) - Enhanced for LinkedIn generation
CREATE TABLE IF NOT EXISTS person_cvs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    
    -- CV file storage
    cv_filename TEXT,
    cv_file_url TEXT,
    google_drive_file_id TEXT,
    
    -- CV content
    cv_text TEXT,
    structured_data JSONB,  -- {experience: [], education: [], skills: [], certifications: []}
    extracted_competencies TEXT[],
    ai_generated_summary TEXT,
    
    -- LinkedIn integration
    generated_from_linkedin BOOLEAN DEFAULT false,
    linkedin_profile_url TEXT,
    linkedin_data_snapshot JSONB,  -- Raw LinkedIn data used to generate CV
    linkedin_scraped_at TIMESTAMPTZ,
    
    -- CV metadata
    cv_language TEXT DEFAULT 'en',
    cv_format TEXT DEFAULT 'standard',  -- 'standard', 'executive', 'technical', 'academic'
    is_primary BOOLEAN DEFAULT true,
    is_public BOOLEAN DEFAULT false,  -- Can this CV be shared publicly?
    
    -- Processing status
    parse_status TEXT DEFAULT 'pending',  -- 'pending', 'processing', 'completed', 'failed'
    generation_status TEXT,  -- 'manual_upload', 'linkedin_generated', 'ai_enhanced'
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cvs_person ON person_cvs(person_id);
CREATE INDEX IF NOT EXISTS idx_cvs_linkedin ON person_cvs(generated_from_linkedin) WHERE generated_from_linkedin = true;

-- Google Workspace profile sync (NEW) - Enhanced for Directory sync
CREATE TABLE IF NOT EXISTS google_profile_syncs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    
    -- Google identifiers
    google_user_id TEXT,  -- Google Workspace user ID
    google_email TEXT,    -- Their @disruptiveventures.se email
    
    -- Sync tracking
    last_sync_at TIMESTAMPTZ,
    sync_status TEXT DEFAULT 'pending',  -- 'pending', 'syncing', 'completed', 'failed'
    sync_error TEXT,
    sync_direction TEXT DEFAULT 'both',  -- 'to_google', 'from_google', 'both'
    
    -- What was synced
    synced_fields JSONB,  -- {name: true, title: true, department: true, phone: true, ...}
    current_profile_data JSONB,  -- Current Google Directory profile data
    previous_profile_data JSONB,  -- Previous state for change tracking
    
    -- Sync configuration
    auto_sync_enabled BOOLEAN DEFAULT true,
    sync_frequency TEXT DEFAULT 'daily',  -- 'realtime', 'hourly', 'daily', 'manual'
    fields_to_sync TEXT[],  -- ['name', 'title', 'department', 'phone', 'bio', 'photo']
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(person_id)
);

CREATE INDEX IF NOT EXISTS idx_google_syncs_person ON google_profile_syncs(person_id);
CREATE INDEX IF NOT EXISTS idx_google_syncs_google_user ON google_profile_syncs(google_user_id);
CREATE INDEX IF NOT EXISTS idx_google_syncs_status ON google_profile_syncs(sync_status);

-- Google Contacts sync (NEW)
CREATE TABLE IF NOT EXISTS google_contacts_syncs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    google_resource_name TEXT,
    google_contact_groups TEXT[],
    last_sync_at TIMESTAMPTZ,
    sync_status TEXT,
    sync_error TEXT,
    synced_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(entity_type, entity_id)
);

CREATE INDEX IF NOT EXISTS idx_google_contacts_syncs_entity ON google_contacts_syncs(entity_type, entity_id);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_people_wheel_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_contracts_updated_at ON contracts;
CREATE TRIGGER update_contracts_updated_at BEFORE UPDATE ON contracts FOR EACH ROW EXECUTE FUNCTION update_people_wheel_updated_at();

DROP TRIGGER IF EXISTS update_role_descriptions_updated_at ON role_descriptions;
CREATE TRIGGER update_role_descriptions_updated_at BEFORE UPDATE ON role_descriptions FOR EACH ROW EXECUTE FUNCTION update_people_wheel_updated_at();

DROP TRIGGER IF EXISTS update_recruitment_candidates_updated_at ON recruitment_candidates;
CREATE TRIGGER update_recruitment_candidates_updated_at BEFORE UPDATE ON recruitment_candidates FOR EACH ROW EXECUTE FUNCTION update_people_wheel_updated_at();

DROP TRIGGER IF EXISTS update_person_competencies_updated_at ON person_competencies;
CREATE TRIGGER update_person_competencies_updated_at BEFORE UPDATE ON person_competencies FOR EACH ROW EXECUTE FUNCTION update_people_wheel_updated_at();

DROP TRIGGER IF EXISTS update_person_cvs_updated_at ON person_cvs;
CREATE TRIGGER update_person_cvs_updated_at BEFORE UPDATE ON person_cvs FOR EACH ROW EXECUTE FUNCTION update_people_wheel_updated_at();

DROP TRIGGER IF EXISTS update_google_profile_syncs_updated_at ON google_profile_syncs;
CREATE TRIGGER update_google_profile_syncs_updated_at BEFORE UPDATE ON google_profile_syncs FOR EACH ROW EXECUTE FUNCTION update_people_wheel_updated_at();

DROP TRIGGER IF EXISTS update_google_contacts_syncs_updated_at ON google_contacts_syncs;
CREATE TRIGGER update_google_contacts_syncs_updated_at BEFORE UPDATE ON google_contacts_syncs FOR EACH ROW EXECUTE FUNCTION update_people_wheel_updated_at();

-- ============================================================================
-- RLS POLICIES (only for NEW tables)
-- ============================================================================

-- Enable RLS
ALTER TABLE contracts ENABLE ROW LEVEL SECURITY;
ALTER TABLE role_descriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE recruitment_candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE recruitment_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE person_competencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE person_cvs ENABLE ROW LEVEL SECURITY;
ALTER TABLE google_profile_syncs ENABLE ROW LEVEL SECURITY;
ALTER TABLE google_contacts_syncs ENABLE ROW LEVEL SECURITY;

-- Contracts
CREATE POLICY "Org admins can manage contracts" ON contracts FOR ALL
    USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));

CREATE POLICY "Contract parties can view" ON contracts FOR SELECT
    USING (party_person_id IN (SELECT p.id FROM people p JOIN org_memberships om ON om.org_id = p.org_id WHERE om.user_id = auth.uid()));

CREATE POLICY "Service role contracts" ON contracts FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Role descriptions
CREATE POLICY "Org members view active roles" ON role_descriptions FOR SELECT
    USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid()) AND status = 'active');

CREATE POLICY "Org admins manage roles" ON role_descriptions FOR ALL
    USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));

CREATE POLICY "Service role role_descriptions" ON role_descriptions FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Recruitment candidates
CREATE POLICY "Org admins manage candidates" ON recruitment_candidates FOR ALL
    USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));

CREATE POLICY "Service role recruitment_candidates" ON recruitment_candidates FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Recruitment notes
CREATE POLICY "Org admins manage notes" ON recruitment_notes FOR ALL
    USING (candidate_id IN (SELECT rc.id FROM recruitment_candidates rc JOIN org_memberships om ON om.org_id = rc.org_id WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));

CREATE POLICY "Service role recruitment_notes" ON recruitment_notes FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Person competencies
CREATE POLICY "Users view own competencies" ON person_competencies FOR SELECT
    USING (person_id IN (SELECT p.id FROM people p JOIN org_memberships om ON om.org_id = p.org_id WHERE om.user_id = auth.uid()));

CREATE POLICY "Org admins manage competencies" ON person_competencies FOR ALL
    USING (person_id IN (SELECT p.id FROM people p JOIN org_memberships om ON om.org_id = p.org_id WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));

CREATE POLICY "Service role person_competencies" ON person_competencies FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Person CVs
CREATE POLICY "Users view own cvs" ON person_cvs FOR SELECT
    USING (person_id IN (SELECT p.id FROM people p JOIN org_memberships om ON om.org_id = p.org_id WHERE om.user_id = auth.uid()));

CREATE POLICY "Org admins manage cvs" ON person_cvs FOR ALL
    USING (person_id IN (SELECT p.id FROM people p JOIN org_memberships om ON om.org_id = p.org_id WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));

CREATE POLICY "Service role person_cvs" ON person_cvs FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Google profile syncs
CREATE POLICY "Org admins manage profile syncs" ON google_profile_syncs FOR ALL
    USING (person_id IN (SELECT p.id FROM people p JOIN org_memberships om ON om.org_id = p.org_id WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));

CREATE POLICY "Service role google_profile_syncs" ON google_profile_syncs FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Google contacts syncs
CREATE POLICY "Org admins manage contacts syncs" ON google_contacts_syncs FOR ALL
    USING (EXISTS (SELECT 1 FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));

CREATE POLICY "Service role google_contacts_syncs" ON google_contacts_syncs FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- ============================================================================
-- HELPER FUNCTIONS FOR DV EMPLOYEE MANAGEMENT
-- ============================================================================

-- Auto-populate email domain from work_email
CREATE OR REPLACE FUNCTION populate_email_domain()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.work_email IS NOT NULL AND NEW.work_email != '' THEN
        NEW.email_domain = SPLIT_PART(NEW.work_email, '@', 2);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_populate_email_domain ON people;
CREATE TRIGGER trigger_populate_email_domain
    BEFORE INSERT OR UPDATE OF work_email ON people
    FOR EACH ROW
    EXECUTE FUNCTION populate_email_domain();

-- Function to update person from LinkedIn data
CREATE OR REPLACE FUNCTION update_person_from_linkedin(
    p_person_id UUID,
    p_linkedin_data JSONB
)
RETURNS void AS $$
BEGIN
    UPDATE people
    SET
        bio = COALESCE(p_linkedin_data->>'summary', bio),
        job_title = COALESCE(p_linkedin_data->>'headline', job_title),
        photo_url = COALESCE(p_linkedin_data->>'profilePicture', photo_url),
        location = COALESCE(p_linkedin_data->>'location', location),
        updated_at = NOW()
    WHERE id = p_person_id;
    
    -- Store extracted competencies from LinkedIn
    IF p_linkedin_data ? 'skills' THEN
        INSERT INTO person_competencies (person_id, skill_name, skill_category, source, extracted_by_ai)
        SELECT 
            p_person_id,
            skill->>'name',
            'linkedin',
            'linkedin_api',
            true
        FROM jsonb_array_elements(p_linkedin_data->'skills') AS skill
        ON CONFLICT DO NOTHING;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to sync person to Google Workspace Directory
CREATE OR REPLACE FUNCTION sync_person_to_google_directory(
    p_person_id UUID
)
RETURNS JSONB AS $$
DECLARE
    person_record RECORD;
    sync_payload JSONB;
BEGIN
    SELECT * INTO person_record
    FROM people
    WHERE id = p_person_id;
    
    IF NOT FOUND THEN
        RETURN jsonb_build_object('error', 'Person not found');
    END IF;
    
    -- Build Google Directory API payload
    sync_payload = jsonb_build_object(
        'name', jsonb_build_object(
            'fullName', person_record.name,
            'familyName', SPLIT_PART(person_record.name, ' ', 2),
            'givenName', SPLIT_PART(person_record.name, ' ', 1)
        ),
        'primaryEmail', person_record.work_email,
        'organizations', jsonb_build_array(
            jsonb_build_object(
                'title', person_record.job_title,
                'department', person_record.department,
                'primary', true
            )
        ),
        'phones', jsonb_build_array(
            jsonb_build_object(
                'value', person_record.phone,
                'type', 'work'
            )
        ),
        'locations', jsonb_build_array(
            jsonb_build_object(
                'area', person_record.location,
                'type', 'desk'
            )
        )
    );
    
    -- Update sync timestamp
    UPDATE people
    SET google_directory_synced_at = NOW()
    WHERE id = p_person_id;
    
    RETURN sync_payload;
END;
$$ LANGUAGE plpgsql;

-- Function to link person to employment contract
CREATE OR REPLACE FUNCTION link_person_to_contract(
    p_person_id UUID,
    p_contract_id UUID
)
RETURNS void AS $$
DECLARE
    contract_record RECORD;
BEGIN
    SELECT start_date, end_date INTO contract_record
    FROM contracts
    WHERE id = p_contract_id AND contract_type = 'employment';
    
    IF FOUND THEN
        UPDATE people
        SET
            employment_contract_id = p_contract_id,
            contract_start_date = contract_record.start_date,
            contract_end_date = contract_record.end_date,
            updated_at = NOW()
        WHERE id = p_person_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to generate CV from LinkedIn profile
CREATE OR REPLACE FUNCTION generate_cv_from_linkedin(
    p_person_id UUID,
    p_linkedin_data JSONB,
    p_cv_format TEXT DEFAULT 'standard'
)
RETURNS UUID AS $$
DECLARE
    cv_id UUID;
    person_record RECORD;
BEGIN
    -- Get person info
    SELECT * INTO person_record
    FROM people
    WHERE id = p_person_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Person not found';
    END IF;
    
    -- Create CV record from LinkedIn data
    INSERT INTO person_cvs (
        person_id,
        generated_from_linkedin,
        linkedin_profile_url,
        linkedin_data_snapshot,
        linkedin_scraped_at,
        structured_data,
        extracted_competencies,
        ai_generated_summary,
        cv_format,
        parse_status,
        generation_status,
        is_primary
    )
    VALUES (
        p_person_id,
        true,
        person_record.linkedin_url,
        p_linkedin_data,
        NOW(),
        jsonb_build_object(
            'name', person_record.name,
            'email', person_record.work_email,
            'phone', person_record.phone,
            'title', COALESCE(p_linkedin_data->>'headline', person_record.job_title),
            'summary', p_linkedin_data->>'summary',
            'experience', p_linkedin_data->'positions',
            'education', p_linkedin_data->'education',
            'skills', p_linkedin_data->'skills',
            'certifications', p_linkedin_data->'certifications',
            'languages', p_linkedin_data->'languages'
        ),
        ARRAY(SELECT jsonb_array_elements_text(p_linkedin_data->'skills')),
        p_linkedin_data->>'summary',
        p_cv_format,
        'completed',
        'linkedin_generated',
        true
    )
    RETURNING id INTO cv_id;
    
    -- Update person profile with LinkedIn data
    PERFORM update_person_from_linkedin(p_person_id, p_linkedin_data);
    
    RETURN cv_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- UPDATE EXISTING DV EMPLOYEES WITH DOMAIN
-- ============================================================================

-- Update email_domain for existing employees with @disruptiveventures.se
UPDATE people
SET 
    email_domain = 'disruptiveventures.se',
    work_email = COALESCE(work_email, email)
WHERE 
    email LIKE '%@disruptiveventures.se'
    OR work_email LIKE '%@disruptiveventures.se';

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE contracts IS 'Contracts library (employment, NDA, investment) with AI generation';
COMMENT ON TABLE role_descriptions IS 'Job role descriptions with AI generation for recruitment';
COMMENT ON TABLE recruitment_candidates IS 'Recruitment pipeline with AI screening';
COMMENT ON TABLE recruitment_notes IS 'Interview notes with AI extraction';
COMMENT ON TABLE person_competencies IS 'Skills and competencies for Google Workspace Directory sync';
COMMENT ON TABLE person_cvs IS 'CV storage and AI parsing for competency extraction';
COMMENT ON TABLE google_profile_syncs IS 'Sync tracking for Google Workspace Directory profiles';
COMMENT ON TABLE google_contacts_syncs IS 'Sync tracking for Google Contacts CRM integration';

COMMENT ON COLUMN people.work_email IS 'Work email (e.g., name@disruptiveventures.se)';
COMMENT ON COLUMN people.email_domain IS 'Auto-extracted domain from work_email';
COMMENT ON COLUMN people.employment_contract_id IS 'Link to employment contract in contracts table';
COMMENT ON COLUMN people.google_workspace_id IS 'Google Workspace Directory user ID';
COMMENT ON COLUMN people.employee_number IS 'Internal employee ID number';
COMMENT ON COLUMN people.contract_start_date IS 'Employment contract start date (synced from contract)';
COMMENT ON COLUMN people.contract_end_date IS 'Employment contract end date (if fixed-term)';

COMMENT ON COLUMN contracts.employment_type IS 'For employment contracts: full-time, part-time, contractor, consultant';
COMMENT ON COLUMN contracts.terms IS 'Contract terms as JSON: salary_breakdown, benefits, vacation_days, notice_period, etc.';

COMMENT ON COLUMN person_cvs.generated_from_linkedin IS 'True if CV was auto-generated from LinkedIn profile';
COMMENT ON COLUMN person_cvs.linkedin_data_snapshot IS 'Raw LinkedIn profile data used for CV generation';

COMMENT ON COLUMN google_profile_syncs.fields_to_sync IS 'Which fields to sync to Google Workspace Directory';
COMMENT ON COLUMN google_profile_syncs.auto_sync_enabled IS 'Enable automatic syncing to Google Directory';

COMMENT ON FUNCTION update_person_from_linkedin IS 'Updates person profile with data extracted from LinkedIn API/scraping';
COMMENT ON FUNCTION sync_person_to_google_directory IS 'Generates Google Directory API payload for syncing employee profile';
COMMENT ON FUNCTION link_person_to_contract IS 'Links person to their employment contract';
COMMENT ON FUNCTION generate_cv_from_linkedin IS 'Creates CV record from LinkedIn profile data and updates person profile';
-- ============================================================================
-- MIGRATION 010: DEALFLOW WHEEL (CLEAN)
-- Lead qualification, research, outreach automation
-- ============================================================================

-- Inbound leads (NEW)
CREATE TABLE IF NOT EXISTS dealflow_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    company_name TEXT NOT NULL,
    website TEXT,
    domain TEXT,
    founder_name TEXT,
    founder_email TEXT,
    founder_linkedin TEXT,
    source TEXT,
    source_details TEXT,
    referrer_id UUID REFERENCES people(id),
    pitch_deck_url TEXT,
    one_liner TEXT,
    company_stage TEXT,
    ai_qualification_score FLOAT,
    ai_qualification_reason TEXT,
    meets_thesis BOOLEAN,
    thesis_match_reason TEXT,
    research_status TEXT DEFAULT 'pending',
    research_completed_at TIMESTAMPTZ,
    stage TEXT DEFAULT 'new',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dealflow_leads_org ON dealflow_leads(org_id);
CREATE INDEX IF NOT EXISTS idx_dealflow_leads_stage ON dealflow_leads(stage);
CREATE INDEX IF NOT EXISTS idx_dealflow_leads_score ON dealflow_leads(ai_qualification_score);

-- AI-generated research (NEW)
CREATE TABLE IF NOT EXISTS dealflow_research (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL REFERENCES dealflow_leads(id) ON DELETE CASCADE,
    market_size TEXT,
    market_trends TEXT[],
    competitors TEXT[],
    competitive_advantages TEXT[],
    product_analysis TEXT,
    business_model_analysis TEXT,
    traction_metrics JSONB,
    founder_backgrounds TEXT[],
    team_strengths TEXT[],
    team_gaps TEXT[],
    investment_opportunity TEXT,
    key_risks TEXT[],
    suggested_questions TEXT[],
    sources_used TEXT[],
    generated_by TEXT,
    generation_time_ms INTEGER,
    google_doc_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dealflow_research_lead ON dealflow_research(lead_id);

-- Market analysis cache (NEW)
CREATE TABLE IF NOT EXISTS market_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    market_name TEXT NOT NULL,
    market_category TEXT,
    market_size_tam TEXT,
    market_size_sam TEXT,
    growth_rate TEXT,
    key_trends TEXT[],
    key_players TEXT[],
    investment_attractiveness TEXT,
    key_risks TEXT[],
    sources TEXT[],
    last_updated TIMESTAMPTZ,
    google_doc_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_market_analyses_org ON market_analyses(org_id);
CREATE INDEX IF NOT EXISTS idx_market_analyses_name ON market_analyses(market_name);

-- Automated outreach (NEW)
CREATE TABLE IF NOT EXISTS dealflow_outreach (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL REFERENCES dealflow_leads(id) ON DELETE CASCADE,
    campaign_type TEXT,
    subject TEXT,
    body TEXT,
    sent_at TIMESTAMPTZ,
    sent_via TEXT,
    opened_at TIMESTAMPTZ,
    replied_at TIMESTAMPTZ,
    reply_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dealflow_outreach_lead ON dealflow_outreach(lead_id);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_dealflow_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_dealflow_leads_updated_at ON dealflow_leads;
CREATE TRIGGER update_dealflow_leads_updated_at BEFORE UPDATE ON dealflow_leads FOR EACH ROW EXECUTE FUNCTION update_dealflow_updated_at();

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

ALTER TABLE dealflow_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE dealflow_research ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE dealflow_outreach ENABLE ROW LEVEL SECURITY;

-- Dealflow leads
CREATE POLICY "Org members view leads" ON dealflow_leads FOR SELECT
    USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid()));

CREATE POLICY "Org members manage leads" ON dealflow_leads FOR ALL
    USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member')));

CREATE POLICY "Service role dealflow_leads" ON dealflow_leads FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Dealflow research
CREATE POLICY "Org members view research" ON dealflow_research FOR SELECT
    USING (lead_id IN (SELECT id FROM dealflow_leads WHERE org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid())));

CREATE POLICY "Org members manage research" ON dealflow_research FOR ALL
    USING (lead_id IN (SELECT id FROM dealflow_leads WHERE org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member'))));

CREATE POLICY "Service role dealflow_research" ON dealflow_research FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Market analyses
CREATE POLICY "Org members view market" ON market_analyses FOR SELECT
    USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid()));

CREATE POLICY "Org members manage market" ON market_analyses FOR ALL
    USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member')));

CREATE POLICY "Service role market_analyses" ON market_analyses FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Dealflow outreach
CREATE POLICY "Org members view outreach" ON dealflow_outreach FOR SELECT
    USING (lead_id IN (SELECT id FROM dealflow_leads WHERE org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid())));

CREATE POLICY "Org members manage outreach" ON dealflow_outreach FOR ALL
    USING (lead_id IN (SELECT id FROM dealflow_leads WHERE org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member'))));

CREATE POLICY "Service role dealflow_outreach" ON dealflow_outreach FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE dealflow_leads IS 'Inbound leads with AI qualification and pipeline tracking';
COMMENT ON TABLE dealflow_research IS 'AI-generated research reports for qualified leads';
COMMENT ON TABLE market_analyses IS 'Reusable market analysis cache across leads';
COMMENT ON TABLE dealflow_outreach IS 'Automated outreach campaigns with tracking';
-- ============================================================================
-- MIGRATION 011: BUILDING COMPANIES WHEEL (CLEAN)
-- Portfolio support, target tracking, CEO dashboards, qualification
-- ============================================================================

-- Portfolio companies (NEW)
CREATE TABLE IF NOT EXISTS portfolio_companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    dv_org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    investment_date DATE,
    investment_amount DECIMAL,
    investment_stage TEXT,
    current_valuation DECIMAL,
    ownership_percentage FLOAT,
    lead_partner_id UUID REFERENCES people(id),
    board_seat BOOLEAN DEFAULT false,
    target_stage TEXT,
    target_date DATE,
    target_valuation DECIMAL,
    qualification_score FLOAT,
    qualification_status TEXT,
    last_qualification_check TIMESTAMPTZ,
    ceo_dashboard_enabled BOOLEAN DEFAULT true,
    dashboard_url TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organization_id)
);

CREATE INDEX IF NOT EXISTS idx_portfolio_companies_dv_org ON portfolio_companies(dv_org_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_companies_status ON portfolio_companies(status);

-- Portfolio targets (NEW)
CREATE TABLE IF NOT EXISTS portfolio_targets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_company_id UUID NOT NULL REFERENCES portfolio_companies(id) ON DELETE CASCADE,
    target_category TEXT NOT NULL,
    target_name TEXT NOT NULL,
    target_description TEXT,
    metric_name TEXT,
    target_value DECIMAL,
    current_value DECIMAL,
    unit TEXT,
    deadline DATE,
    is_critical BOOLEAN DEFAULT false,
    progress_percentage FLOAT,
    status TEXT,
    last_updated_at TIMESTAMPTZ,
    last_updated_by UUID REFERENCES people(id),
    update_frequency TEXT DEFAULT 'weekly',
    ai_prediction TEXT,
    ai_recommendations TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_portfolio_targets_company ON portfolio_targets(portfolio_company_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_targets_status ON portfolio_targets(status);

-- Target updates (NEW)
CREATE TABLE IF NOT EXISTS target_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_id UUID NOT NULL REFERENCES portfolio_targets(id) ON DELETE CASCADE,
    new_value DECIMAL,
    previous_value DECIMAL,
    change DECIMAL,
    change_percentage FLOAT,
    update_note TEXT,
    updated_by UUID REFERENCES people(id),
    update_source TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_target_updates_target ON target_updates(target_id);

-- Qualification criteria (NEW)
CREATE TABLE IF NOT EXISTS qualification_criteria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dv_org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    stage TEXT NOT NULL,
    criteria_name TEXT NOT NULL,
    criteria_category TEXT,
    requirement_type TEXT,
    minimum_value DECIMAL,
    target_value DECIMAL,
    weight FLOAT,
    is_mandatory BOOLEAN DEFAULT false,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_qualification_criteria_org ON qualification_criteria(dv_org_id);

-- CEO dashboard configs (NEW)
CREATE TABLE IF NOT EXISTS ceo_dashboard_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_company_id UUID NOT NULL REFERENCES portfolio_companies(id) ON DELETE CASCADE,
    visible_sections TEXT[],
    custom_metrics JSONB,
    can_update_targets BOOLEAN DEFAULT true,
    can_request_support BOOLEAN DEFAULT true,
    can_view_dv_notes BOOLEAN DEFAULT false,
    logo_url TEXT,
    theme_color TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(portfolio_company_id)
);

-- Support requests (NEW)
CREATE TABLE IF NOT EXISTS portfolio_support_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_company_id UUID NOT NULL REFERENCES portfolio_companies(id) ON DELETE CASCADE,
    requested_by UUID REFERENCES people(id),
    request_type TEXT,
    subject TEXT NOT NULL,
    description TEXT,
    urgency TEXT DEFAULT 'normal',
    assigned_to UUID REFERENCES people(id),
    status TEXT DEFAULT 'new',
    response TEXT,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_support_requests_company ON portfolio_support_requests(portfolio_company_id);
CREATE INDEX IF NOT EXISTS idx_support_requests_status ON portfolio_support_requests(status);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_building_companies_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_portfolio_companies_updated_at ON portfolio_companies;
CREATE TRIGGER update_portfolio_companies_updated_at BEFORE UPDATE ON portfolio_companies FOR EACH ROW EXECUTE FUNCTION update_building_companies_updated_at();

DROP TRIGGER IF EXISTS update_portfolio_targets_updated_at ON portfolio_targets;
CREATE TRIGGER update_portfolio_targets_updated_at BEFORE UPDATE ON portfolio_targets FOR EACH ROW EXECUTE FUNCTION update_building_companies_updated_at();

DROP TRIGGER IF EXISTS update_ceo_dashboard_configs_updated_at ON ceo_dashboard_configs;
CREATE TRIGGER update_ceo_dashboard_configs_updated_at BEFORE UPDATE ON ceo_dashboard_configs FOR EACH ROW EXECUTE FUNCTION update_building_companies_updated_at();

DROP TRIGGER IF EXISTS update_portfolio_support_requests_updated_at ON portfolio_support_requests;
CREATE TRIGGER update_portfolio_support_requests_updated_at BEFORE UPDATE ON portfolio_support_requests FOR EACH ROW EXECUTE FUNCTION update_building_companies_updated_at();

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

ALTER TABLE portfolio_companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_targets ENABLE ROW LEVEL SECURITY;
ALTER TABLE target_updates ENABLE ROW LEVEL SECURITY;
ALTER TABLE qualification_criteria ENABLE ROW LEVEL SECURITY;
ALTER TABLE ceo_dashboard_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_support_requests ENABLE ROW LEVEL SECURITY;

-- Portfolio companies
CREATE POLICY "DV admins manage portfolio" ON portfolio_companies FOR ALL
    USING (dv_org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member')));

CREATE POLICY "CEOs view own company" ON portfolio_companies FOR SELECT
    USING (organization_id IN (SELECT p.primary_organization_id FROM people p WHERE p.email = auth.email()));

CREATE POLICY "Service role portfolio_companies" ON portfolio_companies FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Portfolio targets
CREATE POLICY "DV admins manage targets" ON portfolio_targets FOR ALL
    USING (portfolio_company_id IN (SELECT id FROM portfolio_companies WHERE dv_org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member'))));

CREATE POLICY "CEOs view own targets" ON portfolio_targets FOR SELECT
    USING (portfolio_company_id IN (SELECT pc.id FROM portfolio_companies pc JOIN people p ON p.primary_organization_id = pc.organization_id WHERE p.email = auth.email()));

CREATE POLICY "CEOs update own targets" ON portfolio_targets FOR UPDATE
    USING (portfolio_company_id IN (SELECT pc.id FROM portfolio_companies pc JOIN people p ON p.primary_organization_id = pc.organization_id WHERE p.email = auth.email()));

CREATE POLICY "Service role portfolio_targets" ON portfolio_targets FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Target updates
CREATE POLICY "View target updates" ON target_updates FOR SELECT
    USING (target_id IN (SELECT id FROM portfolio_targets));

CREATE POLICY "Create target updates" ON target_updates FOR INSERT
    WITH CHECK (target_id IN (SELECT id FROM portfolio_targets));

CREATE POLICY "Service role target_updates" ON target_updates FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Qualification criteria
CREATE POLICY "Org members view criteria" ON qualification_criteria FOR SELECT
    USING (dv_org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid()));

CREATE POLICY "DV admins manage criteria" ON qualification_criteria FOR ALL
    USING (dv_org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));

CREATE POLICY "Service role qualification_criteria" ON qualification_criteria FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- CEO dashboard configs
CREATE POLICY "CEOs manage own dashboard" ON ceo_dashboard_configs FOR ALL
    USING (portfolio_company_id IN (SELECT pc.id FROM portfolio_companies pc JOIN people p ON p.primary_organization_id = pc.organization_id WHERE p.email = auth.email()));

CREATE POLICY "DV admins manage dashboards" ON ceo_dashboard_configs FOR ALL
    USING (portfolio_company_id IN (SELECT id FROM portfolio_companies WHERE dv_org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin', 'member'))));

CREATE POLICY "Service role ceo_dashboard_configs" ON ceo_dashboard_configs FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Support requests
CREATE POLICY "CEOs create requests" ON portfolio_support_requests FOR INSERT
    WITH CHECK (portfolio_company_id IN (SELECT pc.id FROM portfolio_companies pc JOIN people p ON p.primary_organization_id = pc.organization_id WHERE p.email = auth.email()));

CREATE POLICY "CEOs view own requests" ON portfolio_support_requests FOR SELECT
    USING (portfolio_company_id IN (SELECT pc.id FROM portfolio_companies pc JOIN people p ON p.primary_organization_id = pc.organization_id WHERE p.email = auth.email()));

CREATE POLICY "DV team manage requests" ON portfolio_support_requests FOR ALL
    USING (portfolio_company_id IN (SELECT id FROM portfolio_companies WHERE dv_org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid())));

CREATE POLICY "Service role portfolio_support_requests" ON portfolio_support_requests FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE portfolio_companies IS 'Portfolio companies with investment details and qualification tracking';
COMMENT ON TABLE portfolio_targets IS 'Targets portfolio companies must achieve for next round qualification';
COMMENT ON TABLE target_updates IS 'Historical record of target value changes';
COMMENT ON TABLE qualification_criteria IS 'Rules defining what companies need to qualify for next round';
COMMENT ON TABLE ceo_dashboard_configs IS 'CEO-facing dashboards per portfolio company';
COMMENT ON TABLE portfolio_support_requests IS 'Support requests from portfolio companies to DV team';
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
