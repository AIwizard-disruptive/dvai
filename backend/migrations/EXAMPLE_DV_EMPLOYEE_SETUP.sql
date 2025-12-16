-- ============================================================================
-- EXAMPLE: Complete DV Employee Setup Workflow
-- ============================================================================
-- This script demonstrates the full employee management workflow:
-- 1. Create employee
-- 2. Generate CV from LinkedIn
-- 3. Create employment contract
-- 4. Link contract to employee
-- 5. Sync to Google Workspace
-- ============================================================================

-- PREREQUISITE: Get your org_id
-- SELECT id, name FROM orgs WHERE domain = 'disruptiveventures.se';
-- Replace 'YOUR_ORG_ID' below with your actual org_id

DO $$
DECLARE
    v_org_id UUID := 'YOUR_ORG_ID';  -- Replace with your actual org_id
    v_person_id UUID;
    v_contract_id UUID;
    v_cv_id UUID;
    v_google_payload JSONB;
BEGIN

-- ============================================================================
-- STEP 1: Create Employee Profile
-- ============================================================================

INSERT INTO people (
    org_id,
    name,
    work_email,
    person_type,
    job_title,
    department,
    phone,
    location,
    linkedin_url,
    employment_type,
    start_date,
    employee_number
)
VALUES (
    v_org_id,
    'Anna Svensson',
    'anna.svensson@disruptiveventures.se',
    'internal',
    'Investment Manager',
    'Ventures',
    '+46701234567',
    'Stockholm, Sweden',
    'https://linkedin.com/in/annasvensson',
    'full-time',
    '2022-01-15',
    'DV-001'
)
RETURNING id INTO v_person_id;

RAISE NOTICE '✅ Created employee: % (ID: %)', 'Anna Svensson', v_person_id;

-- ============================================================================
-- STEP 2: Generate CV from LinkedIn Data
-- ============================================================================

-- Simulate LinkedIn profile data (in real scenario, this comes from scraper)
SELECT generate_cv_from_linkedin(
    v_person_id,
    jsonb_build_object(
        'headline', 'Investment Manager | Early-stage Ventures',
        'summary', 'Investment professional with 8 years of experience in venture capital, focusing on early-stage tech companies. Expertise in due diligence, portfolio management, and founder support.',
        'positions', jsonb_build_array(
            jsonb_build_object(
                'title', 'Investment Manager',
                'company', 'Disruptive Ventures',
                'startDate', '2022-01',
                'endDate', null,
                'current', true,
                'description', 'Lead investment decisions for early-stage SaaS and AI companies.'
            ),
            jsonb_build_object(
                'title', 'Senior Analyst',
                'company', 'Nordic Capital',
                'startDate', '2019-03',
                'endDate', '2021-12',
                'current', false,
                'description', 'Performed due diligence on growth equity investments.'
            )
        ),
        'education', jsonb_build_array(
            jsonb_build_object(
                'school', 'Stockholm School of Economics',
                'degree', 'MSc Finance',
                'fieldOfStudy', 'Corporate Finance',
                'startDate', '2015',
                'endDate', '2017'
            )
        ),
        'skills', jsonb_build_array(
            'Venture Capital',
            'Due Diligence',
            'Portfolio Management',
            'Financial Modeling',
            'Strategic Planning',
            'Startup Ecosystems'
        ),
        'certifications', jsonb_build_array(
            jsonb_build_object(
                'name', 'CFA Level II',
                'authority', 'CFA Institute',
                'year', 2020
            )
        ),
        'languages', jsonb_build_array(
            jsonb_build_object('language', 'Swedish', 'proficiency', 'Native'),
            jsonb_build_object('language', 'English', 'proficiency', 'Fluent')
        ),
        'profilePicture', 'https://media.licdn.com/dms/image/example.jpg'
    ),
    'executive'  -- CV format
) INTO v_cv_id;

RAISE NOTICE '✅ Generated CV from LinkedIn (CV ID: %)', v_cv_id;

-- ============================================================================
-- STEP 3: Create Employment Contract
-- ============================================================================

INSERT INTO contracts (
    org_id,
    contract_type,
    contract_name,
    party_person_id,
    start_date,
    end_date,
    value,
    currency,
    employment_type,
    probation_end_date,
    notice_period_days,
    terms,
    status,
    google_doc_id
)
VALUES (
    v_org_id,
    'employment',
    'Employment Agreement - Anna Svensson',
    v_person_id,
    '2022-01-15',
    NULL,  -- Permanent employment
    720000,  -- 720k SEK annual salary
    'SEK',
    'full-time',
    '2022-07-15',  -- 6 months probation
    90,  -- 3 months notice period
    jsonb_build_object(
        'salary_breakdown', jsonb_build_object(
            'base_salary', 600000,
            'bonus_potential', 120000,
            'equity_options', 5000
        ),
        'benefits', jsonb_build_array(
            'Health insurance',
            'Pension 4.5% employer contribution',
            'Wellness allowance 5000 SEK/year',
            'Mobile phone',
            'Home office setup'
        ),
        'vacation_days', 30,
        'remote_work', 'hybrid - 3 days office, 2 days remote',
        'equipment', jsonb_build_array(
            'MacBook Pro 16"',
            'iPhone',
            'Headphones',
            'External monitor'
        ),
        'professional_development', jsonb_build_object(
            'budget', 20000,
            'currency', 'SEK',
            'frequency', 'annual'
        )
    ),
    'draft',  -- Start as draft, will be 'sent' -> 'signed' -> 'active'
    '1abcdefGHIJKLMNOP_qrstuvwxyz'  -- Google Docs ID
)
RETURNING id INTO v_contract_id;

