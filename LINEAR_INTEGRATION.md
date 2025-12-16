# Linear Integration Guide

Complete guide to syncing meeting action items with Linear for seamless project management.

## 🎯 What Linear Integration Does

Your Meeting Intelligence Platform automatically:
- ✅ **Syncs action items** from meetings to Linear issues
- ✅ **Maps owners** to Linear assignees (by name or email)
- ✅ **Sets due dates** from AI-extracted deadlines
- ✅ **Includes context** with meeting links and source quotes
- ✅ **Maintains sync** with two-way updates
- ✅ **Tracks provenance** - every issue links back to transcript

### Example Flow

```
Meeting: "Product Planning Session"
    ↓
AI extracts: "Alice will complete design mockups by Dec 20"
    ↓
Linear issue created:
    Title: "Complete design mockups"
    Assignee: Alice (matched by name)
    Due date: 2025-12-20
    Description: Includes meeting context + source quote
    Labels: "from-meeting"
    ↓
Updates sync both ways:
    - Change status in Linear → Updates in your platform
    - Change in platform → Updates Linear issue
```

---

## 🚀 Quick Setup (2 Minutes)

### Step 1: Get Your Linear API Key

1. Go to [Linear Settings → API](https://linear.app/settings/api)
2. Click **"Create new API key"**
3. Give it a name: `Meeting Intelligence Platform`
4. Click **"Create key"**
5. **Copy the key** (starts with `lin_api_...`)
   
   ⚠️ **Important**: Save it now - you won't see it again!

### Step 2: Get Your Team ID

**Option A: From Linear URL**
```
Your workspace: https://linear.app/acme/team/ENG/...
                                         ^^^
Team key is "ENG" - you'll need the actual team ID
```

**Option B: Using GraphQL API**
```bash
curl https://api.linear.app/graphql \
  -H "Authorization: YOUR_LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ teams { nodes { id name key } } }"
  }'
```

Copy the `id` field for your team (looks like: `abc123-def456-...`)

### Step 3: Add Integration via API

```bash
# Make sure your backend is running
curl -X POST http://localhost:8000/integrations \
  -H "Authorization: Bearer $YOUR_SUPABASE_TOKEN" \
  -H "X-Org-Id: $YOUR_ORG_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "linear",
    "secrets": {
      "api_key": "lin_api_YOUR_KEY_HERE"
    },
    "config": {
      "team_id": "abc123-def456-YOUR_TEAM_ID",
      "default_priority": 3,
      "add_meeting_label": true
    }
  }'
```

Response:
```json
{
  "id": "integration-uuid",
  "provider": "linear",
  "enabled": true,
  "config": {...},
  "created_at": "2025-12-12T..."
}
```

✅ **Done!** Linear is now connected.

---

## 📊 How It Works

### Automatic Sync (Default)

After every meeting is processed:
```
Meeting Processed
    ↓
Action Items Extracted
    ↓
Linear Integration Detected
    ↓
For each action item:
    ├─→ Check if already synced
    ├─→ If new: Create Linear issue
    └─→ If exists: Update Linear issue
    ↓
External ref saved (for idempotency)
```

### Manual Sync

Trigger sync manually for a specific meeting:
```bash
curl -X POST http://localhost:8000/sync/linear/meeting/$MEETING_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

Or for a specific action item:
```bash
curl -X POST http://localhost:8000/action-items/$ITEM_ID/sync-linear \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

---

## 🔄 Status Mapping

Meeting action item statuses automatically map to Linear states:

| Meeting Status | Linear State |
|----------------|--------------|
| `open` | **Todo** |
| `in_progress` | **In Progress** |
| `blocked` | **Blocked** |
| `done` | **Done** |
| `cancelled` | **Cancelled** |

### Custom State Mapping

Configure custom mappings in integration config:
```json
{
  "config": {
    "team_id": "abc123...",
    "state_mapping": {
      "open": "Backlog",
      "in_progress": "In Progress",
      "blocked": "Blocked",
      "done": "Completed"
    }
  }
}
```

---

## 👤 Owner/Assignee Matching

The system intelligently matches action item owners to Linear users:

### Matching Priority

1. **By Email** (most reliable):
   ```
   AI extracts: "alice@company.com will do X"
   → Matches Linear user with email "alice@company.com"
   ```

2. **By Name** (fuzzy matching):
   ```
   AI extracts: "Alice Johnson will do X"
   → Searches Linear for user named "Alice Johnson"
   → Falls back to "Alice" if exact match not found
   ```

3. **Unassigned** (fallback):
   ```
   AI extracts: "Someone should do X" (no clear owner)
   → Creates unassigned issue
   → Can be assigned manually in Linear
   ```

### Pre-configure Team Members

Help improve matching by adding team member mappings:
```bash
curl -X PATCH http://localhost:8000/integrations/$INTEGRATION_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "team_members": [
        {"name": "Alice", "email": "alice@company.com", "linear_id": "user-uuid-1"},
        {"name": "Bob", "email": "bob@company.com", "linear_id": "user-uuid-2"}
      ]
    }
  }'
```

---

## 📝 Issue Format

### Linear Issue Title
```
Complete design mockups
```
Clean, action-oriented from AI extraction.

### Linear Issue Description
```markdown
Complete design mockups for the new dashboard feature

**From Meeting**: Product Planning Session
**Meeting Date**: 2025-12-10
**Confidence**: High (0.9)

**Source Quote**:
> "Alice, can you work on the design mockups? We need them by next Friday."

**Context**:
This action item was extracted from the meeting transcript using AI.
The owner and due date were identified from the discussion.

🔗 [View full meeting transcript](http://localhost:3000/meetings/abc-123)
```

### Automatic Labels

Issues created from meetings get tagged with:
- `from-meeting` (if `add_meeting_label: true`)
- Meeting type (e.g., `standup`, `planning`)
- Project tags from meeting

---

## 🔗 Two-Way Sync

### Platform → Linear

Updates in your platform automatically sync to Linear:

```bash
# Update action item status
curl -X PATCH http://localhost:8000/action-items/$ITEM_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" \
  -d '{"status": "in_progress"}'

# Linear issue updated to "In Progress" ✓
```

### Linear → Platform (Coming Soon)

Webhook support for Linear → Platform updates:
```
Linear issue updated
    ↓
Webhook received
    ↓
Action item updated in platform
```

**Setup webhook** (when ready):
1. Linear Settings → Webhooks
2. Add webhook URL: `https://your-domain.com/webhooks/linear`
3. Select events: `Issue created`, `Issue updated`, `Issue deleted`

---

## ⚙️ Configuration Options

### Basic Configuration

```json
{
  "team_id": "abc123-...",
  "default_priority": 3,
  "add_meeting_label": true
}
```

### Advanced Configuration

```json
{
  "team_id": "abc123-...",
  
  // Priority mapping (1=Urgent, 2=High, 3=Normal, 4=Low)
  "default_priority": 3,
  "priority_mapping": {
    "high": 2,
    "medium": 3,
    "low": 4
  },
  
  // Labels
  "add_meeting_label": true,
  "meeting_label_name": "from-meeting",
  "auto_add_labels": ["ai-generated", "needs-review"],
  
  // State mapping (use your team's state names)
  "state_mapping": {
    "open": "Backlog",
    "in_progress": "In Progress",
    "blocked": "Blocked",
    "done": "Done"
  },
  
  // Team member mappings (for better owner matching)
  "team_members": [
    {
      "name": "Alice Johnson",
      "email": "alice@company.com",
      "linear_id": "user-uuid-1"
    }
  ],
  
  // Project assignment
  "default_project_id": "project-uuid",
  
  // Automation
  "auto_sync": true,
  "sync_updates": true,
  "create_subtasks": false
}
```

---

## 🎯 API Reference

### Integration Management

```bash
# Add Linear integration
POST /integrations
{
  "provider": "linear",
  "secrets": {"api_key": "lin_api_..."},
  "config": {"team_id": "..."}
}

# List integrations
GET /integrations

# Update Linear config
PATCH /integrations/$INTEGRATION_ID
{
  "config": {"default_priority": 2}
}

# Test Linear connection
POST /integrations/test/linear

# Remove integration
DELETE /integrations/$INTEGRATION_ID
```

### Sync Operations

```bash
# Sync all action items from a meeting
POST /sync/linear/meeting/$MEETING_ID

# Sync single action item
POST /action-items/$ITEM_ID/sync-linear

# Force re-sync (updates all existing issues)
POST /sync/linear/meeting/$MEETING_ID?force=true

# View sync status
GET /action-items/$ITEM_ID/external-refs
```

### Query Linear Data

```bash
# List teams (to get team IDs)
GET /integrations/linear/teams

# List team members
GET /integrations/linear/teams/$TEAM_ID/members

# List workflow states
GET /integrations/linear/teams/$TEAM_ID/states

# Search users
GET /integrations/linear/users?q=alice

# List synced issues
GET /integrations/linear/issues?meeting_id=$MEETING_ID
```

---

## 📊 Usage Examples

### Example 1: Complete Workflow

```bash
# 1. Upload meeting
curl -X POST http://localhost:8000/artifacts/upload \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" \
  -F "file=@standup.mp3"

# 2. Wait for processing (~3 min)

# 3. Get meeting ID
MEETING_ID=$(curl http://localhost:8000/meetings \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" | jq -r '.[0].id')

# 4. View action items
curl http://localhost:8000/meetings/$MEETING_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" | jq '.action_items'

# 5. Sync to Linear (if not auto-synced)
curl -X POST http://localhost:8000/sync/linear/meeting/$MEETING_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"

# 6. Check Linear - issues are there! ✓
```

### Example 2: Update Existing Issue

```bash
# Get action item
ACTION_ITEM_ID="..."

# Update status
curl -X PATCH http://localhost:8000/action-items/$ACTION_ITEM_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" \
  -d '{
    "status": "in_progress",
    "owner_email": "bob@company.com"
  }'

# Linear issue automatically updated ✓
```

### Example 3: Batch Sync Multiple Meetings

```bash
# Get all meetings from last week
MEETINGS=$(curl http://localhost:8000/meetings?since=7d \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" | jq -r '.[].id')

# Sync each to Linear
for meeting_id in $MEETINGS; do
  curl -X POST http://localhost:8000/sync/linear/meeting/$meeting_id \
    -H "Authorization: Bearer $TOKEN" \
    -H "X-Org-Id: $ORG_ID"
done
```

---

## 🔍 Monitoring & Troubleshooting

### Check Sync Status

```bash
# View all synced items
curl http://localhost:8000/integrations/linear/synced-items \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"

# Check specific action item
curl http://localhost:8000/action-items/$ITEM_ID/external-refs \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

### Common Issues

**1. "Linear not configured"**
```bash
# Check integration exists
curl http://localhost:8000/integrations \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"

# Should show Linear with enabled: true
```

**2. "Team ID not found"**
```bash
# Verify team ID
curl https://api.linear.app/graphql \
  -H "Authorization: YOUR_LINEAR_API_KEY" \
  -d '{"query": "{ teams { nodes { id name } } }"}'
```

**3. "Cannot match owner"**
```bash
# Add team member mapping
curl -X PATCH http://localhost:8000/integrations/$INTEGRATION_ID \
  -d '{
    "config": {
      "team_members": [
        {"name": "Alice", "linear_id": "..."}
      ]
    }
  }'
