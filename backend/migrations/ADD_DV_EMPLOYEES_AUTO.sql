-- ============================================================================
-- ADD DV EMPLOYEES - AUTO ORG_ID
-- ============================================================================
-- This script automatically fetches your org_id and adds all DV employees
-- 
-- ⚠️  PREREQUISITES: Run migrations 007, 008, 009 first!
--    Or run: psql $DATABASE_URL -f backend/migrations/009_people_wheel_clean.sql
-- 
-- ⚠️  PLACEHOLDER DATA: job_title, department, bio must be updated with real info
-- 
-- WHAT THIS DOES:
-- 1. Ensures required columns exist on people table
-- 2. Automatically gets your org_id
-- 3. Adds all 27 employees with LinkedIn URLs
-- ============================================================================

-- Ensure required columns exist (idempotent)
ALTER TABLE people ADD COLUMN IF NOT EXISTS work_email TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS email_domain TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS person_type TEXT DEFAULT 'internal';
ALTER TABLE people ADD COLUMN IF NOT EXISTS job_title TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS department TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS bio TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS linkedin_url TEXT;

-- Create indexes if needed
CREATE INDEX IF NOT EXISTS idx_people_work_email ON people(work_email);
CREATE INDEX IF NOT EXISTS idx_people_email_domain ON people(email_domain);

DO $$
DECLARE
    v_org_id UUID;
    v_org_name TEXT;
BEGIN

-- Try to find org by name (Disruptive Ventures)
SELECT id, name INTO v_org_id, v_org_name 
FROM orgs 
WHERE name ILIKE '%disruptive%' OR name ILIKE '%DV%'
LIMIT 1;

IF v_org_id IS NULL THEN
    -- If no DV org found, use the first org available
    SELECT id, name INTO v_org_id, v_org_name FROM orgs LIMIT 1;
    
    IF v_org_id IS NULL THEN
        RAISE EXCEPTION 'No org found! Please create an org first.';
    END IF;
END IF;

RAISE NOTICE 'Using org: % (ID: %)', v_org_name, v_org_id;

-- ============================================================================
-- EMPLOYEE 1: Julia Ludvigsson
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type, 
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Julia Ludvigsson',
    'julia.ludvigsson@disruptiveventures.se',
    'julia.ludvigsson@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/julia-ludvigsson-4a8868306/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 2: Markus Löwegren
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Markus Löwegren',
    'markus.lowegren@disruptiveventures.se',
    'markus.lowegren@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/markus-löwegren-43b75017/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 3: Fanny Lundin
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Fanny Lundin',
    'fanny.lundin@disruptiveventures.se',
    'fanny.lundin@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/fanny-lundin-/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 4: Jonna Persson
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Jonna Persson',
    'jonna.persson@disruptiveventures.se',
    'jonna.persson@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/jonna-persson-77344b1b5/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 5: Anton Nygren
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Anton Nygren',
    'anton.nygren@disruptiveventures.se',
    'anton.nygren@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/anton-nygren/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 6: Serge Lachapelle
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Serge Lachapelle',
    'serge.lachapelle@disruptiveventures.se',
    'serge.lachapelle@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/sergelachapelle/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

-- ============================================================================
-- EMPLOYEE 7: Martin Peterson
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Martin Peterson',
    'martin.peterson@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/martin-peterson-590127254/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

-- ============================================================================
-- EMPLOYEE 8: Henrik Lundgren
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Henrik Lundgren',
    'henrik.lundgren@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/henrik-lundgren-29751255/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

-- ============================================================================
-- EMPLOYEE 9: Johan de Boer
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Johan de Boer',
    'johan.deboer@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/johan-deboer/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

-- ============================================================================
-- EMPLOYEE 10: Per-Ola Gradin
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Per-Ola Gradin',
    'per-ola.gradin@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/per-ola-gradin-2b0396257/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

-- ============================================================================
-- EMPLOYEE 11: Joel Ek
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Joel Ek',
    'joel.ek@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/joelek123/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

-- ============================================================================
-- EMPLOYEE 12: Pontus Kressner
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Pontus Kressner',
    'pontus.kressner@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/pontus-kressner-72268552/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

