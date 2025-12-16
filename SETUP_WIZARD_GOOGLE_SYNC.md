# Setup Wizard + Google Tasks Sync

## 🚀 Quick Setup (5 minutes)

### **Step 1: Run Database Migrations**

```bash
# Make sure you're using your Supabase connection
export DATABASE_URL="your_supabase_connection_string"

# Run migrations in order
psql $DATABASE_URL -f backend/migrations/013_task_sync_system.sql
psql $DATABASE_URL -f backend/migrations/SETUP_WIZARD_SERGE_SYNC.sql
```

Or run them through your database tool (Supabase dashboard, pgAdmin, etc.)

---

### **Step 2: Update Wizard Profile**

```bash
cd backend
python setup_wizard_sync.py
```

This will:
- ✅ Update wizard@disruptiveventures.se profile
- ✅ Set job title: "AI Assistant"
- ✅ Set department: "Operations"
- ✅ Set bio: "AI-powered assistant helping with task management..."

---

### **Step 3: Connect Google Account**

```bash
# Start your backend
uvicorn app.main:app --reload
```

Then in browser:
```
http://localhost:8000/integration-test
```

1. Click **"Connect Google"**
2. Authorize the app
3. **Copy the access_token** from the response

---

### **Step 4: Run Google Tasks Sync**

```bash
python sync_google_tasks.py
```

When prompted, paste your access_token.

This will:
- 📤 Push database tasks → Google Tasks
- 📥 Pull Google Tasks → database
- ✅ Keep both in sync

---

## 🧪 Test It Works

### **Create a task in your app:**

```python
# In Python console
import asyncio
from app.database import get_db
from sqlalchemy import text

async def create_test_task():
    async for db in get_db():
        await db.execute(text("""
            INSERT INTO tasks (
                org_id,
                assigned_to_email,
                title,
                description,
                status,
                priority,
                due_date,
                source
            ) VALUES (
                (SELECT id FROM orgs LIMIT 1),
                'wizard@disruptiveventures.se',
                'Review Q4 investor deck',
                'Provide feedback on the Q4 presentation by EOW',
                'todo',
                'high',
                CURRENT_DATE + INTERVAL '3 days',
                'manual'
            )
        """))
        await db.commit()
        print("✅ Task created!")

asyncio.run(create_test_task())
```

### **Run sync:**

```bash
python sync_google_tasks.py
```

### **Check Google Tasks:**

Open Google Tasks (https://tasks.google.com) and you should see:
- ✅ "Review Q4 investor deck" task
- ✅ Due date set
- ✅ Description included

---

## 🔄 Continuous Sync (Optional)

For automatic syncing, you can:

### **Option 1: Cron Job**

```bash
# Add to crontab (runs every 5 minutes)
*/5 * * * * cd /path/to/dv/backend && python sync_google_tasks.py
```

### **Option 2: Background Service**

Create `backend/sync_service.py`:

```python
#!/usr/bin/env python3
"""Background sync service - runs continuously"""

import asyncio
import time
from sync_google_tasks import GoogleTasksSync, get_db
from sqlalchemy import text

async def sync_loop(access_token: str, interval: int = 300):
    """Run sync every `interval` seconds (default 5 min)"""
    
    sync = GoogleTasksSync(access_token)
    
    while True:
        try:
            print(f"\n⏰ Running sync at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            async for db in get_db():
                # Get org and person
                result = await db.execute(text("SELECT id FROM orgs LIMIT 1"))
                org = await result.fetchone()
                org_id = str(org[0]) if org else None
                
                person_id = await sync.get_wizard_person_id(db)
                
                if person_id:
                    await sync.sync_db_to_google(db, person_id)
                    await sync.sync_google_to_db(db, person_id, org_id)
                    print("✅ Sync complete")
                else:
                    print("❌ Wizard not found")
            
        except Exception as e:
            print(f"❌ Sync error: {e}")
        
        # Wait before next sync
        await asyncio.sleep(interval)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python sync_service.py <access_token>")
        sys.exit(1)
    
    access_token = sys.argv[1]
    asyncio.run(sync_loop(access_token))
```

Run it:
```bash
# Keep it running in background
nohup python sync_service.py "your_access_token" &
```

---

## 📊 Monitor Sync Status

```sql
-- Check recent syncs
SELECT 
    t.title,
    t.status,
    t.google_task_id,
    t.last_synced_to_google_at,
    t.updated_at
FROM tasks t
WHERE t.assigned_to_email = 'wizard@disruptiveventures.se'
ORDER BY t.updated_at DESC
LIMIT 10;

-- Check sync log
SELECT 
    tsl.sync_direction,
    tsl.sync_status,
    tsl.synced_at,
    t.title
FROM task_sync_log tsl
JOIN tasks t ON t.id = tsl.task_id
WHERE t.assigned_to_email = 'wizard@disruptiveventures.se'
ORDER BY tsl.created_at DESC
LIMIT 20;
```

---

## 🐛 Troubleshooting

### **"Tasks table does not exist"**

Run migration first:
```bash
psql $DATABASE_URL -f backend/migrations/013_task_sync_system.sql
```

### **"Wizard profile not found"**

Run setup script:
```bash
python setup_wizard_sync.py
```

### **"Invalid credentials" from Google**

Your access token expired. Get a new one:
1. Go to http://localhost:8000/integration-test
2. Click "Connect Google" again
3. Copy new access_token

### **"Google Tasks API not enabled"**

Enable it in Google Cloud Console:
```
https://console.cloud.google.com/apis/library/tasks.googleapis.com
```

---

## ✅ Summary

**What you have now:**
- ✅ wizard@disruptiveventures.se profile updated
- ✅ Database table for tasks
- ✅ Sync script for Google Tasks
- ✅ Bidirectional sync (DB ↔ Google Tasks)

**To use it:**
1. Create tasks in your database
2. Run `python sync_google_tasks.py`
3. Tasks appear in Google Tasks ✨

**Or:**
1. Create tasks in Google Tasks
2. Run `python sync_google_tasks.py`
3. Tasks appear in your database ✨

---

🎉 **Your tasks are now synced with Google Tasks!**