```

**4. Issues duplicating**
- Check `external_refs` table for existing mappings
- Use `force=false` on sync to prevent duplicates
- Clear old refs if needed: `DELETE /external-refs/$REF_ID`

### View Celery Logs

```bash
# Check Celery worker logs for sync details
celery -A app.worker.celery_app inspect active

# Specific task logs
tail -f celery-worker.log | grep linear
```

---

## 🎨 Customization

### Custom Issue Templates

Edit `backend/app/worker/tasks/sync.py`:

```python
async def _sync_action_items_to_linear(meeting_id: str, org_id: str):
    # Customize issue description
    description = f"""
{item.title}

**Meeting Context**
- Meeting: {meeting.title}
- Date: {meeting.meeting_date}
- Type: {meeting.meeting_type}

**AI Extraction Details**
- Confidence: {item.confidence:.0%}
- Source: "{item.source_quote[:100]}..."

**Action Required**
{item.description}

---
🤖 Auto-generated from meeting transcript
🔗 [View transcript](http://localhost:3000/meetings/{meeting_id})
    """.strip()
```

### Custom Priority Logic

```python
# Map AI confidence to Linear priority
def get_priority(item: ActionItem) -> int:
    if item.priority == "high" or item.confidence > 0.9:
        return 1  # Urgent
    elif item.priority == "medium":
        return 2  # High
    elif item.confidence < 0.5:
        return 4  # Low (uncertain)
    else:
        return 3  # Normal
