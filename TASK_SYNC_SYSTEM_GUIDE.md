-- ============================================================================
-- COMPLETE TASK SYNC SYSTEM GUIDE
-- Linear ↔ Database ↔ Google Tasks Bidirectional Sync
-- ============================================================================

## 🎯 **Overview**

Your task sync system enables:
- ✅ **Bidirectional sync** between Linear, your database, and Google Tasks
- ✅ **Shared tasks** - wizard@ and serge@ see the same Linear tasks as you
- ✅ **Google Tasks sync** - Update in Google Tasks → syncs to Linear and DB
- ✅ **Status tracking** - Change status anywhere, updates everywhere
- ✅ **Audit log** - Full history of all sync events

---

## 📊 **Architecture**

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│   Linear    │◄────────┤  Database    │────────►│ Google Tasks │
│   (Issues)  │         │   (tasks)    │         │              │
└─────────────┘         └──────────────┘         └──────────────┘
      ▲                        │                        ▲
      │                        ▼                        │
      │                  ┌──────────┐                   │
      └──────────────────│ Webhooks │───────────────────┘
                         │ & Polling│
                         └──────────┘
```

---

## 🗄️ **Database Schema**

### **1. `tasks` - Central Source of Truth**

```sql
- id: UUID
- org_id: UUID
- assigned_to_person_id: UUID
- title: TEXT
- description: TEXT
- status: 'todo', 'in_progress', 'done', 'cancelled'
- priority: 'low', 'medium', 'high', 'urgent'
- due_date: DATE
- linear_issue_id: TEXT (unique)
- google_task_id: TEXT (unique)
- sync_enabled: BOOLEAN
- last_synced_to_linear_at: TIMESTAMPTZ
- last_synced_to_google_at: TIMESTAMPTZ
```

### **2. `task_sync_log` - Audit Trail**

Tracks every sync operation with:
- What changed
- Direction (to/from Linear/Google)
- Success/failure status
- Error messages
- Retry count

### **3. `google_task_lists` - Google Tasks Configuration**

- Links people to their Google Task Lists
- Controls sync direction and auto-sync settings

### **4. `linear_user_mappings` - Linear User Assignment**

- Maps people to Linear user IDs
- wizard@ and serge@ both map to YOUR Linear ID
- Ensures shared task visibility

---

## 🚀 **Quick Start**

### **Step 1: Run Migrations**

```bash
# Run the task sync system migration
psql $DATABASE_URL -f backend/migrations/013_task_sync_system.sql

# Setup wizard@ and serge@ profiles
psql $DATABASE_URL -f backend/migrations/SETUP_WIZARD_SERGE_SYNC.sql
```

### **Step 2: Verify Setup**

```sql
-- Check people and mappings
SELECT 
    p.name,
    p.email,
    lm.linear_user_id,
    gtl.auto_sync_enabled
FROM people p
LEFT JOIN linear_user_mappings lm ON lm.person_email = p.email
LEFT JOIN google_task_lists gtl ON gtl.person_id = p.id
WHERE p.email IN ('wizard@disruptiveventures.se', 'serge@disruptiveventures.se')
ORDER BY p.name;
```

---

## 🔄 **Bidirectional Sync Flow**

### **Scenario 1: Linear → Database → Google Tasks**

1. **You update a task in Linear** (change status to "Done")
2. **Linear webhook** calls your API endpoint
3. **API** calls `create_task_from_linear()` or updates existing task
4. **Trigger** logs the change in `task_sync_log`
5. **Sync service** reads pending sync logs
6. **Service** calls `sync_task_to_google()` to get Google API payload
7. **Service** posts update to Google Tasks API
8. **Updates** `last_synced_to_google_at` timestamp

### **Scenario 2: Google Tasks → Database → Linear**

1. **Serge updates task in Google Tasks** (marks as complete)
2. **Polling service** detects change (Google Tasks has no webhooks)
3. **Service** calls `create_task_from_google()` or updates existing task
4. **Trigger** logs the change in `task_sync_log`
5. **Service** calls `sync_task_to_linear()` to get Linear API payload
6. **Service** posts update to Linear API
7. **Updates** `last_synced_to_linear_at` timestamp

### **Scenario 3: Database Direct Update**

1. **User updates task directly in your app**
2. **Trigger** `log_task_changes()` fires automatically
3. **Creates** sync log entry with status 'pending'
4. **Sync service** picks up pending changes
5. **Syncs** to both Linear and Google Tasks

---

## 🛠️ **Implementation**

### **Backend Sync Service (Node.js/Python)**

You need to build a sync service that:

#### **A) Listens for Linear Webhooks**

```typescript
// Example: Express.js webhook endpoint
app.post('/webhooks/linear', async (req, res) => {
  const { action, data } = req.body;
  
  if (action === 'create' || action === 'update') {
    const linearIssue = data;
    
    // Check if task exists in DB
    const existingTask = await db.query(
      'SELECT id FROM tasks WHERE linear_issue_id = $1',
      [linearIssue.id]
    );
    
    if (existingTask) {
      // Update existing task
      await db.query(`
        UPDATE tasks
        SET 
          title = $1,
          description = $2,
          status = $3,
          updated_at = NOW()
        WHERE linear_issue_id = $4
      `, [linearIssue.title, linearIssue.description, mapStatus(linearIssue.state), linearIssue.id]);
    } else {
      // Create new task
      await db.query(
        'SELECT create_task_from_linear($1, $2, $3)',
        [orgId, linearIssue.id, JSON.stringify(linearIssue)]
      );
    }
  }
  
  res.sendStatus(200);
});
```

#### **B) Polls Google Tasks**

```typescript
// Polling service (runs every 5 minutes)
async function syncGoogleTasks() {
  // Get all Google Task Lists to sync
  const taskLists = await db.query(`
    SELECT * FROM google_task_lists
    WHERE auto_sync_enabled = true
  `);
  
  for (const list of taskLists) {
    // Get person's Google OAuth token
    const integration = await db.query(`
      SELECT access_token FROM user_integrations
      WHERE person_id = $1 AND integration_type = 'google'
    `, [list.person_id]);
    
    if (!integration) continue;
    
    // Fetch tasks from Google Tasks API
    const googleTasks = await fetchGoogleTasks(
      integration.access_token,
      list.google_task_list_id
    );
    
    for (const googleTask of googleTasks) {
      // Check if exists in DB
      const dbTask = await db.query(
        'SELECT * FROM tasks WHERE google_task_id = $1',
        [googleTask.id]
      );
      
      if (dbTask && hasChanged(dbTask, googleTask)) {
        // Update from Google
        await updateTaskFromGoogle(dbTask.id, googleTask);
      } else if (!dbTask) {
        // Create new task
        await db.query(
          'SELECT create_task_from_google($1, $2, $3, $4)',
          [list.org_id, list.person_id, googleTask.id, JSON.stringify(googleTask)]
        );
      }
    }
  }
}

