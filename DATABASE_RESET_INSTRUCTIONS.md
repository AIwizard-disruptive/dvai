# 🔥 Database Reset Instructions

## Overview

This guide will help you **completely reset your database** and rebuild it from scratch with the correct schema.

⚠️ **WARNING**: This will **DELETE ALL DATA** in your database!

---

## What Was Fixed

### Problems Identified:
1. **Missing `org_id` columns** on junction tables (`meeting_participants`, `meeting_tags`, `meeting_entities`)
2. **Old conflicting RLS policies** (`auth read meetings`, etc.)
3. **Schema inconsistencies** between migrations

### Solution:
- Created `RESET_DATABASE.sql` that:
  - Drops all existing tables, policies, and functions
  - Rebuilds the complete schema from scratch
  - Adds `org_id` to ALL junction tables
  - Creates consistent RLS policies using helper functions
  - Enables proper multi-tenant isolation

---

## Prerequisites

1. **Supabase Database Connection String**
   - Get from: Supabase Dashboard → Project Settings → Database → Connection String (URI)
   - Format: `postgresql://postgres.[YOUR-PROJECT-REF].supabase.co:5432/postgres`

2. **Environment File**
   - Create `backend/.env` if it doesn't exist
   - Add your connection string

---

## Option 1: Using the Bash Script (Recommended)

### Step 1: Setup Environment Variables

Create or update `backend/.env`:

```bash
# Supabase Database
SUPABASE_DB_URL=postgresql://postgres.[YOUR-PROJECT-REF].supabase.co:5432/postgres?password=[YOUR-PASSWORD]
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key

# JWT Secret (from Supabase Dashboard → API Settings)
JWT_SECRET=your-jwt-secret

# Other config...
```

### Step 2: Run the Reset Script

```bash
# From project root
./reset_and_rebuild_database.sh
```

The script will:
1. Ask for confirmation (type `yes`)
2. Load your `.env` file
3. Drop all tables
4. Rebuild the schema
5. Show success message

---

## Option 2: Using Supabase SQL Editor

### Step 1: Open Supabase Dashboard
1. Go to your Supabase project
2. Click **SQL Editor** in the sidebar

### Step 2: Copy and Run Migration
1. Open `backend/migrations/RESET_DATABASE.sql`
2. Copy the entire contents
3. Paste into SQL Editor
4. Click **Run**

### Step 3: Verify Success
You should see:
```
✅ DATABASE RESET COMPLETE
✓ All old data deleted
✓ Fresh schema created
✓ 19 tables created
✓ RLS policies enabled

→ Ready for data import
```

---

## Option 3: Using psql Command

```bash
cd "/Users/marcus/Library/Mobile Documents/com~apple~CloudDocs/Documents/Cursor-projects/Disruptive Ventures/DV Legacy/dv"

psql "postgresql://postgres.[YOUR-PROJECT-REF].supabase.co:5432/postgres?password=[YOUR-PASSWORD]" \
  -f backend/migrations/RESET_DATABASE.sql
```

---

## Verify the Schema

After reset, verify with this SQL:

```sql
-- Check tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Check meeting_participants has org_id
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'meeting_participants'
ORDER BY ordinal_position;

-- Check policies
SELECT tablename, policyname
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename = 'meetings'
ORDER BY tablename, policyname;
```

Expected results:
- **19 tables** created
- `meeting_participants` has `org_id` column
- Policies are named: `meetings_all`, `action_items_all`, etc. (not `auth read meetings`)

---

## What Tables Are Created

### Core Tables (9):
- `orgs` - Organizations
- `org_memberships` - User→Org relationships with roles
- `meetings` - Meeting records
- `meeting_groups` - Meeting collections
- `people` - Contact directory
- `artifacts` - Uploaded files
- `transcript_chunks` - Transcript segments
- `summaries` - Meeting summaries
- `processing_runs` - Processing job tracking

### Intelligence Tables (3):
- `action_items` - Extracted action items
- `decisions` - Key decisions
- `links` - Referenced URLs

### Metadata Tables (4):
- `tags` - Custom tags
- `entities` - Named entities (companies, products)
- `meeting_tags` - Meeting↔Tag junction
- `meeting_entities` - Meeting↔Entity junction

### Junction Tables (1):
- `meeting_participants` - Meeting↔People junction

### Integration Tables (2):
- `integrations` - External integrations config
- `external_refs` - Sync mappings

---

## Next Steps After Reset

### 1. Create Your First Org

Use the API or SQL:

```sql
-- Insert an org
INSERT INTO orgs (name, settings)
VALUES ('My Company', '{}')
RETURNING id;

-- Add yourself as owner (replace with your auth.users.id)
INSERT INTO org_memberships (org_id, user_id, role)
VALUES (
  'YOUR-ORG-ID-FROM-ABOVE',
  'YOUR-USER-ID',  -- From auth.users table
  'owner'
);
```

### 2. Test RLS Policies

```sql
-- Set your user context (testing RLS)
SELECT set_config('request.jwt.claims', 
  json_build_object('sub', 'YOUR-USER-ID')::text, 
  true);

-- You should see your org
SELECT * FROM orgs;

-- You should be able to insert meetings
INSERT INTO meetings (org_id, title, meeting_date)
VALUES ('YOUR-ORG-ID', 'Test Meeting', '2024-01-01');
```

### 3. Start Your Backend

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload --port 8000
```

### 4. Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Create a meeting (requires auth token)
curl -X POST http://localhost:8000/api/meetings \
  -H "Authorization: Bearer YOUR-TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Meeting",
    "meeting_date": "2024-01-15"
  }'
```

---

## Troubleshooting

### Error: "role 'postgres' does not exist"
- Use your Supabase connection string, not a local PostgreSQL
- Make sure password is URL-encoded if it contains special characters

### Error: "permission denied for schema public"
- Use the **service_role** connection string (has elevated privileges)
- Or run via Supabase SQL Editor (runs as postgres)

### Error: "column 'org_id' does not exist" (after reset)
- This should NOT happen with the reset script
- If it does, the migration didn't complete
- Check Supabase logs for errors during execution

### Want to Add Layer 2/3 Tables Later?
After the base schema is working, run:
```bash
psql "$SUPABASE_DB_URL" -f backend/migrations/002_production_architecture.sql
```

---

## Migration File Reference

| File | Purpose |
|------|---------|
| `000_drop_all_tables.sql` | Drop all tables (standalone) |
| `001_initial_schema.sql` | Base schema (reference, not for existing DBs) |
| `002_production_architecture.sql` | Layer 1/2/3 + GDPR tables |
| `003_fix_junction_tables.sql` | Alter existing DB (not needed after reset) |
| **`RESET_DATABASE.sql`** | **Complete reset + rebuild (USE THIS)** |

---

## Questions?

If you encounter issues:
1. Check Supabase logs (Dashboard → Logs)
2. Verify your connection string is correct
3. Ensure you're using the service_role key for migrations
4. Run the verification SQL above to check schema state

---

**Ready to reset?** Run `./reset_and_rebuild_database.sh` from the project root!



