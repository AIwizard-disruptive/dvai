-- ============================================================================
-- DATABASE VERIFICATION SCRIPT (Supabase Compatible)
-- Run this in Supabase SQL Editor after RESET_DATABASE.sql
-- ============================================================================

-- Check all tables, policies, functions, and schema correctness

DO $$ 
DECLARE
    table_count INTEGER;
    policy_count INTEGER;
    function_count INTEGER;
    index_count INTEGER;
    trigger_count INTEGER;
    expected_tables TEXT[] := ARRAY[
        'orgs', 'org_memberships', 'meeting_groups', 'meetings', 'people',
        'meeting_participants', 'artifacts', 'transcript_chunks', 'summaries',
        'action_items', 'decisions', 'tags', 'meeting_tags', 'entities',
        'meeting_entities', 'links', 'processing_runs', 'external_refs', 'integrations'
    ];
    table_name TEXT;
    issues_found BOOLEAN := false;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '🔍 DATABASE VERIFICATION';
    RAISE NOTICE '======================';
    RAISE NOTICE '';
    
    -- ========================================================================
    -- 1. CHECK TABLES
    -- ========================================================================
    
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    
    RAISE NOTICE '📋 TABLES:';
    RAISE NOTICE '  ✓ Found % tables', table_count;
    
    IF table_count < 19 THEN
        RAISE WARNING '  ✗ Expected at least 19 tables!';
        issues_found := true;
    END IF;
    
    -- Check each expected table
    FOREACH table_name IN ARRAY expected_tables
    LOOP
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = table_name
        ) THEN
            RAISE WARNING '  ✗ Missing table: %', table_name;
            issues_found := true;
        END IF;
    END LOOP;
    
    RAISE NOTICE '';
    
    -- ========================================================================
    -- 2. CHECK JUNCTION TABLES HAVE ORG_ID
    -- ========================================================================
    
    RAISE NOTICE '🔗 JUNCTION TABLES:';
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'meeting_participants' AND column_name = 'org_id'
    ) THEN
        RAISE WARNING '  ✗ meeting_participants missing org_id column';
        issues_found := true;
    ELSE
        RAISE NOTICE '  ✓ meeting_participants has org_id';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'meeting_tags' AND column_name = 'org_id'
    ) THEN
        RAISE WARNING '  ✗ meeting_tags missing org_id column';
        issues_found := true;
    ELSE
        RAISE NOTICE '  ✓ meeting_tags has org_id';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'meeting_entities' AND column_name = 'org_id'
    ) THEN
        RAISE WARNING '  ✗ meeting_entities missing org_id column';
        issues_found := true;
    ELSE
        RAISE NOTICE '  ✓ meeting_entities has org_id';
    END IF;
    
    RAISE NOTICE '';
    
    -- ========================================================================
    -- 3. CHECK RLS POLICIES
    -- ========================================================================
    
    SELECT COUNT(*) INTO policy_count
    FROM pg_policies
    WHERE schemaname = 'public';
    
    RAISE NOTICE '🔒 RLS POLICIES:';
    RAISE NOTICE '  ✓ Found % policies', policy_count;
    
    IF policy_count < 28 THEN
        RAISE WARNING '  ✗ Expected at least 28 policies!';
        issues_found := true;
    END IF;
    
    -- Check critical policies
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'meetings_all') THEN
        RAISE WARNING '  ✗ Missing policy: meetings_all';
        issues_found := true;
    ELSE
        RAISE NOTICE '  ✓ Policy exists: meetings_all';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'meeting_participants_all') THEN
        RAISE WARNING '  ✗ Missing policy: meeting_participants_all';
        issues_found := true;
    ELSE
        RAISE NOTICE '  ✓ Policy exists: meeting_participants_all';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'meeting_tags_all') THEN
        RAISE WARNING '  ✗ Missing policy: meeting_tags_all';
        issues_found := true;
    ELSE
        RAISE NOTICE '  ✓ Policy exists: meeting_tags_all';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'meeting_entities_all') THEN
        RAISE WARNING '  ✗ Missing policy: meeting_entities_all';
        issues_found := true;
    ELSE
        RAISE NOTICE '  ✓ Policy exists: meeting_entities_all';
    END IF;
    
    -- Check NO old policies exist
    IF EXISTS (SELECT 1 FROM pg_policies WHERE policyname LIKE 'auth %') THEN
        RAISE WARNING '  ✗ Old "auth" policies still exist - need cleanup!';
        issues_found := true;
    ELSE
        RAISE NOTICE '  ✓ No old "auth" policies found';
    END IF;
    
    RAISE NOTICE '';
    
    -- ========================================================================
    -- 4. CHECK HELPER FUNCTIONS
    -- ========================================================================
    
    SELECT COUNT(*) INTO function_count
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname = 'public'
      AND p.proname IN ('user_is_org_member', 'user_can_write_org', 'user_is_org_admin', 'update_updated_at_column');
    
    RAISE NOTICE '⚙️  HELPER FUNCTIONS:';
    RAISE NOTICE '  ✓ Found % helper functions', function_count;
    
    IF function_count < 4 THEN
        RAISE WARNING '  ✗ Expected 4 helper functions!';
        issues_found := true;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'user_is_org_member') THEN
        RAISE WARNING '  ✗ Missing: user_is_org_member';
        issues_found := true;
    ELSE
        RAISE NOTICE '  ✓ Function: user_is_org_member';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'user_can_write_org') THEN
        RAISE WARNING '  ✗ Missing: user_can_write_org';
        issues_found := true;
    ELSE
        RAISE NOTICE '  ✓ Function: user_can_write_org';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'user_is_org_admin') THEN
        RAISE WARNING '  ✗ Missing: user_is_org_admin';
        issues_found := true;
    ELSE
        RAISE NOTICE '  ✓ Function: user_is_org_admin';
    END IF;
    
    RAISE NOTICE '';
    
    -- ========================================================================
    -- 5. CHECK INDEXES
    -- ========================================================================
    
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE schemaname = 'public';
    
    RAISE NOTICE '📇 INDEXES:';
    RAISE NOTICE '  ✓ Found % indexes', index_count;
    
    -- Critical indexes on junction tables
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'meeting_participants' AND indexname = 'ix_meeting_participants_org_id'
    ) THEN
        RAISE WARNING '  ✗ Missing: ix_meeting_participants_org_id';
        issues_found := true;
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'meeting_tags' AND indexname = 'ix_meeting_tags_org_id'
    ) THEN
        RAISE WARNING '  ✗ Missing: ix_meeting_tags_org_id';
        issues_found := true;
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'meeting_entities' AND indexname = 'ix_meeting_entities_org_id'
    ) THEN
        RAISE WARNING '  ✗ Missing: ix_meeting_entities_org_id';
        issues_found := true;
    END IF;
    
    RAISE NOTICE '';
    
    -- ========================================================================
    -- 6. CHECK TRIGGERS
    -- ========================================================================
    
    SELECT COUNT(*) INTO trigger_count
    FROM pg_trigger t
    JOIN pg_class c ON t.tgrelid = c.oid
    JOIN pg_namespace n ON c.relnamespace = n.oid
    WHERE n.nspname = 'public' AND NOT t.tgisinternal;
    
    RAISE NOTICE '⚡ TRIGGERS:';
    RAISE NOTICE '  ✓ Found % triggers', trigger_count;
    
    RAISE NOTICE '';
    
    -- ========================================================================
    -- FINAL VERDICT
    -- ========================================================================
    
    RAISE NOTICE '═══════════════════════════════════════';
    IF issues_found THEN
        RAISE WARNING '';
        RAISE WARNING '⚠️  VERIFICATION FAILED';
        RAISE WARNING '';
        RAISE WARNING 'Issues found! Run RESET_DATABASE.sql again.';
        RAISE WARNING '';
    ELSE
        RAISE NOTICE '';
        RAISE NOTICE '✅ DATABASE VERIFICATION PASSED';
        RAISE NOTICE '';
        RAISE NOTICE 'Summary:';
        RAISE NOTICE '  • % tables', table_count;
        RAISE NOTICE '  • % RLS policies', policy_count;
        RAISE NOTICE '  • % helper functions', function_count;
        RAISE NOTICE '  • % indexes', index_count;
        RAISE NOTICE '  • % triggers', trigger_count;
        RAISE NOTICE '';
        RAISE NOTICE '🎉 Database is ready!';
        RAISE NOTICE '';
    END IF;
    RAISE NOTICE '═══════════════════════════════════════';
    
END $$;

-- Show detailed table info
SELECT 
    t.table_name,
    COUNT(c.column_name) as columns,
    (SELECT COUNT(*) FROM pg_policies p WHERE p.tablename = t.table_name) as policies,
    (SELECT COUNT(*) FROM pg_indexes i WHERE i.tablename = t.table_name) as indexes
FROM information_schema.tables t
LEFT JOIN information_schema.columns c ON t.table_name = c.table_name AND c.table_schema = 'public'
WHERE t.table_schema = 'public'
  AND t.table_type = 'BASE TABLE'
GROUP BY t.table_name
ORDER BY t.table_name;





