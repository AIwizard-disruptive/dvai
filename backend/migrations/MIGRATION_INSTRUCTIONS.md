# How to Run New Migrations (009-012)

## Option 1: Using Your SQL Query Tool (Easiest)

Since you're already using a SQL query tool, run each migration file **one at a time**:

### Step 1: Run Migration 009 (PEOPLE Wheel)
1. Open `009_people_wheel.sql` in your SQL query tool
2. Execute the entire file
3. **If you get "already exists" errors**, that's OK - it means some objects are already there

### Step 2: Run Migration 010 (DEALFLOW Wheel)
1. Open `010_dealflow_wheel.sql`
2. Execute the entire file

### Step 3: Run Migration 011 (BUILDING COMPANIES Wheel)
1. Open `011_building_companies_wheel.sql`
2. Execute the entire file

### Step 4: Run Migration 012 (ADMIN Wheel)
1. Open `012_admin_wheel.sql`
2. Execute the entire file

**That's it!** All 4 wheels will be set up.

---

## Option 2: Using Supabase SQL Editor (Recommended if using Supabase)

1. Go to https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/editor
2. Click "New Query"
3. Copy contents of `009_people_wheel.sql`
4. Click "Run"
5. Repeat for 010, 011, 012

---

## Option 3: Install PostgreSQL Client

If you want to use psql:

```bash
# macOS
brew install postgresql

# Then run migrations
cd backend/migrations
export DATABASE_URL="postgresql://postgres.gqpupmuzriqarmrsuwev:siQfof-byvhe8-foxfyf@aws-0-us-east-1.pooler.supabase.com:5432/postgres"
./run_new_migrations.sh
```

---

## Option 4: Set Up Python Environment

If you want to use the Python script:

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python3 run_new_migrations.py
```

---

## Common Errors (Safe to Ignore)

### ✅ "policy already exists"
**Cause**: Migration 008 already ran  
**Solution**: Ignore - the new migrations don't conflict

### ✅ "relation already exists"
**Cause**: Running migrations multiple times  
**Solution**: Ignore - all migrations use `IF NOT EXISTS`

---

## Verify Migrations Succeeded

After running, check if new tables exist:

```sql
-- Check PEOPLE wheel tables
SELECT table_name FROM information_schema.tables 
WHERE table_name IN ('hr_policies', 'contracts', 'role_descriptions', 'recruitment_candidates', 'person_competencies', 'person_cvs');

-- Check DEALFLOW wheel tables
SELECT table_name FROM information_schema.tables 
WHERE table_name IN ('dealflow_leads', 'dealflow_research', 'market_analyses', 'dealflow_outreach');

-- Check BUILDING wheel tables
SELECT table_name FROM information_schema.tables 
WHERE table_name IN ('portfolio_companies', 'portfolio_targets', 'qualification_criteria', 'ceo_dashboard_configs');

-- Check ADMIN wheel tables
SELECT table_name FROM information_schema.tables 
WHERE table_name IN ('dv_dashboard_configs', 'dv_alerts');

-- Check materialized views
SELECT matviewname FROM pg_matviews 
WHERE matviewname IN ('dv_portfolio_health', 'dv_dealflow_metrics');
```

Expected result: All table names should appear.

---

## What Gets Created

**Total: 29 new tables + 2 materialized views + 31 new tables**

- 10 PEOPLE wheel tables
- 4 DEALFLOW wheel tables
- 5 BUILDING COMPANIES wheel tables
- 2 ADMIN wheel tables
- 2 materialized views
- Plus indexes, triggers, and functions

**File locations**:
- `migrations/009_people_wheel.sql` - 383 lines
- `migrations/010_dealflow_wheel.sql` - 261 lines
- `migrations/011_building_companies_wheel.sql` - 283 lines
- `migrations/012_admin_wheel.sql` - 175 lines

---

## Need Help?

If you encounter errors other than "already exists":
1. Check the error message
2. See which table/policy is causing the issue
3. You can skip that specific CREATE statement if it exists
4. Continue with the rest of the migration

The migrations are designed to be **idempotent** (safe to run multiple times).
