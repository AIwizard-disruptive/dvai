# 🔧 Apply Migration 013 in Supabase - Quick Guide

## Current Issue

The `tasks` table structure is incomplete. You need to apply migration `013_task_sync_system.sql` in Supabase.

---

## Steps to Apply (5 minutes)

### 1. Open Supabase SQL Editor

**Link:** https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/editor

Or:
1. Go to https://supabase.com/dashboard
2. Select project: `gqpupmuzriqarmrsuwev`
3. Click "SQL Editor" in left menu

### 2. Open the Migration File

The file you currently have open:
```
backend/migrations/013_task_sync_system.sql
```

### 3. Copy All Contents

- Select all (Cmd + A)
- Copy (Cmd + C)
- All 467 lines

### 4. Paste in Supabase SQL Editor

1. Click "New Query" in Supabase
2. Paste the SQL (Cmd + V)
3. Click "Run" or press Cmd + Enter

### 5. Wait for Completion

You should see:
```
Success! No rows returned
```

Or tables created confirmation.

### 6. Verify Tables

Run this query in SQL Editor to verify:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('tasks', 'task_sync_log', 'google_task_lists');
```

Should return 3 rows.

---

## What This Does

Creates 3 tables:
- ✅ `tasks` - Store all tasks with Linear sync
- ✅ `task_sync_log` - Audit trail
- ✅ `google_task_lists` - Google Tasks integration

Plus:
- Indexes for performance
- RLS policies for security
- Triggers for auto-updating timestamps
- Helper functions for sync

---

## After Migration Applied

1. **Refresh** your Kanban page
2. **Click "Sync Now"** button
3. **Tasks sync** from Linear to database
4. **Edit any task** → Saves to database + syncs to Linear
5. **No more 404 errors!**

---

## Quick Test After

Try clicking a task and editing it - should work perfectly! ✅

---

**Let me know when you've run it and I'll help verify it worked!** 🚀

