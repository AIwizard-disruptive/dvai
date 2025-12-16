-- ============================================================================
-- DATABASE VERIFICATION SCRIPT
-- Run this after RESET_DATABASE.sql to verify everything is correct
-- ============================================================================

\echo ''
\echo '🔍 VERIFYING DATABASE SCHEMA'
\echo '============================'
\echo ''

-- ============================================================================
-- 1. CHECK TABLES EXIST
-- ============================================================================

\echo '📋 Checking Tables...'
\echo ''

DO $$ 
DECLARE
    expected_tables TEXT[] := ARRAY[
        'orgs',
        'org_memberships',
        'meeting_groups',
        'meetings',
        'people',
        'meeting_participants',
        'artifacts',
        'transcript_chunks',
        'summaries',
        'action_items',
        'decisions',
        'tags',
        'meeting_tags',
        'entities',
        'meeting_entities',
        'links',
        'processing_runs',
        'external_refs',
        'integrations'
    ];
    actual_count INTEGER;
    missing_tables TEXT[];
    table_name TEXT;
BEGIN
    -- Count actual tables
    SELECT COUNT(*) INTO actual_count
    FROM information_schema.tables
    WHERE table_schema = 'public' 
      AND table_type = 'BASE TABLE';
    
    RAISE NOTICE '✓ Found % tables in public schema', actual_count;
    
    -- Check each expected table
    FOREACH table_name IN ARRAY expected_tables
    LOOP
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' 
              AND table_name = table_name
        ) THEN
            RAISE WARNING '✗ Missing table: %', table_name;
        END IF;
    END LOOP;
END $$;

-- ============================================================================
-- 2. CHECK JUNCTION TABLES HAVE ORG_ID
-- ============================================================================

\echo ''
\echo '🔗 Checking Junction Tables...'
\echo ''

DO $$ 
BEGIN
    -- Check meeting_participants
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'meeting_participants' AND column_name = 'org_id'
    ) THEN
        RAISE WARNING '✗ meeting_participants missing org_id column';
    ELSE
        RAISE NOTICE '✓ meeting_participants has org_id';
    END IF;
    
    -- Check meeting_tags
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'meeting_tags' AND column_name = 'org_id'
    ) THEN
        RAISE WARNING '✗ meeting_tags missing org_id column';
    ELSE
        RAISE NOTICE '✓ meeting_tags has org_id';
    END IF;
    
    -- Check meeting_entities
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'meeting_entities' AND column_name = 'org_id'
    ) THEN
        RAISE WARNING '✗ meeting_entities missing org_id column';
    ELSE
        RAISE NOTICE '✓ meeting_entities has org_id';
    END IF;
END $$;

-- ============================================================================
-- 3. CHECK RLS IS ENABLED
-- ============================================================================

\echo ''
\echo '🔒 Checking Row Level Security...'
\echo ''

DO $$ 
DECLARE
    table_record RECORD;
    rls_enabled_count INTEGER := 0;
BEGIN
    FOR table_record IN 
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
    LOOP
        IF EXISTS (
            SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND c.relname = table_record.tablename
              AND c.relrowsecurity = true
        ) THEN
            rls_enabled_count := rls_enabled_count + 1;
        ELSE
            RAISE WARNING '✗ RLS not enabled on: %', table_record.tablename;
        END IF;
    END LOOP;
    
    RAISE NOTICE '✓ RLS enabled on % tables', rls_enabled_count;
END $$;

-- ============================================================================
-- 4. CHECK POLICIES EXIST
-- ============================================================================

\echo ''
\echo '📜 Checking RLS Policies...'
\echo ''

