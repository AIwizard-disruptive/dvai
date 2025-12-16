-- DESTRUCTIVE MIGRATION: DROP ALL TABLES AND START FRESH
-- ⚠️  WARNING: This will delete ALL data in your database
-- Only run this if you want to completely reset your database

-- ============================================================================
-- DROP ALL POLICIES
-- ============================================================================

DO $$ 
DECLARE
    r RECORD;
BEGIN
    FOR r IN (
        SELECT schemaname, tablename, policyname
        FROM pg_policies
        WHERE schemaname = 'public'
    ) LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON %I.%I CASCADE', 
            r.policyname, r.schemaname, r.tablename);
        RAISE NOTICE 'Dropped policy %.%', r.tablename, r.policyname;
    END LOOP;
END $$;

-- ============================================================================
-- DROP ALL FUNCTIONS
-- ============================================================================

DROP FUNCTION IF EXISTS user_is_org_member(UUID) CASCADE;
DROP FUNCTION IF EXISTS user_can_write_org(UUID) CASCADE;
DROP FUNCTION IF EXISTS user_is_org_admin(UUID) CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- ============================================================================
-- DROP ALL TABLES (in correct order to handle foreign keys)
-- ============================================================================

-- Drop junction/linking tables first
DROP TABLE IF EXISTS meeting_entities CASCADE;
DROP TABLE IF EXISTS meeting_tags CASCADE;
DROP TABLE IF EXISTS meeting_participants CASCADE;

-- Drop dependent tables
DROP TABLE IF EXISTS links CASCADE;
DROP TABLE IF EXISTS entities CASCADE;
DROP TABLE IF EXISTS tags CASCADE;
DROP TABLE IF EXISTS decisions CASCADE;
DROP TABLE IF EXISTS action_items CASCADE;
DROP TABLE IF EXISTS summaries CASCADE;
DROP TABLE IF EXISTS transcript_chunks CASCADE;
DROP TABLE IF EXISTS artifacts CASCADE;
DROP TABLE IF EXISTS people CASCADE;

-- Drop Layer 1, 2, 3 tables (from 002_production_architecture.sql)
DROP TABLE IF EXISTS intelligence_evidence CASCADE;
DROP TABLE IF EXISTS intelligence_action_items CASCADE;
DROP TABLE IF EXISTS intelligence_decisions CASCADE;
DROP TABLE IF EXISTS intelligence_summaries CASCADE;
DROP TABLE IF EXISTS pii_detected CASCADE;
DROP TABLE IF EXISTS speakers_normalized CASCADE;
DROP TABLE IF EXISTS transcripts_normalized CASCADE;
DROP TABLE IF EXISTS transcripts_raw CASCADE;

-- Drop operational/integration tables
DROP TABLE IF EXISTS external_refs CASCADE;
DROP TABLE IF EXISTS processing_runs CASCADE;
DROP TABLE IF EXISTS integrations CASCADE;

-- Drop meeting tables
DROP TABLE IF EXISTS meetings CASCADE;
DROP TABLE IF EXISTS meeting_groups CASCADE;

-- Drop org tables last
DROP TABLE IF EXISTS org_memberships CASCADE;
DROP TABLE IF EXISTS orgs CASCADE;

-- ============================================================================
-- SUCCESS
-- ============================================================================

DO $$ 
BEGIN
    RAISE NOTICE '✓ All tables, policies, and functions dropped successfully';
    RAISE NOTICE '→ Now run: 001_initial_schema.sql';
END $$;




