-- ============================================================================
-- 4-WHEEL VC OPERATING SYSTEM - COMPLETE MIGRATION
-- ============================================================================
--
-- INSTRUCTIONS:
-- 1. Open Supabase SQL Editor
-- 2. Copy the ENTIRE contents of FINAL_4_WHEELS_COMPLETE.sql
-- 3. Paste and click "Run"
--
-- This single file includes ALL 4 wheels:
-- - PEOPLE: Recruitment, contracts, competencies, Google integration
-- - DEALFLOW: Lead qualification, research, outreach
-- - BUILDING COMPANIES: Targets, CEO dashboards, qualification tracking
-- - ADMIN: DV dashboards, alerts, portfolio metrics
--
-- Features:
-- ✅ LinkedIn integration (auto-generate CVs from LinkedIn)
-- ✅ Google Workspace Directory sync (employee profiles)
-- ✅ Google Contacts CRM (all contacts in Gmail)
-- ✅ Employment contract management
-- ✅ Full RLS policies for Supabase
-- ✅ Helper functions for automation
-- ✅ Zero conflicts with existing migrations (001-008)
--
-- Tables Created: 18 new tables + 2 materialized views
-- Helper Functions: 4 functions for LinkedIn, Google sync, contracts
--
-- ============================================================================

-- First, verify we're connected to the right database
SELECT current_database() as database_name;

-- Check if required tables exist (from previous migrations)
SELECT 
    COUNT(*) as existing_tables_count,
    string_agg(table_name, ', ') as tables
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('orgs', 'people', 'organizations', 'meetings');

-- If you see 4 tables above, you're good to proceed!
-- Now run: FINAL_4_WHEELS_COMPLETE.sql