DO $$ 
DECLARE
    policy_count INTEGER;
    expected_policies TEXT[] := ARRAY[
        'orgs_select',
        'orgs_insert',
        'orgs_update',
        'orgs_delete',
        'org_memberships_select',
        'org_memberships_insert',
        'org_memberships_update',
        'org_memberships_delete',
        'meeting_groups_all',
        'meetings_all',
        'people_all',
        'meeting_participants_all',
        'artifacts_all',
        'transcript_chunks_all',
        'summaries_all',
        'action_items_all',
        'decisions_all',
        'tags_all',
        'meeting_tags_all',
        'entities_all',
        'meeting_entities_all',
        'links_all',
        'processing_runs_all',
        'external_refs_all',
        'integrations_select',
        'integrations_insert',
        'integrations_update',
        'integrations_delete'
    ];
    policy_name TEXT;
BEGIN
    SELECT COUNT(*) INTO policy_count
    FROM pg_policies
    WHERE schemaname = 'public';
    
    RAISE NOTICE '✓ Found % policies total', policy_count;
    
    -- Check critical policies
    FOREACH policy_name IN ARRAY expected_policies
    LOOP
        IF NOT EXISTS (
            SELECT 1 FROM pg_policies
            WHERE schemaname = 'public' AND policyname = policy_name
        ) THEN
            RAISE WARNING '✗ Missing policy: %', policy_name;
        END IF;
    END LOOP;
END $$;

-- ============================================================================
-- 5. CHECK HELPER FUNCTIONS EXIST
-- ============================================================================

\echo ''
\echo '⚙️  Checking Helper Functions...'
\echo ''

DO $$ 
BEGIN
    -- Check user_is_org_member
    IF NOT EXISTS (
        SELECT 1 FROM pg_proc 
        WHERE proname = 'user_is_org_member'
    ) THEN
        RAISE WARNING '✗ Missing function: user_is_org_member';
    ELSE
        RAISE NOTICE '✓ Function exists: user_is_org_member';
    END IF;
    
    -- Check user_can_write_org
    IF NOT EXISTS (
        SELECT 1 FROM pg_proc 
        WHERE proname = 'user_can_write_org'
    ) THEN
        RAISE WARNING '✗ Missing function: user_can_write_org';
    ELSE
        RAISE NOTICE '✓ Function exists: user_can_write_org';
    END IF;
    
    -- Check user_is_org_admin
    IF NOT EXISTS (
        SELECT 1 FROM pg_proc 
        WHERE proname = 'user_is_org_admin'
    ) THEN
        RAISE WARNING '✗ Missing function: user_is_org_admin';
    ELSE
        RAISE NOTICE '✓ Function exists: user_is_org_admin';
    END IF;
    
    -- Check update_updated_at_column
    IF NOT EXISTS (
        SELECT 1 FROM pg_proc 
        WHERE proname = 'update_updated_at_column'
    ) THEN
        RAISE WARNING '✗ Missing function: update_updated_at_column';
    ELSE
        RAISE NOTICE '✓ Function exists: update_updated_at_column';
    END IF;
END $$;

-- ============================================================================
-- 6. CHECK INDEXES EXIST
-- ============================================================================

\echo ''
\echo '📇 Checking Indexes...'
\echo ''

DO $$ 
DECLARE
    index_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE schemaname = 'public';
    
    RAISE NOTICE '✓ Found % indexes', index_count;
    
    -- Check critical indexes on junction tables
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public' 
          AND tablename = 'meeting_participants'
          AND indexname = 'ix_meeting_participants_org_id'
    ) THEN
        RAISE WARNING '✗ Missing index: ix_meeting_participants_org_id';
    ELSE
        RAISE NOTICE '✓ Index exists: ix_meeting_participants_org_id';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public' 
          AND tablename = 'meeting_tags'
          AND indexname = 'ix_meeting_tags_org_id'
    ) THEN
        RAISE WARNING '✗ Missing index: ix_meeting_tags_org_id';
    ELSE
        RAISE NOTICE '✓ Index exists: ix_meeting_tags_org_id';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public' 
          AND tablename = 'meeting_entities'
          AND indexname = 'ix_meeting_entities_org_id'
    ) THEN
        RAISE WARNING '✗ Missing index: ix_meeting_entities_org_id';
    ELSE
        RAISE NOTICE '✓ Index exists: ix_meeting_entities_org_id';
    END IF;
