-- ============================================================================
-- ADD DV EMPLOYEES - FIXED VERSION
-- ============================================================================
-- Adds all 27 DV employees with LinkedIn URLs
-- ⚠️  PLACEHOLDER DATA: job_title, department, bio must be updated with real info
-- ============================================================================

-- Ensure required columns exist (idempotent)
ALTER TABLE people ADD COLUMN IF NOT EXISTS work_email TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS email_domain TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS person_type TEXT DEFAULT 'internal';
ALTER TABLE people ADD COLUMN IF NOT EXISTS job_title TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS department TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS bio TEXT;
ALTER TABLE people ADD COLUMN IF NOT EXISTS linkedin_url TEXT;

-- Create unique constraint for conflict handling
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'people_org_email_unique'
    ) THEN
        ALTER TABLE people ADD CONSTRAINT people_org_email_unique UNIQUE (org_id, email);
    END IF;
END $$;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_people_work_email ON people(work_email);
CREATE INDEX IF NOT EXISTS idx_people_email_domain ON people(email_domain);
CREATE INDEX IF NOT EXISTS idx_people_linkedin_url ON people(linkedin_url);

-- ============================================================================
-- INSERT EMPLOYEES
-- ============================================================================

DO $$
DECLARE
    v_org_id UUID;
    v_org_name TEXT;
    v_inserted_count INTEGER := 0;
BEGIN

-- Find org
SELECT id, name INTO v_org_id, v_org_name 
FROM orgs 
WHERE name ILIKE '%disruptive%' OR name ILIKE '%DV%'
LIMIT 1;

IF v_org_id IS NULL THEN
    SELECT id, name INTO v_org_id, v_org_name FROM orgs LIMIT 1;
    IF v_org_id IS NULL THEN
        RAISE EXCEPTION 'No org found! Please create an org first.';
    END IF;
END IF;

RAISE NOTICE 'Using org: % (ID: %)', v_org_name, v_org_id;

-- Employee 1: Julia Ludvigsson
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Julia Ludvigsson', 'julia.ludvigsson@disruptiveventures.se', 'julia.ludvigsson@disruptiveventures.se', 'internal', 
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/julia-ludvigsson-4a8868306/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;
IF FOUND THEN v_inserted_count := v_inserted_count + 1; END IF;

-- Employee 2: Markus Löwegren
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Markus Löwegren', 'markus.lowegren@disruptiveventures.se', 'markus.lowegren@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/markus-löwegren-43b75017/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 3: Fanny Lundin
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Fanny Lundin', 'fanny.lundin@disruptiveventures.se', 'fanny.lundin@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/fanny-lundin-/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 4: Jonna Persson
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Jonna Persson', 'jonna.persson@disruptiveventures.se', 'jonna.persson@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/jonna-persson-77344b1b5/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 5: Anton Nygren
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Anton Nygren', 'anton.nygren@disruptiveventures.se', 'anton.nygren@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/anton-nygren/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 6: Serge Lachapelle
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Serge Lachapelle', 'serge.lachapelle@disruptiveventures.se', 'serge.lachapelle@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/sergelachapelle/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 7: Martin Peterson
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Martin Peterson', 'martin.peterson@disruptiveventures.se', 'martin.peterson@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/martin-peterson-590127254/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 8: Henrik Lundgren
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Henrik Lundgren', 'henrik.lundgren@disruptiveventures.se', 'henrik.lundgren@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/henrik-lundgren-29751255/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 9: Johan de Boer
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Johan de Boer', 'johan.deboer@disruptiveventures.se', 'johan.deboer@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/johan-deboer/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 10: Per-Ola Gradin
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Per-Ola Gradin', 'per-ola.gradin@disruptiveventures.se', 'per-ola.gradin@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/per-ola-gradin-2b0396257/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 11: Joel Ek
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Joel Ek', 'joel.ek@disruptiveventures.se', 'joel.ek@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/joelek123/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 12: Pontus Kressner
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Pontus Kressner', 'pontus.kressner@disruptiveventures.se', 'pontus.kressner@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/pontus-kressner-72268552/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 13: Marlise Janssen
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Marlise Janssen', 'marlise.janssen@disruptiveventures.se', 'marlise.janssen@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/marlisejanssen/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 14: Mikaela Jansson
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Mikaela Jansson', 'mikaela.jansson@disruptiveventures.se', 'mikaela.jansson@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/mikaela-jansson-823393126/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 15: Vendela Holmgren
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Vendela Holmgren', 'vendela.holmgren@disruptiveventures.se', 'vendela.holmgren@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/vendela-holmgren-593181234/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 16: Simon Johannesson
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Simon Johannesson', 'simon.johannesson@disruptiveventures.se', 'simon.johannesson@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/simon-johannesson-597516178/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 17: Emrik Cygnaeus
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Emrik Cygnaeus', 'emrik.cygnaeus@disruptiveventures.se', 'emrik.cygnaeus@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/emrik-cygnaeus-1154571b5/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 18: H W Melius
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'H W Melius', 'hw.melius@disruptiveventures.se', 'hw.melius@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/hwmelius/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 19: Noah Kovacs
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Noah Kovacs', 'noah.kovacs@disruptiveventures.se', 'noah.kovacs@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/noah-kovacs-112984291/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 20: Niklas Jansson
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Niklas Jansson', 'niklas.jansson@disruptiveventures.se', 'niklas.jansson@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/niklas-jansson-🇺🇦-070b596/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 21: Leo Kylin
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Leo Kylin', 'leo.kylin@disruptiveventures.se', 'leo.kylin@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/leokylin/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 22: Alexander Höglund
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Alexander Höglund', 'alexander.hoglund@disruptiveventures.se', 'alexander.hoglund@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/alexanderhöglund/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 23: Jakob Nylund
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Jakob Nylund', 'jakob.nylund@disruptiveventures.se', 'jakob.nylund@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/jakobnylund/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 24: Charlotta Stickler
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Charlotta Stickler', 'charlotta.stickler@disruptiveventures.se', 'charlotta.stickler@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/charlotta-stickler-86b7a3221/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 25: Jakob Cedermark
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Jakob Cedermark', 'jakob.cedermark@disruptiveventures.se', 'jakob.cedermark@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/jakob-cedermark-6983601b0/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 26: Philip Stålnert
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Philip Stålnert', 'philip.stalnert@disruptiveventures.se', 'philip.stalnert@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/philip-stålnert-095766157/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

-- Employee 27: Simon Ritzén
INSERT INTO people (org_id, name, email, work_email, person_type, job_title, department, linkedin_url, bio, email_domain)
VALUES (v_org_id, 'Simon Ritzén', 'simon.ritzen@disruptiveventures.se', 'simon.ritzen@disruptiveventures.se', 'internal',
        'PLACEHOLDER', 'PLACEHOLDER', 'https://www.linkedin.com/in/simon-ritzén-09423a211/', 'PLACEHOLDER', 'disruptiveventures.se')
ON CONFLICT (org_id, email) DO NOTHING;

RAISE NOTICE '✅ Successfully added 27 DV employees with LinkedIn URLs';
RAISE NOTICE '⚠️  IMPORTANT: Update PLACEHOLDER fields (job_title, department, bio) with real data from LinkedIn profiles!';

END $$;

-- ============================================================================
-- VERIFICATION
-- ============================================================================
SELECT 
    name, 
    email,
    work_email, 
    job_title,
    department,
    linkedin_url
FROM people
WHERE email_domain = 'disruptiveventures.se'
ORDER BY name;
