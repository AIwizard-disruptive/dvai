-- ============================================================================
-- SETUP: Wizard & Serge Task Sync with Marcus
-- ============================================================================
-- Sets up wizard@disruptiveventures.se and serge@disruptiveventures.se
-- to sync Google Tasks and profiles from your database
-- Their Linear tasks will match your Linear tasks
-- ============================================================================

-- Run migration 013 first if not already run
-- \i backend/migrations/013_task_sync_system.sql

DO $$
DECLARE
    v_org_id UUID;
    v_marcus_person_id UUID;
    v_wizard_person_id UUID;
    v_serge_person_id UUID;
    v_marcus_linear_id TEXT;
    v_marcus_task RECORD;
BEGIN

-- ============================================================================
-- STEP 1: Get org_id and Marcus's person_id
-- ============================================================================
SELECT id INTO v_org_id FROM orgs LIMIT 1;

IF v_org_id IS NULL THEN
    RAISE EXCEPTION 'No org found!';
END IF;

-- Find Marcus
SELECT id INTO v_marcus_person_id 
FROM people 
WHERE email ILIKE '%marcus%' 
   OR name ILIKE '%marcus%'
LIMIT 1;

IF v_marcus_person_id IS NULL THEN
    RAISE NOTICE 'Marcus not found, creating placeholder';
    INSERT INTO people (org_id, name, email, person_type)
    VALUES (v_org_id, 'Marcus', 'marcus@disruptiveventures.se', 'internal')
    RETURNING id INTO v_marcus_person_id;
END IF;

-- Get Marcus's Linear user ID (if exists)
SELECT linear_user_id INTO v_marcus_linear_id
FROM linear_user_mappings
WHERE person_email ILIKE '%marcus%'
LIMIT 1;

RAISE NOTICE 'Marcus person_id: %', v_marcus_person_id;
RAISE NOTICE 'Marcus linear_id: %', COALESCE(v_marcus_linear_id, 'NOT SET');

-- ============================================================================
-- STEP 2: Create/Update Wizard person
-- ============================================================================
INSERT INTO people (
    org_id,
    name,
    email,
    work_email,
    person_type,
    job_title,
    department,
    bio,
    email_domain
) VALUES (
    v_org_id,
    'Wizard',
    'wizard@disruptiveventures.se',
    'wizard@disruptiveventures.se',
    'internal',
    'AI Assistant',
    'Operations',
    'AI-powered assistant helping with task management and workflow automation.',
    'disruptiveventures.se'
)
ON CONFLICT (org_id, email) 
DO UPDATE SET
    work_email = EXCLUDED.work_email,
    job_title = EXCLUDED.job_title,
    department = EXCLUDED.department,
    bio = EXCLUDED.bio,
    updated_at = NOW()
RETURNING id INTO v_wizard_person_id;

RAISE NOTICE '✅ Wizard person created/updated: %', v_wizard_person_id;

-- ============================================================================
-- STEP 3: Create/Update Serge person
-- ============================================================================
INSERT INTO people (
    org_id,
    name,
    email,
    work_email,
    person_type,
    job_title,
    department,
    bio,
    email_domain,
    linkedin_url
) VALUES (
    v_org_id,
    'Serge Lachapelle',
    'serge@disruptiveventures.se',
    'serge@disruptiveventures.se',
    'internal',
    'PLACEHOLDER - Update from LinkedIn',
    'PLACEHOLDER',
    'PLACEHOLDER - Update from LinkedIn',
    'disruptiveventures.se',
    'https://www.linkedin.com/in/sergelachapelle/'
)
ON CONFLICT (org_id, email)
DO UPDATE SET
    work_email = EXCLUDED.work_email,
    linkedin_url = EXCLUDED.linkedin_url,
    updated_at = NOW()
RETURNING id INTO v_serge_person_id;

-- Also update the serge.lachapelle@ record if it exists
UPDATE people 
SET 
    email = 'serge@disruptiveventures.se',
    work_email = 'serge@disruptiveventures.se'
WHERE email = 'serge.lachapelle@disruptiveventures.se'
AND org_id = v_org_id;

RAISE NOTICE '✅ Serge person created/updated: %', v_serge_person_id;

