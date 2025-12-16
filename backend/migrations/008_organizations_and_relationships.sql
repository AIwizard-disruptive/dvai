-- Organizations & Relationships (HubSpot-style)
-- Separate companies from people, link them with relationships

-- ============================================================================
-- ORGANIZATIONS TABLE (Companies, Clients, Partners)
-- ============================================================================

CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,  -- Which DV org manages this
    
    -- Basic info
    name TEXT NOT NULL,
    website_url TEXT,
    domain TEXT,  -- Extract from website (e.g., "google.com")
    
    -- Visual
    logo_url TEXT,  -- Scraped from website or uploaded
    favicon_url TEXT,  -- Scraped from website
    
    -- Classification
    organization_type TEXT NOT NULL,  -- 'client', 'partner', 'portfolio', 'vendor', 'competitor'
    industry TEXT,
    size TEXT,  -- 'startup', 'scale-up', 'enterprise'
    
    -- Contact info
    primary_email TEXT,
    phone TEXT,
    address TEXT,
    city TEXT,
    country TEXT,
    
    -- Business info
    description TEXT,
    founded_year INTEGER,
    employee_count INTEGER,
    revenue_range TEXT,
    
    -- Social/Online
    linkedin_url TEXT,
    twitter_url TEXT,
    crunchbase_url TEXT,
    
    -- Relationship status
    relationship_status TEXT DEFAULT 'prospect',  -- prospect, active, churned, archived
    relationship_owner_id UUID REFERENCES people(id),  -- Who owns this relationship at DV
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_contact_date DATE,
    
    UNIQUE(org_id, domain)
);

CREATE INDEX IF NOT EXISTS idx_organizations_org_id ON organizations(org_id);
CREATE INDEX IF NOT EXISTS idx_organizations_type ON organizations(organization_type);
CREATE INDEX IF NOT EXISTS idx_organizations_status ON organizations(relationship_status);
CREATE INDEX IF NOT EXISTS idx_organizations_domain ON organizations(domain);

-- ============================================================================
-- ENHANCED PEOPLE TABLE
-- ============================================================================

-- Add organization relationship to people
ALTER TABLE people ADD COLUMN IF NOT EXISTS person_type TEXT DEFAULT 'internal';  
-- 'internal' (employee), 'client', 'partner', 'advisor', 'founder'

ALTER TABLE people ADD COLUMN IF NOT EXISTS primary_organization_id UUID REFERENCES organizations(id);
ALTER TABLE people ADD COLUMN IF NOT EXISTS job_title TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS department TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS bio TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS linkedin_url TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS twitter_url TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS photo_url TEXT;

-- For internal employees
ALTER TABLE people ADD COLUMN IF NOT EXISTS employee_id TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS start_date DATE;
ALTER TABLE people ADD COLUMN IF NOT EXISTS employment_type TEXT;  -- 'full-time', 'part-time', 'contractor'

-- Metadata
ALTER TABLE people ADD COLUMN IF NOT EXISTS last_interaction_date DATE;
ALTER TABLE people ADD COLUMN IF NOT EXISTS tags TEXT[];

CREATE INDEX IF NOT EXISTS idx_people_type ON people(person_type);
CREATE INDEX IF NOT EXISTS idx_people_organization ON people(primary_organization_id);

-- ============================================================================
-- PERSON-ORGANIZATION RELATIONSHIPS (Many-to-many)
-- ============================================================================

CREATE TABLE IF NOT EXISTS person_organization_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Role at this organization
    role_title TEXT,  -- "CEO", "CTO", "Advisor", etc.
    is_primary BOOLEAN DEFAULT false,  -- Primary organization for this person
    is_active BOOLEAN DEFAULT true,
    
    -- Dates
    start_date DATE,
    end_date DATE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(person_id, organization_id, role_title)
);

CREATE INDEX IF NOT EXISTS idx_person_org_roles_person ON person_organization_roles(person_id);
CREATE INDEX IF NOT EXISTS idx_person_org_roles_org ON person_organization_roles(organization_id);

-- ============================================================================
-- COMPANY LOGO SCRAPING LOG
-- ============================================================================

CREATE TABLE IF NOT EXISTS logo_scrape_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain TEXT NOT NULL UNIQUE,
    
    -- Scraped data
    logo_url TEXT,
    favicon_url TEXT,
    company_name TEXT,  -- From website
    description TEXT,  -- Meta description
    
    -- Scraping metadata
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    scrape_success BOOLEAN DEFAULT true,
    scrape_method TEXT,  -- 'clearbit', 'manual', 'google', 'website_parser'
    
    -- Cache validity
    cache_expires_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_logo_scrape_domain ON logo_scrape_cache(domain);

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE person_organization_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE logo_scrape_cache ENABLE ROW LEVEL SECURITY;

-- Org members can view organizations
CREATE POLICY "Org members can view organizations"
    ON organizations FOR SELECT
    USING (
        org_id IN (
            SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid()
        )
    );

-- Org admins can manage organizations
CREATE POLICY "Org admins can manage organizations"
    ON organizations FOR ALL
    USING (
        org_id IN (
            SELECT om.org_id FROM org_memberships om 
            WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')
        )
    );

-- Service role access
CREATE POLICY "Service role organizations" ON organizations FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role person_org_roles" ON person_organization_roles FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role logo_cache" ON logo_scrape_cache FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to extract domain from email
CREATE OR REPLACE FUNCTION extract_domain_from_email(email TEXT)
RETURNS TEXT AS $$
BEGIN
    IF email IS NULL OR email = '' THEN
        RETURN NULL;
    END IF;
    
    RETURN SPLIT_PART(email, '@', 2);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to get or create organization from domain
CREATE OR REPLACE FUNCTION get_or_create_organization_from_domain(
    p_org_id UUID,
    p_domain TEXT
)
RETURNS UUID AS $$
DECLARE
    org_record RECORD;
BEGIN
    -- Check if organization exists for this domain
    SELECT id INTO org_record
    FROM organizations
    WHERE org_id = p_org_id AND domain = p_domain
    LIMIT 1;
    
    IF FOUND THEN
        RETURN org_record.id;
    END IF;
    
    -- Create new organization
    INSERT INTO organizations (org_id, name, domain, website_url, organization_type)
    VALUES (p_org_id, INITCAP(REPLACE(p_domain, '.com', '')), p_domain, 'https://' || p_domain, 'client')
    RETURNING id INTO org_record;
    
    RETURN org_record.id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE organizations IS 'Companies, clients, partners, portfolio companies';
COMMENT ON TABLE person_organization_roles IS 'Many-to-many: people can have roles at multiple organizations';
COMMENT ON TABLE logo_scrape_cache IS 'Cached company logos and info scraped from websites';

COMMENT ON COLUMN organizations.organization_type IS 'client, partner, portfolio, vendor, competitor';
COMMENT ON COLUMN organizations.relationship_owner_id IS 'DV team member who owns this relationship';
COMMENT ON COLUMN people.person_type IS 'internal (employee), client, partner, advisor, founder';
COMMENT ON COLUMN people.primary_organization_id IS 'Main company this person works for';

