# 🚀 Quick Start: Reset & Verify Database

## Step 1: Reset Database (Drops Everything & Rebuilds)

### In Supabase SQL Editor:

1. Open **Supabase Dashboard** → **SQL Editor**
2. Copy contents of: `backend/migrations/RESET_DATABASE.sql`
3. Paste and click **Run**
4. Wait for completion (~30 seconds)

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

## Step 2: Verify Everything Is Correct

### In Supabase SQL Editor:

1. Copy contents of: `backend/migrations/VERIFY_DATABASE_SUPABASE.sql`
2. Paste and click **Run**
3. Check the output

Expected result:
```
✅ DATABASE VERIFICATION PASSED

Summary:
  • 19 tables
  • 28 RLS policies
  • 4 helper functions
  • [X] indexes
  • [X] triggers

🎉 Database is ready!
```

---

## What Gets Fixed

### ✅ Tables Created:
- `orgs`, `org_memberships` (organizations & users)
- `meetings`, `meeting_groups`, `people` (core entities)
- `meeting_participants`, `meeting_tags`, `meeting_entities` (junction tables **with org_id**)
- `artifacts`, `transcript_chunks`, `summaries` (content)
- `action_items`, `decisions`, `links`, `tags`, `entities` (intelligence)
- `processing_runs`, `external_refs`, `integrations` (operational)

### ✅ Policies Created:
- `meetings_all`, `action_items_all`, etc. (consistent naming)
- **NOT** `auth read meetings`, `auth write meetings` (old policies removed)

### ✅ Junction Tables Fixed:
- `meeting_participants` now has `org_id` + `created_at`
- `meeting_tags` now has `org_id` + `created_at`
- `meeting_entities` now has `org_id` + `created_at`

---

## Troubleshooting

### If Verification Fails:

1. **Check the warnings** in the output
2. **Run RESET_DATABASE.sql again** - it's safe to re-run
3. **Run VERIFY_DATABASE_SUPABASE.sql again** to confirm

### Common Issues:

**"Missing table: X"**
- Migration didn't complete
- Run RESET_DATABASE.sql again

**"Missing policy: X"**
- Old policies conflicting
- Run RESET_DATABASE.sql again (drops all policies first)

**"Missing org_id column"**
- Should not happen with RESET_DATABASE.sql
- If it does, check you ran the right file (not 001_initial_schema.sql)

---

## Quick Reference

| File | Purpose | Use When |
|------|---------|----------|
| `RESET_DATABASE.sql` | Complete drop & rebuild | First setup or fixing issues |
| `VERIFY_DATABASE_SUPABASE.sql` | Check everything is correct | After reset or when troubleshooting |
| `001_initial_schema.sql` | Reference only | **Don't use** (for new DBs only) |
| `002_production_architecture.sql` | Add Layer 1/2/3 tables | After base schema works (optional) |

---

## Next Steps After Verification Passes

### 1. Create Your First Org (via SQL):

```sql
-- Insert org
INSERT INTO orgs (name, settings)
VALUES ('My Company', '{}')
RETURNING id;

-- Copy the returned ID, then add yourself as owner
-- Get your user_id from: Dashboard → Authentication → Users
INSERT INTO org_memberships (org_id, user_id, role)
VALUES (
  '[ORG-ID-FROM-ABOVE]',
  '[YOUR-AUTH-USER-ID]',
  'owner'
);
```

### 2. Start Backend:

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 3. Test API:

```bash
curl http://localhost:8000/health
```

---

## Files Location

All migrations in: `backend/migrations/`

- ✅ Use: `RESET_DATABASE.sql`
- ✅ Use: `VERIFY_DATABASE_SUPABASE.sql`
- ℹ️ Reference: `001_initial_schema.sql`
- ℹ️ Optional: `002_production_architecture.sql`

---

**Questions?** Check `DATABASE_RESET_INSTRUCTIONS.md` for detailed guide.