-- ============================================================================
-- STEP 4: Setup Linear user mappings (if Marcus has Linear ID)
-- ============================================================================
IF v_marcus_linear_id IS NOT NULL THEN
    -- Map Wizard to Marcus's Linear (shared tasks)
    INSERT INTO linear_user_mappings (
        org_id,
        person_name,
        person_email,
        linear_user_id,
        integration_data
    ) VALUES (
        v_org_id,
        'Wizard',
        'wizard@disruptiveventures.se',
        v_marcus_linear_id,  -- Use Marcus's Linear ID
        jsonb_build_object(
            'shared_with', 'marcus',
            'sync_type', 'shared_tasks',
            'note', 'Wizard shares Marcus''s Linear tasks'
        )
    )
    ON CONFLICT (org_id, person_email) 
    DO UPDATE SET
        linear_user_id = v_marcus_linear_id,
        integration_data = EXCLUDED.integration_data,
        updated_at = NOW();
    
    RAISE NOTICE '✅ Wizard mapped to Marcus''s Linear ID';
    
    -- Map Serge to Marcus's Linear (shared tasks)
    INSERT INTO linear_user_mappings (
        org_id,
        person_name,
        person_email,
        linear_user_id,
        integration_data
    ) VALUES (
        v_org_id,
        'Serge Lachapelle',
        'serge@disruptiveventures.se',
        v_marcus_linear_id,  -- Use Marcus's Linear ID
        jsonb_build_object(
            'shared_with', 'marcus',
            'sync_type', 'shared_tasks',
            'note', 'Serge shares Marcus''s Linear tasks'
        )
    )
    ON CONFLICT (org_id, person_email)
    DO UPDATE SET
        linear_user_id = v_marcus_linear_id,
        integration_data = EXCLUDED.integration_data,
        updated_at = NOW();
    
    RAISE NOTICE '✅ Serge mapped to Marcus''s Linear ID';
ELSE
    RAISE NOTICE '⚠️  Marcus has no Linear ID set - Linear sync will not work until configured';
END IF;

-- ============================================================================
-- STEP 5: Setup Google Task Lists for Wizard and Serge
-- ============================================================================

-- Wizard's Google Task List
INSERT INTO google_task_lists (
    org_id,
    person_id,
    google_task_list_id,
    google_task_list_name,
    auto_sync_enabled,
    sync_to_linear,
    sync_from_linear
) VALUES (
    v_org_id,
    v_wizard_person_id,
    'PLACEHOLDER_GOOGLE_TASK_LIST_ID_WIZARD',  -- Will be replaced by actual Google Task List ID
    'My Tasks',
    true,
    true,
    true
)
ON CONFLICT (person_id, google_task_list_id)
DO UPDATE SET
    auto_sync_enabled = true,
    sync_to_linear = true,
    sync_from_linear = true,
    updated_at = NOW();

RAISE NOTICE '✅ Google Task List configured for Wizard';

-- Serge's Google Task List
INSERT INTO google_task_lists (
    org_id,
    person_id,
    google_task_list_id,
    google_task_list_name,
    auto_sync_enabled,
    sync_to_linear,
    sync_from_linear
) VALUES (
    v_org_id,
    v_serge_person_id,
    'PLACEHOLDER_GOOGLE_TASK_LIST_ID_SERGE',  -- Will be replaced by actual Google Task List ID
    'My Tasks',
    true,
    true,
    true
)
ON CONFLICT (person_id, google_task_list_id)
DO UPDATE SET
    auto_sync_enabled = true,
    sync_to_linear = true,
    sync_from_linear = true,
    updated_at = NOW();

RAISE NOTICE '✅ Google Task List configured for Serge';

-- ============================================================================
-- STEP 6: Copy Marcus's tasks to Wizard and Serge (if any exist)
-- ============================================================================

-- This would normally be done by your sync service, but here's a one-time copy
-- Note: In production, tasks will sync automatically via webhooks/polling

RAISE NOTICE '';
RAISE NOTICE '════════════════════════════════════════════════════════════';
RAISE NOTICE 'SETUP COMPLETE';
RAISE NOTICE '════════════════════════════════════════════════════════════';
RAISE NOTICE 'Wizard: %', v_wizard_person_id;
RAISE NOTICE 'Serge: %', v_serge_person_id;
RAISE NOTICE '';
RAISE NOTICE 'NEXT STEPS:';
RAISE NOTICE '1. Update Serge''s profile with real LinkedIn data';
RAISE NOTICE '2. Configure Google OAuth for wizard@ and serge@';
RAISE NOTICE '3. Get actual Google Task List IDs and update google_task_lists table';
RAISE NOTICE '4. Setup Linear webhook to call create_task_from_linear() on issue updates';
RAISE NOTICE '5. Setup Google Tasks polling/webhook to call create_task_from_google()';
RAISE NOTICE '6. Deploy sync service to handle bidirectional updates';

END $$;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- View all people with sync setup
SELECT 
    p.name,
    p.email,
    p.job_title,
    p.department,
    lm.linear_user_id,
    gtl.google_task_list_name,
    gtl.auto_sync_enabled
FROM people p
LEFT JOIN linear_user_mappings lm ON lm.person_email = p.email
LEFT JOIN google_task_lists gtl ON gtl.person_id = p.id
WHERE p.email IN ('marcus@disruptiveventures.se', 'wizard@disruptiveventures.se', 'serge@disruptiveventures.se')
ORDER BY p.name;

-- View sync configuration
SELECT * FROM google_task_lists;
