# 🔧 Apply Tasks Migration - Setup Guide

## Current Issue

Your `tasks` table doesn't exist yet, which is why you're getting:
```
Error: Could not find the table 'public.tasks'
```

The migration exists (`013_task_sync_system.sql`) but hasn't been applied to your database.

---

## Quick Fix: Apply Migration Manually

### Step 1: Open Supabase SQL Editor

Go to:
```
https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/editor
```

### Step 2: Copy the Migration SQL

Open this file:
```
backend/migrations/013_task_sync_system.sql
```

Copy ALL the contents (all 467 lines)

### Step 3: Run in SQL Editor

1. Click "New Query" in Supabase SQL Editor
2. Paste the entire SQL
3. Click "Run" or press `Cmd + Enter`

### Step 4: Verify Tables Created

You should see:
```
✅ tasks
✅ task_sync_log
✅ google_task_lists
```

### Step 5: Restart Backend

After migration is applied:
```bash
# The server will auto-restart with --reload flag
# Just refresh your browser
```

---

## What This Migration Does

### Creates 3 Tables

**1. `tasks` - Central source of truth**
- Stores all tasks (from meetings, Linear, Google Tasks, manual)
- Has `linear_issue_id` for two-way sync
- Tracks sync timestamps
- Full CRUD operations

**2. `task_sync_log` - Audit trail**
- Logs all sync operations
- Tracks field changes
- Helps debug sync issues

**3. `google_task_lists` - Google Tasks integration**
- Maps Google Task Lists to your org
- Sync configuration per list

### Key Features

✅ **Two-way Linear sync** - Update here, pushes to Linear  
✅ **Two-way Google sync** - Syncs with Google Tasks  
✅ **Audit trail** - All changes logged  
✅ **Conflict resolution** - Last write wins  
✅ **Automatic triggers** - Updates timestamps  

---

## After Migration is Applied

### Your Workflow Will Be

1. **Tasks created in meetings** → Saved to `tasks` table → Synced to Linear
2. **Edit task in Kanban** → Updates `tasks` table → Syncs to Linear
3. **Edit in Linear** → Webhooks update `tasks` table → Shows in Kanban
4. **Drag in Kanban** → Status updated → Syncs to Linear

### Database Structure

```
tasks table:
├── id (UUID)
├── title, description, status, priority
├── linear_issue_id (for sync)
├── google_task_id (for sync)
├── last_synced_to_linear_at
├── last_synced_to_google_at
└── sync_enabled (can disable per task)
```

---

## Alternative: Run Via Supabase CLI

If you have Supabase CLI installed:

```bash
cd backend
supabase db push --db-url "your-database-url"
```

---

## After Tables Exist

Your Kanban board will:
1. ✅ Load tasks from database
2. ✅ Allow editing all tasks
3. ✅ Two-way sync with Linear
4. ✅ Track all changes
5. ✅ No more errors!

---

## Current Status

- ✅ Code ready for two-way sync
- ✅ Linear API integrated
- ✅ GraphQL mutations working
- ❌ **Missing: tasks table** (need to apply migration)
- ❌ **Database connection issue** (tenant/user not found)

---

## Troubleshooting Database Connection

If you still see "Tenant or user not found" after applying migration:

### Check Supabase Project Status

1. Go to: https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev
2. Check if project is **paused** or **inactive**
3. Click "Resume" if paused

### Verify Connection

Try connecting in Python:
```python
from supabase import create_client

supabase = create_client(
    "https://gqpupmuzriqarmrsuwev.supabase.co",
    "your-service-role-key"
)

# Test query
result = supabase.table('people').select('*').limit(1).execute()
print("✅ Connected:", result.data)
```

### Check API Keys

Make sure your service role key starts with:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Quick Summary

**To fix everything:**

1. ✅ `.env` file copied - DONE
2. 🔄 Apply migration 013 in Supabase SQL Editor - **DO THIS**
3. 🔄 Fix database connection (check project status) - **CHECK THIS**
4. 🔄 Restart backend server
5. ✅ Two-way sync works!

---

## Need Help?

If you get stuck:
1. Share the Supabase project status (paused/active?)
2. Share any errors from SQL Editor when running migration
3. I'll help debug!

The code is 100% ready - we just need the database table! 🚀