// Run every 5 minutes
setInterval(syncGoogleTasks, 5 * 60 * 1000);
```

#### **C) Processes Sync Log Queue**

```typescript
// Sync service (runs continuously)
async function processSyncQueue() {
  // Get pending sync log entries
  const pendingSync = await db.query(`
    SELECT * FROM task_sync_log
    WHERE sync_status = 'pending'
    AND retry_count < 3
    ORDER BY created_at ASC
    LIMIT 10
  `);
  
  for (const log of pendingSync) {
    try {
      if (log.sync_direction === 'to_linear') {
        // Sync to Linear
        const payload = await db.query(
          'SELECT sync_task_to_linear($1)',
          [log.task_id]
        );
        
        await linearApi.updateIssue(log.linear_issue_id, payload);
        
        await db.query(`
          UPDATE task_sync_log
          SET sync_status = 'success', synced_at = NOW()
          WHERE id = $1
        `, [log.id]);
      } else if (log.sync_direction === 'to_google') {
        // Sync to Google
        const payload = await db.query(
          'SELECT sync_task_to_google($1)',
          [log.task_id]
        );
        
        await googleTasksApi.updateTask(log.google_task_id, payload);
        
        await db.query(`
          UPDATE task_sync_log
          SET sync_status = 'success', synced_at = NOW()
          WHERE id = $1
        `, [log.id]);
      }
    } catch (error) {
      // Log error and increment retry count
      await db.query(`
        UPDATE task_sync_log
        SET 
          sync_status = 'failed',
          error_message = $1,
          retry_count = retry_count + 1
        WHERE id = $2
      `, [error.message, log.id]);
    }
  }
}

// Run every 30 seconds
setInterval(processSyncQueue, 30 * 1000);
```

---

## 🔧 **Configuration Steps**

### **1. Setup Linear Webhook**

```bash
# In Linear settings:
# 1. Go to Settings → API → Webhooks
# 2. Create new webhook
# 3. URL: https://your-api.com/webhooks/linear
# 4. Events: issue.create, issue.update, issue.remove
# 5. Copy webhook secret for signature verification
```

### **2. Get Linear User IDs**

```typescript
// Fetch your Linear user ID
const linearClient = new LinearClient({ apiKey: LINEAR_API_KEY });
const me = await linearClient.viewer;
console.log('My Linear ID:', me.id);

// Store in database
await db.query(`
  INSERT INTO linear_user_mappings (org_id, person_name, person_email, linear_user_id)
  VALUES ($1, $2, $3, $4)
  ON CONFLICT (org_id, person_email) DO UPDATE SET linear_user_id = $4
`, [orgId, 'Marcus', 'marcus@disruptiveventures.se', me.id]);
```

### **3. Setup Google OAuth for wizard@ and serge@**

```typescript
// Get Google OAuth tokens for each user
const wizardAuth = await getGoogleOAuth('wizard@disruptiveventures.se');
const sergeAuth = await getGoogleOAuth('serge@disruptiveventures.se');

