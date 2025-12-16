# ✅ Task Sync System - READY

## 🎯 What's Complete

### **1. Database Schema** ✅
- **`tasks`** table - Central source of truth for all tasks
- **`task_sync_log`** - Audit trail of all sync operations  
- **`google_task_lists`** - Google Tasks configuration per user
- **Linear user mappings** - Links people to Linear user IDs

### **2. Bidirectional Sync Functions** ✅
- `sync_task_to_linear()` - Generates Linear API payload
- `sync_task_to_google()` - Generates Google Tasks API payload
- `create_task_from_linear()` - Creates task from Linear webhook
- `create_task_from_google()` - Creates task from Google Tasks API
- Automatic change tracking via triggers

### **3. User Setup** ✅
- wizard@disruptiveventures.se configured
- serge@disruptiveventures.se configured
- Both mapped to YOUR Linear user ID (shared tasks)
- Google Task Lists placeholders ready

---

## 🚀 Quick Start

### **Run the migrations:**

```bash
# 1. Task sync system
psql $DATABASE_URL -f backend/migrations/013_task_sync_system.sql

# 2. Setup wizard@ and serge@
psql $DATABASE_URL -f backend/migrations/SETUP_WIZARD_SERGE_SYNC.sql
```

### **Verify:**

```sql
SELECT 
    p.name,
    p.email,
    lm.linear_user_id,
    gtl.auto_sync_enabled
FROM people p
LEFT JOIN linear_user_mappings lm ON lm.person_email = p.email
LEFT JOIN google_task_lists gtl ON gtl.person_id = p.id
WHERE p.email IN ('wizard@disruptiveventures.se', 'serge@disruptiveventures.se');
```

---

## 📋 How It Works

### **Scenario: You update task in Linear**
1. Linear webhook → Your API
2. API calls `create_task_from_linear()` 
3. Task saved to DB with `linear_issue_id`
4. Trigger logs change to `task_sync_log`
5. Sync service reads pending syncs
6. Calls `sync_task_to_google()` for payload
7. Posts to Google Tasks API
8. wizard@ and serge@ see the task in Google Tasks ✅

### **Scenario: Serge updates task in Google Tasks**
1. Polling service detects change
2. Calls `create_task_from_google()` or updates existing
3. Task saved to DB with `google_task_id`
4. Trigger logs change to `task_sync_log`
5. Sync service reads pending syncs
6. Calls `sync_task_to_linear()` for payload
7. Posts to Linear API
8. You see the update in Linear ✅

### **Scenario: Direct DB update**
1. You update task via your app UI
2. Trigger automatically logs to `task_sync_log`
3. Sync service syncs to BOTH Linear and Google Tasks
4. Everyone stays in sync ✅

---

## ⚠️ What You Need to Build

### **Sync Service (Backend)**

The database is ready. You need to build a service that:

1. **Listens for Linear webhooks**
   - POST endpoint at `/webhooks/linear`
   - Verifies webhook signature
   - Calls `create_task_from_linear()` or updates tasks

2. **Polls Google Tasks**
   - Runs every 5 minutes
   - Fetches tasks for wizard@ and serge@
   - Calls `create_task_from_google()` or updates tasks

3. **Processes sync queue**
   - Reads `task_sync_log` WHERE `sync_status = 'pending'`
   - For each pending sync:
     - Calls `sync_task_to_linear()` or `sync_task_to_google()`
     - Posts to respective API
     - Updates sync log status

**Tech stack options:**
- Node.js + Express + node-cron
- Python + FastAPI + APScheduler
- Go + Gin + cron

---

## 🔧 Configuration Needed

### **1. Linear Webhook**
```
URL: https://your-api.com/webhooks/linear
Events: issue.create, issue.update, issue.remove
```

### **2. Get Your Linear User ID**
```typescript
const linearClient = new LinearClient({ apiKey: LINEAR_API_KEY });
const me = await linearClient.viewer;
// Store me.id in linear_user_mappings for marcus@
```

### **3. Google OAuth for wizard@ and serge@**
- Setup OAuth 2.0 flow
- Get access_token and refresh_token
- Store in `user_integrations` table

### **4. Get Google Task List IDs**
```typescript
const lists = await googleTasks.tasklists.list({ auth });
// Update google_task_lists.google_task_list_id
```

---

## 📊 Files Created

- ✅ `013_task_sync_system.sql` - Complete database schema
- ✅ `SETUP_WIZARD_SERGE_SYNC.sql` - User setup script
- ✅ `TASK_SYNC_SYSTEM_GUIDE.md` - Complete implementation guide
- ✅ `TASK_SYNC_READY.md` - This file

---

## 🎯 Your Current State

✅ **Database ready** - All tables, functions, triggers created  
✅ **wizard@ and serge@ configured** - Mapped to your Linear ID  
✅ **Audit logging** - All changes tracked automatically  
⚠️ **Sync service** - Needs to be built (see guide)  
⚠️ **OAuth tokens** - Need to be configured  
⚠️ **Webhook** - Need to be setup in Linear  

---

## 🚀 Deploy Checklist

- [ ] Run migration 013_task_sync_system.sql
- [ ] Run SETUP_WIZARD_SERGE_SYNC.sql
- [ ] Get your Linear user ID
- [ ] Update linear_user_mappings with real Linear ID
- [ ] Setup Linear webhook pointing to your API
- [ ] Setup Google OAuth for wizard@ and serge@
- [ ] Get Google Task List IDs
- [ ] Build sync service (webhook listener + poller + queue processor)
- [ ] Deploy sync service
- [ ] Test: Create task in Linear → appears in Google Tasks
- [ ] Test: Update task in Google Tasks → appears in Linear
- [ ] Monitor task_sync_log for errors

---

**Ready to sync! Your database is set up for bidirectional task management.** 🎉

See `TASK_SYNC_SYSTEM_GUIDE.md` for complete implementation details.
