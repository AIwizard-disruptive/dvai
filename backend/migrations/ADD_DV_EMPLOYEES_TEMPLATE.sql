-- ============================================================================
-- ADD DV EMPLOYEES - TEMPLATE
-- ============================================================================
-- This script provides a template for adding DV employees with LinkedIn profiles.
-- 
-- ⚠️  IMPORTANT: This template contains PLACEHOLDER data that MUST be replaced
--     with real information from LinkedIn profiles before execution.
-- 
-- HOW TO USE:
-- 1. For each person below, visit their LinkedIn profile
-- 2. Replace PLACEHOLDER values with actual data
-- 3. Remove any employees that shouldn't be added
-- 4. Update YOUR_ORG_ID with your actual org_id
-- 5. Run this script
-- ============================================================================

-- Get your org_id first:
-- SELECT id FROM orgs WHERE domain = 'disruptiveventures.se';

DO $$
DECLARE
    v_org_id UUID := 'YOUR_ORG_ID';  -- ⚠️  REPLACE THIS
BEGIN

-- ============================================================================
-- EMPLOYEE 1: Julia Ludvigsson
-- LinkedIn: https://www.linkedin.com/in/julia-ludvigsson-4a8868306/
-- ============================================================================
-- ⚠️  PLACEHOLDER - Replace with actual data from LinkedIn profile
INSERT INTO people (
    org_id, name, work_email, person_type, 
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Julia Ludvigsson',  -- ✅ Real name from LinkedIn URL
    'julia.ludvigsson@disruptiveventures.se',  -- ⚠️  PLACEHOLDER - Verify actual email
    'internal',
    'PLACEHOLDER_TITLE',  -- ⚠️  REPLACE: Get from LinkedIn (e.g., 'Investment Analyst')
    'PLACEHOLDER_DEPT',   -- ⚠️  REPLACE: e.g., 'Ventures', 'Operations'
    'https://www.linkedin.com/in/julia-ludvigsson-4a8868306/',
    'PLACEHOLDER_BIO',    -- ⚠️  REPLACE: Short bio from LinkedIn summary/headline
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 2: Markus Löwegren
-- LinkedIn: https://www.linkedin.com/in/markus-löwegren-43b75017/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Markus Löwegren',
    'markus.lowegren@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/markus-löwegren-43b75017/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 3: Fanny Lundin
-- LinkedIn: https://www.linkedin.com/in/fanny-lundin-/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Fanny Lundin',
    'fanny.lundin@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/fanny-lundin-/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 4: Jonna Persson
-- LinkedIn: https://www.linkedin.com/in/jonna-persson-77344b1b5/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Jonna Persson',
    'jonna.persson@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/jonna-persson-77344b1b5/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 5: Anton Nygren
-- LinkedIn: https://www.linkedin.com/in/anton-nygren/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Anton Nygren',
    'anton.nygren@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/anton-nygren/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 6: Serge Lachapelle
-- LinkedIn: https://www.linkedin.com/in/sergelachapelle/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Serge Lachapelle',
    'serge.lachapelle@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/sergelachapelle/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 7: Martin Peterson
-- LinkedIn: https://www.linkedin.com/in/martin-peterson-590127254/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Martin Peterson',
    'martin.peterson@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/martin-peterson-590127254/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 8: Henrik Lundgren
-- LinkedIn: https://www.linkedin.com/in/henrik-lundgren-29751255/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Henrik Lundgren',
    'henrik.lundgren@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/henrik-lundgren-29751255/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 9: Johan de Boer
-- LinkedIn: https://www.linkedin.com/in/johan-deboer/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Johan de Boer',
    'johan.deboer@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/johan-deboer/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 10: Per-Ola Gradin
-- LinkedIn: https://www.linkedin.com/in/per-ola-gradin-2b0396257/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Per-Ola Gradin',
    'per-ola.gradin@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/per-ola-gradin-2b0396257/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 11: Joel Ek
-- LinkedIn: https://www.linkedin.com/in/joelek123/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Joel Ek',
    'joel.ek@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/joelek123/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 12: Pontus Kressner
-- LinkedIn: https://www.linkedin.com/in/pontus-kressner-72268552/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Pontus Kressner',
    'pontus.kressner@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/pontus-kressner-72268552/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 13: Marlise Janssen
-- LinkedIn: https://www.linkedin.com/in/marlisejanssen/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Marlise Janssen',
    'marlise.janssen@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/marlisejanssen/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 14: Mikaela Jansson
-- LinkedIn: https://www.linkedin.com/in/mikaela-jansson-823393126/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Mikaela Jansson',
    'mikaela.jansson@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/mikaela-jansson-823393126/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 15: Vendela Holmgren
-- LinkedIn: https://www.linkedin.com/in/vendela-holmgren-593181234/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Vendela Holmgren',
    'vendela.holmgren@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/vendela-holmgren-593181234/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 16: Simon Johannesson
-- LinkedIn: https://www.linkedin.com/in/simon-johannesson-597516178/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Simon Johannesson',
    'simon.johannesson@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/simon-johannesson-597516178/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 17: Emrik Cygnaeus
-- LinkedIn: https://www.linkedin.com/in/emrik-cygnaeus-1154571b5/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Emrik Cygnaeus',
    'emrik.cygnaeus@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/emrik-cygnaeus-1154571b5/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 18: H W Melius
-- LinkedIn: https://www.linkedin.com/in/hwmelius/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'H W Melius',
    'hw.melius@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/hwmelius/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 19: Noah Kovacs
-- LinkedIn: https://www.linkedin.com/in/noah-kovacs-112984291/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Noah Kovacs',
    'noah.kovacs@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/noah-kovacs-112984291/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 20: Niklas Jansson
-- LinkedIn: https://www.linkedin.com/in/niklas-jansson-🇺🇦-070b596/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Niklas Jansson',
    'niklas.jansson@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/niklas-jansson-🇺🇦-070b596/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 21: Leo Kylin
-- LinkedIn: https://www.linkedin.com/in/leokylin/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Leo Kylin',
    'leo.kylin@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/leokylin/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 22: Alexander Höglund
-- LinkedIn: https://www.linkedin.com/in/alexanderhöglund/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Alexander Höglund',
    'alexander.hoglund@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/alexanderhöglund/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 23: Jakob Nylund
-- LinkedIn: https://www.linkedin.com/in/jakobnylund/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Jakob Nylund',
    'jakob.nylund@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/jakobnylund/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 24: Charlotta Stickler
-- LinkedIn: https://www.linkedin.com/in/charlotta-stickler-86b7a3221/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Charlotta Stickler',
    'charlotta.stickler@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/charlotta-stickler-86b7a3221/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 25: Jakob Cedermark
-- LinkedIn: https://www.linkedin.com/in/jakob-cedermark-6983601b0/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Jakob Cedermark',
    'jakob.cedermark@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/jakob-cedermark-6983601b0/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 26: Philip Stålnert
-- LinkedIn: https://www.linkedin.com/in/philip-stålnert-095766157/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Philip Stålnert',
    'philip.stalnert@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/philip-stålnert-095766157/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- EMPLOYEE 27: Simon Ritzén
-- LinkedIn: https://www.linkedin.com/in/simon-ritzén-09423a211/
-- ============================================================================
INSERT INTO people (
    org_id, name, work_email, person_type,
    job_title, department, linkedin_url, bio, email_domain
) VALUES (
    v_org_id,
    'Simon Ritzén',
    'simon.ritzen@disruptiveventures.se',
    'internal',
    'PLACEHOLDER_TITLE',
    'PLACEHOLDER_DEPT',
    'https://www.linkedin.com/in/simon-ritzén-09423a211/',
    'PLACEHOLDER_BIO',
    'disruptiveventures.se'
) ON CONFLICT DO NOTHING;

RAISE NOTICE '✅ Template script completed. Remember to replace all PLACEHOLDER values!';

END $$;

-- ============================================================================
-- VERIFICATION QUERY
-- ============================================================================
-- After replacing placeholders and running script, verify with:
-- 
-- SELECT name, work_email, job_title, department, linkedin_url
-- FROM people
-- WHERE email_domain = 'disruptiveventures.se'
-- ORDER BY name;