// Store in user_integrations
await db.query(`
  INSERT INTO user_integrations (user_id, org_id, integration_type, access_token, refresh_token)
  VALUES ($1, $2, 'google', $3, $4)
`, [wizardUserId, orgId, wizardAuth.access_token, wizardAuth.refresh_token]);
```

### **4. Get Google Task List IDs**

```typescript
// Fetch wizard's task lists
const taskLists = await googleTasks.tasklists.list({
  auth: wizardOAuth
});

console.log('Wizard Task Lists:', taskLists.data.items);

// Update in database
await db.query(`
  UPDATE google_task_lists
  SET google_task_list_id = $1
  WHERE person_id = $2
`, [taskLists.data.items[0].id, wizardPersonId]);
```

---

## 📋 **Example API Calls**

### **Create Task (Manual)**

```sql
INSERT INTO tasks (
    org_id,
    assigned_to_person_id,
    title,
    description,
    status,
    priority,
    due_date,
    source,
    sync_enabled
) VALUES (
    '00000000-0000-0000-0000-000000000001',
    (SELECT id FROM people WHERE email = 'wizard@disruptiveventures.se'),
    'Review Q4 investor deck',
    'Review and provide feedback on the Q4 investor presentation',
    'todo',
    'high',
    '2024-12-20',
    'manual',
    true
);
-- This will automatically trigger sync to Linear and Google Tasks!
```

### **Sync Existing Linear Issue to DB**

```sql
-- Assuming you have Linear issue data
SELECT create_task_from_linear(
    '00000000-0000-0000-0000-000000000001',  -- org_id
    'ISS-123',  -- linear_issue_id
    '{
        "title": "Fix authentication bug",
        "description": "Users unable to login with SSO",
        "state": "started",
        "priority": 2,
        "assigneeId": "abc123",
        "dueDate": "2024-12-25"
    }'::jsonb
);
```

### **Sync Google Task to DB**

```sql
SELECT create_task_from_google(
    '00000000-0000-0000-0000-000000000001',  -- org_id
    (SELECT id FROM people WHERE email = 'serge@disruptiveventures.se'),
    'MTIzNDU2Nzg5',  -- google_task_id
    '{
        "title": "Prepare board meeting agenda",
        "notes": "Review Q4 metrics and prepare discussion points",
        "status": "needsAction",
        "due": "2024-12-30T00:00:00Z"
    }'::jsonb
);
```

---

## 🔍 **Monitoring & Debugging**

### **View Sync Status**

```sql
-- Recent sync activity
SELECT 
    t.title,
    tsl.sync_direction,
    tsl.sync_type,
    tsl.sync_status,
    tsl.error_message,
    tsl.created_at
FROM task_sync_log tsl
JOIN tasks t ON t.id = tsl.task_id
ORDER BY tsl.created_at DESC
LIMIT 20;
```

### **Check Failed Syncs**

```sql
-- Failed syncs needing attention
SELECT 
    t.title,
    tsl.sync_direction,
    tsl.error_message,
    tsl.retry_count,
    tsl.created_at
FROM task_sync_log tsl
JOIN tasks t ON t.id = tsl.task_id
WHERE tsl.sync_status = 'failed'
AND tsl.retry_count >= 3
ORDER BY tsl.created_at DESC;
```

### **View User's Tasks**

```sql
-- Wizard's tasks
SELECT 
    t.title,
    t.status,
    t.priority,
    t.due_date,
    t.linear_issue_id,
    t.google_task_id,
    t.last_synced_to_linear_at,
    t.last_synced_to_google_at
FROM tasks t
JOIN people p ON p.id = t.assigned_to_person_id
WHERE p.email = 'wizard@disruptiveventures.se'
ORDER BY t.created_at DESC;
```

---

## ⚠️ **Important Considerations**

### **Conflict Resolution**

When same task updated in multiple places simultaneously:
1. **Last write wins** by default
2. Use `updated_at` timestamps to determine latest version
3. Log conflicts in `task_sync_log` for manual review

### **Rate Limiting**

- **Linear API**: 2000 requests/hour
- **Google Tasks API**: 10,000 requests/day
- Implement exponential backoff for retries

### **Data Privacy**

- ✅ Task descriptions may contain sensitive info
- ✅ RLS policies enforce org-level isolation
- ✅ Encrypt OAuth tokens at application layer
- ✅ Audit log tracks all changes

### **Performance**

- Use batch operations where possible
- Index on `linear_issue_id` and `google_task_id`
- Partition `task_sync_log` by date for large volumes

---

## 🎯 **Next Steps**

1. ✅ **Run migrations** (013_task_sync_system.sql)
2. ✅ **Setup wizard@ and serge@** (SETUP_WIZARD_SERGE_SYNC.sql)
3. ⚠️ **Build sync service** (Node.js/Python/Go)
4. ⚠️ **Configure Linear webhook**
5. ⚠️ **Setup Google OAuth for users**
6. ⚠️ **Get Google Task List IDs**
7. ⚠️ **Deploy and monitor**

---

## 📞 **Support**

Check the function documentation:
```sql
\df+ sync_task_to_linear
\df+ sync_task_to_google
\df+ create_task_from_linear
\df+ create_task_from_google
```

Your complete bidirectional task sync system is ready! 🚀