-- ============================================================================
-- EMPLOYEE 13: Marlise Janssen
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Marlise Janssen',
    'marlise.janssen@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/marlisejanssen/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

-- ============================================================================
-- EMPLOYEE 14: Mikaela Jansson
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Mikaela Jansson',
    'mikaela.jansson@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/mikaela-jansson-823393126/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

-- ============================================================================
-- EMPLOYEE 15: Vendela Holmgren
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Vendela Holmgren',
    'vendela.holmgren@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/vendela-holmgren-593181234/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

-- ============================================================================
-- EMPLOYEE 16: Simon Johannesson
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Simon Johannesson',
    'simon.johannesson@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/simon-johannesson-597516178/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

-- ============================================================================
-- EMPLOYEE 17: Emrik Cygnaeus
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Emrik Cygnaeus',
    'emrik.cygnaeus@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/emrik-cygnaeus-1154571b5/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

-- ============================================================================
-- EMPLOYEE 18: H W Melius
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'H W Melius',
    'hw.melius@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/hwmelius/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

-- ============================================================================
-- EMPLOYEE 19: Noah Kovacs
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Noah Kovacs',
    'noah.kovacs@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/noah-kovacs-112984291/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

-- ============================================================================
-- EMPLOYEE 20: Niklas Jansson
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Niklas Jansson',
    'niklas.jansson@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/niklas-jansson-🇺🇦-070b596/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

-- ============================================================================
-- EMPLOYEE 21: Leo Kylin
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Leo Kylin',
    'leo.kylin@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/leokylin/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

-- ============================================================================
-- EMPLOYEE 22: Alexander Höglund
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Alexander Höglund',
    'alexander.hoglund@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/alexanderhöglund/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

-- ============================================================================
-- EMPLOYEE 23: Jakob Nylund
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Jakob Nylund',
    'jakob.nylund@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/jakobnylund/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

-- ============================================================================
-- EMPLOYEE 24: Charlotta Stickler
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Charlotta Stickler',
    'charlotta.stickler@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/charlotta-stickler-86b7a3221/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

-- ============================================================================
-- EMPLOYEE 25: Jakob Cedermark
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Jakob Cedermark',
    'jakob.cedermark@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/jakob-cedermark-6983601b0/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

-- ============================================================================
-- EMPLOYEE 26: Philip Stålnert
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Philip Stålnert',
    'philip.stalnert@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/philip-stålnert-095766157/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

-- ============================================================================
-- EMPLOYEE 27: Simon Ritzén
-- ============================================================================
INSERT INTO people (
    org_id, name, email, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Simon Ritzén',
    'simon.ritzen@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update with real title',
    'PLACEHOLDER - Update with real department',
    'https://www.linkedin.com/in/simon-ritzén-09423a211/',
    'PLACEHOLDER - Update with real bio from LinkedIn',
    'disruptiveventures.se'
) ON CONFLICT (org_id, email) DO NOTHING;

RAISE NOTICE '✅ Added 27 DV employees with LinkedIn URLs';
RAISE NOTICE '⚠️  IMPORTANT: Update PLACEHOLDER fields with real data from LinkedIn!';

END $$;

-- ============================================================================
-- VERIFICATION & UPDATE QUERIES
-- ============================================================================

-- View all employees (verify they were created)
SELECT 
    name, 
    work_email, 
    job_title,
    department,
    linkedin_url
FROM people
WHERE email_domain = 'disruptiveventures.se'
ORDER BY name;

-- ============================================================================
-- UPDATE TEMPLATE (Use this to update each employee with real data)
-- ============================================================================
/*

-- Example: Update Julia Ludvigsson with real data from LinkedIn
UPDATE people
SET
    job_title = 'Investment Analyst',  -- Replace with real title
    department = 'Ventures',           -- Replace with real department
    bio = 'Investment analyst focused on early-stage tech companies...',  -- Real bio
    phone = '+46701234567',           -- If available
    location = 'Stockholm',           -- If available
    updated_at = NOW()
WHERE work_email = 'julia.ludvigsson@disruptiveventures.se';

-- Repeat for each employee...

*/