RAISE NOTICE '✅ Created employment contract (Contract ID: %)', v_contract_id;

-- ============================================================================
-- STEP 4: Link Contract to Employee
-- ============================================================================

PERFORM link_person_to_contract(v_person_id, v_contract_id);

RAISE NOTICE '✅ Linked contract to employee';

-- ============================================================================
-- STEP 5: Generate Google Workspace Sync Payload
-- ============================================================================

SELECT sync_person_to_google_directory(v_person_id) INTO v_google_payload;

RAISE NOTICE '✅ Generated Google Workspace sync payload:';
RAISE NOTICE '%', v_google_payload;

-- ============================================================================
-- STEP 6: Create Google Sync Record
-- ============================================================================

INSERT INTO google_profile_syncs (
    person_id,
    google_user_id,
    google_email,
    sync_status,
    fields_to_sync,
    auto_sync_enabled,
    sync_frequency,
    current_profile_data
)
VALUES (
    v_person_id,
    NULL,  -- Will be filled after first sync with Google
    'anna.svensson@disruptiveventures.se',
    'pending',
    ARRAY['name', 'title', 'department', 'phone', 'bio', 'photo', 'location'],
    true,
    'daily',
    v_google_payload
);

RAISE NOTICE '✅ Created Google Workspace sync record';

-- ============================================================================
-- VERIFICATION: Show complete employee profile
-- ============================================================================

RAISE NOTICE '';
RAISE NOTICE '════════════════════════════════════════════════════════════';
RAISE NOTICE 'COMPLETE EMPLOYEE PROFILE';
RAISE NOTICE '════════════════════════════════════════════════════════════';

-- Employee details
PERFORM (
    SELECT 
        RAISE(NOTICE, 'Name: %', p.name),
        RAISE(NOTICE, 'Email: %', p.work_email),
        RAISE(NOTICE, 'Domain: %', p.email_domain),
        RAISE(NOTICE, 'Employee #: %', p.employee_number),
        RAISE(NOTICE, 'Title: %', p.job_title),
        RAISE(NOTICE, 'Department: %', p.department),
        RAISE(NOTICE, 'Phone: %', p.phone),
        RAISE(NOTICE, 'LinkedIn: %', p.linkedin_url),
        RAISE(NOTICE, 'Contract Start: %', p.contract_start_date),
        RAISE(NOTICE, 'Employment Type: %', p.employment_type)
    FROM people p
    WHERE p.id = v_person_id
);

RAISE NOTICE '';
RAISE NOTICE '✅ Employee setup complete!';

END $$;

-- ============================================================================
-- USEFUL QUERIES AFTER SETUP
-- ============================================================================

-- View all DV employees
-- SELECT 
--     name,
--     work_email,
--     email_domain,
--     job_title,
--     department,
--     employee_number,
--     contract_start_date
-- FROM people
-- WHERE email_domain = 'disruptiveventures.se'
-- AND person_type = 'internal';

-- View employee with contract details
-- SELECT 
--     p.name,
--     p.work_email,
--     p.job_title,
--     c.contract_type,
--     c.value as annual_salary,
--     c.currency,
--     c.status as contract_status,
--     c.terms->>'vacation_days' as vacation_days,
--     c.terms->'salary_breakdown'->>'base_salary' as base_salary
-- FROM people p
-- LEFT JOIN contracts c ON c.id = p.employment_contract_id
-- WHERE p.email_domain = 'disruptiveventures.se';

-- View employee CV
-- SELECT 
--     p.name,
--     cv.generated_from_linkedin,
--     cv.cv_format,
--     cv.extracted_competencies,
--     cv.linkedin_scraped_at
-- FROM people p
-- JOIN person_cvs cv ON cv.person_id = p.id
-- WHERE p.email_domain = 'disruptiveventures.se'
-- AND cv.is_primary = true;

-- View employee competencies
-- SELECT 
--     p.name,
--     pc.skill_name,
--     pc.skill_category,
--     pc.proficiency_level,
--     pc.source
-- FROM people p
-- JOIN person_competencies pc ON pc.person_id = p.id
-- WHERE p.email_domain = 'disruptiveventures.se'
-- ORDER BY p.name, pc.skill_name;