```

### Auto-assign Based on Keywords

```python
# Smart assignment based on task content
def assign_owner(item: ActionItem) -> Optional[str]:
    if "design" in item.title.lower():
        return design_team_lead_id
    elif "backend" in item.title.lower():
        return backend_team_lead_id
    else:
        return item.owner_linear_id
```

---

## 🚀 Advanced Features

### Subtask Creation

Create Linear sub-issues for multi-step action items:

```python
# Detect multi-step actions
if "\n-" in item.description:
    # Parse subtasks
    subtasks = parse_subtasks(item.description)
    
    # Create parent issue
    parent = await linear.create_issue(...)
    
    # Create sub-issues
    for subtask in subtasks:
        await linear.create_issue(
            parent_id=parent["id"],
            title=subtask.title,
            ...
        )
```

### Project Auto-assignment

Map meeting types to Linear projects:

```json
{
  "config": {
    "project_mapping": {
      "sprint_planning": "project-uuid-1",
      "product_review": "project-uuid-2",
      "customer_call": "project-uuid-3"
    }
  }
}
```

### Time Estimates

Extract and set time estimates:

```python
# AI extracts: "This should take about 2 hours"
# Parse estimate and set in Linear
if item.estimated_hours:
    await linear.update_issue(
        issue_id=issue_id,
        estimate=item.estimated_hours
    )