END $$;

-- ============================================================================
-- 7. CHECK TRIGGERS EXIST
-- ============================================================================

\echo ''
\echo '⚡ Checking Triggers...'
\echo ''

DO $$ 
DECLARE
    trigger_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO trigger_count
    FROM pg_trigger t
    JOIN pg_class c ON t.tgrelid = c.oid
    JOIN pg_namespace n ON c.relnamespace = n.oid
    WHERE n.nspname = 'public'
      AND NOT t.tgisinternal;
    
    RAISE NOTICE '✓ Found % triggers', trigger_count;
END $$;

-- ============================================================================
-- 8. DETAILED TABLE LIST
-- ============================================================================

\echo ''
\echo '📊 Table Details:'
\echo ''

SELECT 
    t.table_name,
    COUNT(c.column_name) as column_count,
    (SELECT COUNT(*) FROM pg_policies p WHERE p.tablename = t.table_name) as policy_count,
    (SELECT COUNT(*) FROM pg_indexes i WHERE i.tablename = t.table_name) as index_count
FROM information_schema.tables t
LEFT JOIN information_schema.columns c ON t.table_name = c.table_name AND c.table_schema = 'public'
WHERE t.table_schema = 'public'
  AND t.table_type = 'BASE TABLE'
GROUP BY t.table_name
ORDER BY t.table_name;

-- ============================================================================
-- 9. POLICY LIST
-- ============================================================================

\echo ''
\echo '📋 All Policies:'
\echo ''

SELECT 
    tablename,
    policyname,
    CASE 
        WHEN cmd = 'ALL' THEN '🔓 ALL'
        WHEN cmd = 'SELECT' THEN '👁️  SELECT'
        WHEN cmd = 'INSERT' THEN '➕ INSERT'
        WHEN cmd = 'UPDATE' THEN '✏️  UPDATE'
        WHEN cmd = 'DELETE' THEN '🗑️  DELETE'
    END as operation
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- ============================================================================
-- FINAL SUMMARY
-- ============================================================================

\echo ''
\echo '═══════════════════════════════════════'

DO $$ 
DECLARE
    table_count INTEGER;
    policy_count INTEGER;
    function_count INTEGER;
    issues_found BOOLEAN := false;
BEGIN
    -- Get counts
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    
    SELECT COUNT(*) INTO policy_count
    FROM pg_policies
    WHERE schemaname = 'public';
    
    SELECT COUNT(*) INTO function_count
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname = 'public'
      AND p.proname IN ('user_is_org_member', 'user_can_write_org', 'user_is_org_admin', 'update_updated_at_column');
    
    -- Check for issues
    IF table_count < 19 THEN
        issues_found := true;
    END IF;
    
    IF policy_count < 28 THEN
        issues_found := true;
    END IF;
    
    IF function_count < 4 THEN
        issues_found := true;
    END IF;
    
    -- Check junction tables
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'meeting_participants' AND column_name = 'org_id'
    ) OR NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'meeting_tags' AND column_name = 'org_id'
    ) OR NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'meeting_entities' AND column_name = 'org_id'
    ) THEN
        issues_found := true;
    END IF;
    
    RAISE NOTICE '';
    IF issues_found THEN
        RAISE WARNING '⚠️  VERIFICATION FAILED - Issues found above';
        RAISE NOTICE '';
        RAISE NOTICE 'Run RESET_DATABASE.sql again to fix issues';
    ELSE
        RAISE NOTICE '✅ DATABASE VERIFICATION PASSED';
        RAISE NOTICE '';
        RAISE NOTICE 'Summary:';
        RAISE NOTICE '  • % tables created', table_count;
        RAISE NOTICE '  • % RLS policies active', policy_count;
        RAISE NOTICE '  • % helper functions ready', function_count;
        RAISE NOTICE '';
        RAISE NOTICE '🎉 Database is ready for use!';
    END IF;
END $$;

\echo '═══════════════════════════════════════'
\echo ''




