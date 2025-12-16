# Linear Integration - 2 Minute Setup

Sync meeting action items to Linear issues automatically.

## 🎯 What You Get

- ✅ Action items → Linear issues
- ✅ Auto-assign owners
- ✅ Set due dates and priorities
- ✅ Link back to meeting context
- ✅ Two-way sync (coming soon)

## ⚡ Setup (2 Minutes)

### 1. Get Linear API Key

1. Go to: https://linear.app/settings/api
2. Click **"Create new API key"**
3. Name: `Meeting Intelligence`
4. Copy the key (starts with `lin_api_...`)

### 2. Get Your Team ID

**Quick method** - Use GraphQL:

```bash
curl https://api.linear.app/graphql \
  -H "Authorization: lin_api_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ teams { nodes { id name key } } }"}'
```

Copy the `id` for your team.

### 3. Add Integration

```bash
curl -X POST http://localhost:8000/integrations \
  -H "Authorization: Bearer $YOUR_TOKEN" \
  -H "X-Org-Id: $YOUR_ORG_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "linear",
    "secrets": {
      "api_key": "lin_api_YOUR_KEY_HERE"
    },
    "config": {
      "team_id": "YOUR_TEAM_ID_HERE",
      "default_priority": 3,
      "add_meeting_label": true
    }
  }'
```

✅ **Done!** Linear is connected.

## 🧪 Test It

### Upload a test meeting:

```bash
# Create test notes
cat > test_meeting.txt << 'EOF'
Sprint Planning - Dec 12, 2025

Action Items:
1. Alice will complete the user dashboard by Friday
2. Bob needs to review the API documentation by Dec 15
3. Charlie will schedule the demo for next week
EOF

# Upload
curl -X POST http://localhost:8000/artifacts/upload \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" \
  -F "file=@test_meeting.txt"
```

### Check Linear

Go to https://linear.app - you should see 3 new issues! 🎉

## 🔄 How It Works

```
Meeting → AI Extraction → Action Items → Linear Issues
```

**Status mapping**:
- `open` → Todo
- `in_progress` → In Progress
- `blocked` → Blocked
- `done` → Done

## 📊 API Endpoints

```bash
# Sync meeting to Linear
POST /sync/linear/meeting/{meeting_id}

# Sync single action item
POST /action-items/{item_id}/sync-linear

# View synced items
GET /integrations/linear/synced-items

# Test connection
POST /integrations/test/linear
```

## ⚙️ Configuration Options

Basic config:
```json
{
  "team_id": "abc123...",
  "default_priority": 3,
  "add_meeting_label": true
}
```

Advanced config:
```json
{
  "team_id": "abc123...",
  "default_priority": 3,
  "priority_mapping": {
    "high": 2,
    "medium": 3,
    "low": 4
  },
  "state_mapping": {
    "open": "Backlog",
    "in_progress": "In Progress",
    "done": "Done"
  },
  "team_members": [
    {
      "name": "Alice",
      "email": "alice@company.com",
      "linear_id": "user-uuid"
    }
  ],
  "auto_sync": true
}
```

## 🐛 Troubleshooting

**"Linear not configured"**
```bash
# Check integration exists
curl http://localhost:8000/integrations | grep linear
```

**"Cannot find team"**
```bash
# Verify team ID
curl https://api.linear.app/graphql \
  -H "Authorization: lin_api_YOUR_KEY" \
  -d '{"query": "{ teams { nodes { id name } } }"}'
```

**Issues not syncing**
```bash
# Check Celery worker is running
celery -A app.worker.celery_app inspect active

# Manual sync
curl -X POST http://localhost:8000/sync/linear/meeting/$MEETING_ID
```

## 🎯 What Gets Synced

**Linear Issue includes**:
- **Title**: From AI extraction
- **Description**: Meeting context + source quote
- **Assignee**: Matched by name or email
- **Due date**: From AI extraction
- **Priority**: Based on keywords and confidence
- **Labels**: `from-meeting`, meeting type
- **Project**: (if configured)
- **Link**: Back to full transcript

**Example Linear Issue**:
```
Title: Complete user dashboard

Description:
Complete the user dashboard redesign with new analytics

From Meeting: Sprint Planning
Date: 2025-12-12
Confidence: High (0.95)

Source Quote:
> "Alice, can you wrap up the dashboard? We need it for the demo on Friday."

🔗 View full transcript: http://localhost:3000/meetings/abc-123
```

## 📈 Best Practices

1. **Review first**: Start with manual sync, review AI output
2. **Map team**: Add team member mappings for better matching
3. **Use labels**: Enable `add_meeting_label` for tracking
4. **Monitor confidence**: Only auto-sync high-confidence items initially

## ✅ Checklist

- [ ] Got Linear API key
- [ ] Found team ID
- [ ] Added integration via API
- [ ] Processed test meeting
- [ ] Verified issues in Linear
- [ ] Tested status updates
- [ ] Configured team member mappings (optional)
- [ ] Enabled auto-sync (optional)

## 🚀 Next Steps

**Already working?** Great! Your meetings now automatically create Linear issues.

**Want more?** See:
- `LINEAR_INTEGRATION.md` - Full documentation
- `INTEGRATIONS_OVERVIEW.md` - All integrations

**Add more integrations**:
- Google (Gmail + Calendar): `GOOGLE_QUICKSTART.md`
- Already configured: OpenAI for AI extraction

---

**Linear synced! Now your meeting action items become trackable tasks! 🎉**