```

---

## 📈 Best Practices

### 1. Start with Manual Sync
- Disable auto-sync initially: `"auto_sync": false`
- Review AI-extracted action items first
- Manually trigger sync when ready
- Enable auto-sync after confidence builds

### 2. Review AI Confidence
```bash
# Only sync high-confidence items
GET /action-items?confidence_min=0.8
```

### 3. Use Clear Meeting Titles
```
✅ Good: "Q4 Sprint Planning - Product Team"
❌ Bad: "Meeting 123"
```

### 4. Maintain Team Member Mappings
- Keep `team_members` config updated
- Add new hires promptly
- Use consistent name formats

### 5. Monitor Sync Status
```bash
# Weekly sync health check
curl http://localhost:8000/integrations/linear/stats
```

---

## 📊 Metrics & Analytics

### Track Sync Performance

```sql
-- View sync success rate
SELECT 
  COUNT(*) as total,
  SUM(CASE WHEN kind = 'linear_issue' THEN 1 ELSE 0 END) as synced,
  ROUND(100.0 * SUM(CASE WHEN kind = 'linear_issue' THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM action_items;
```

### Most Active Assignees

```sql
-- Top action item owners
SELECT 
  owner_name,
  COUNT(*) as items,
  AVG(confidence) as avg_confidence
FROM action_items
WHERE org_id = 'your-org-id'
GROUP BY owner_name
ORDER BY items DESC
LIMIT 10;
```

---

## 🎓 Training Linear GraphQL

Want to customize further? Learn Linear's GraphQL API:

```bash
# Interactive GraphQL playground
open https://studio.apollographql.com/sandbox/explorer?endpoint=https://api.linear.app/graphql

# Example custom query
curl https://api.linear.app/graphql \
  -H "Authorization: YOUR_KEY" \
  -d '{
    "query": "query Issues($teamId: String!) {
      issues(filter: {team: {id: {eq: $teamId}}}) {
        nodes {
          id
          title
          state { name }
          assignee { name email }
        }
      }
    }",
    "variables": {"teamId": "YOUR_TEAM_ID"}
  }'
```

---

## ✅ Setup Checklist

- [ ] Linear API key obtained
- [ ] Team ID found
- [ ] Integration added via API
- [ ] Team members mapped (optional)
- [ ] Test meeting uploaded
- [ ] Action items synced to Linear
- [ ] Linear issues verified
- [ ] Status update tested (both ways)
- [ ] Auto-sync enabled (if desired)

---

## 🔗 Quick Links

| Resource | URL |
|----------|-----|
| Linear API Docs | https://developers.linear.app/ |
| Linear API Keys | https://linear.app/settings/api |
| Linear GraphQL Explorer | https://studio.apollographql.com/sandbox/explorer |
| Your Linear Workspace | https://linear.app/your-workspace |

---

## 🎯 Next Steps

1. ✅ **Get Linear API key** (2 minutes)
2. ✅ **Add integration via API** (see Quick Setup above)
3. ✅ **Process a test meeting**
4. ✅ **Verify issues in Linear**
5. 🚀 **Enable auto-sync and enjoy!**

---

**Linear integration complete! Your meetings now become Linear issues automatically! 🚀**




