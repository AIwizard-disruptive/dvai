-- ============================================================================
-- RUN NEW MIGRATIONS (009-012) - PURE SQL VERSION
-- Safe execution of new 4-wheel migrations
-- ============================================================================

-- This script runs migrations 009-012 for the 4-wheel VC operating system
-- It's safe to run multiple times (uses IF NOT EXISTS)

-- Note: Run these migrations in order from your SQL client or via:
-- psql $DATABASE_URL -f 009_people_wheel.sql
-- psql $DATABASE_URL -f 010_dealflow_wheel.sql
-- psql $DATABASE_URL -f 011_building_companies_wheel.sql
-- psql $DATABASE_URL -f 012_admin_wheel.sql

-- Or copy the contents of each file and run them individually

SELECT 'To run migrations, execute each migration file in order:' AS instructions;
SELECT '1. migrations/009_people_wheel.sql' AS step_1;
SELECT '2. migrations/010_dealflow_wheel.sql' AS step_2;
SELECT '3. migrations/011_building_companies_wheel.sql' AS step_3;
SELECT '4. migrations/012_admin_wheel.sql' AS step_4;
