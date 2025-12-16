-- ============================================================================
-- VERIFY 4-WHEEL MIGRATIONS - Run this AFTER migrations
-- ============================================================================

-- Check all new tables were created
SELECT 
    'PEOPLE WHEEL' as wheel,
    COUNT(*) as tables_created
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'contracts',
    'role_descriptions',
    'recruitment_candidates',
    'recruitment_notes',
    'person_competencies',
    'person_cvs',
    'google_profile_syncs',
    'google_contacts_syncs'
)

UNION ALL

SELECT 
    'DEALFLOW WHEEL' as wheel,
    COUNT(*) as tables_created
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'dealflow_leads',
    'dealflow_research',
    'market_analyses',
    'dealflow_outreach'
)

UNION ALL

SELECT 
    'BUILDING COMPANIES WHEEL' as wheel,
    COUNT(*) as tables_created
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'portfolio_companies',
    'portfolio_targets',
    'target_updates',
    'qualification_criteria',
    'ceo_dashboard_configs',
    'portfolio_support_requests'
)

UNION ALL

SELECT 
    'ADMIN WHEEL' as wheel,
    COUNT(*) as tables_created
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'dv_dashboard_configs',
    'dv_alerts'
);

-- Expected results:
-- PEOPLE WHEEL: 8 tables
-- DEALFLOW WHEEL: 4 tables
-- BUILDING COMPANIES WHEEL: 6 tables
-- ADMIN WHEEL: 2 tables
-- Total: 20 tables

-- Check materialized views
SELECT 
    'MATERIALIZED VIEWS' as type,
    COUNT(*) as count
FROM pg_matviews 
WHERE matviewname IN ('dv_portfolio_health', 'dv_dealflow_metrics');

-- Expected: 2 materialized views

-- Check helper functions
SELECT 
    'HELPER FUNCTIONS' as type,
    COUNT(*) as count
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'public'
AND p.proname IN (
    'populate_email_domain',
    'update_person_from_linkedin',
    'sync_person_to_google_directory',
    'link_person_to_contract',
    'generate_cv_from_linkedin'
);

-- Expected: 5 functions

-- Check new columns added to people table
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'people'
AND column_name IN (
    'work_email',
    'email_domain',
    'employee_number',
    'employment_contract_id',
    'google_workspace_id',
    'google_directory_synced_at'
)
ORDER BY column_name;

-- Expected: 6 new columns

-- Check RLS policies
SELECT 
    schemaname,
    tablename,
    policyname
FROM pg_policies
WHERE tablename IN (
    'contracts',
    'role_descriptions',
    'recruitment_candidates',
    'dealflow_leads',
    'portfolio_companies',
    'dv_alerts'
)
ORDER BY tablename, policyname;

-- Summary query
SELECT 
    '✅ MIGRATION VERIFICATION COMPLETE' as status,
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('contracts', 'dealflow_leads', 'portfolio_companies', 'dv_alerts')) as critical_tables,
    (SELECT COUNT(*) FROM pg_matviews WHERE matviewname IN ('dv_portfolio_health', 'dv_dealflow_metrics')) as materialized_views,
    (SELECT COUNT(*) FROM pg_proc p JOIN pg_namespace n ON p.pronamespace = n.oid WHERE n.nspname = 'public' AND p.proname IN ('generate_cv_from_linkedin', 'sync_person_to_google_directory')) as helper_functions;

-- If critical_tables = 4, materialized_views = 2, helper_functions = 2, you're good! ✅

