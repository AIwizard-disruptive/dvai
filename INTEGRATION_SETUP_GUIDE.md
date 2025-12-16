# 🔌 Integration Setup Guide

Complete guide to setting up Google Workspace (Gmail, Drive, Calendar) and Linear integrations for automated meeting distribution.

---

## 📋 Overview

Your system needs these integrations to automatically:
- ✉️ **Gmail**: Send task solutions and updates to assignees
- 📅 **Calendar**: Create deadline events for action items
- 📁 **Drive**: Save meeting documents to shared folders
- 🎯 **Linear**: Create issues for action items with owners

---

## 1️⃣ Linear Integration (Easiest - 2 minutes)

### Get Your Linear API Key

1. **Go to Linear Settings**
   ```
   https://linear.app/settings/api
   ```

2. **Create Personal API Key**
   - Click "Personal API keys"
   - Click "Create new key"
   - Name: "Meeting Intelligence Bot"
   - Click "Create key"
   - **Copy the key** (starts with `lin_api_...`)

3. **Add to .env file**
   ```bash
   cd backend
   nano .env
   ```
   
   Find this line:
   ```
   LINEAR_API_KEY=
   ```
   
   Replace with:
   ```
   LINEAR_API_KEY=lin_api_YOUR_KEY_HERE
   ```
   
   Press `Ctrl+O` to save, `Ctrl+X` to exit

4. **Get Your Team ID** (needed for creating issues)
   - Open Linear
   - Go to your team's page
   - Copy team ID from URL: `linear.app/TEAM_NAME/...`
   - Or we'll fetch it via API once key is configured

### Test Linear Connection

```bash
curl -X POST http://localhost:8000/integrations/linear/test \
  -H "Content-Type: application/json"
```

Expected response:
```json
{
  "status": "connected",
  "teams": [
    {"id": "abc123", "name": "Engineering", "key": "ENG"}
  ]
}
```

---

## 2️⃣ Google Workspace Integration (10 minutes)

You already have OAuth credentials configured! Now we need to:
1. Enable required APIs
2. Add scopes
3. Get user consent

### A. Enable Google APIs

1. **Go to Google Cloud Console**
   ```
   https://console.cloud.google.com/apis/dashboard
   ```

2. **Enable these APIs** (click "+ ENABLE APIS AND SERVICES"):
   - ✅ Gmail API
   - ✅ Google Calendar API
   - ✅ Google Drive API

### B. Configure OAuth Consent Screen

1. **Go to OAuth consent screen**
   ```
   https://console.cloud.google.com/apis/credentials/consent
   ```

2. **Add Required Scopes**
   - Click "Edit App"
   - Scroll to "Scopes"
   - Click "Add or Remove Scopes"
   - Add:
     ```
     https://www.googleapis.com/auth/gmail.send
     https://www.googleapis.com/auth/gmail.compose
     https://www.googleapis.com/auth/calendar
     https://www.googleapis.com/auth/calendar.events
     https://www.googleapis.com/auth/drive.file
     ```
   - Click "Update"
   - Click "Save and Continue"

3. **Add Test Users** (if in testing mode)
   - Add your email: `wizard@disruptiveventures.se`
   - Add team member emails
   - Click "Save and Continue"

### C. Connect Your Google Account

1. **Start the server** (if not running)
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. **Open OAuth flow**
   ```
   http://localhost:8000/integrations/google/connect
   ```

3. **Sign in with Google**
   - Choose your Google Workspace account
   - Click "Allow" for all permissions
   - You'll be redirected back to the app

4. **Verify connection**
   ```
   http://localhost:8000/integrations/google/status
   ```

### D. Test Google Integrations

**Test Gmail:**
```bash
curl -X POST http://localhost:8000/integrations/google/test-email \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["your-email@example.com"],
    "subject": "Test from Meeting Intelligence",
    "body": "This is a test email!"
  }'
```

**Test Calendar:**
```bash
curl -X POST http://localhost:8000/integrations/google/test-calendar \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Test Event",
    "start": "2025-12-20T10:00:00Z",
    "end": "2025-12-20T11:00:00Z"
  }'
```

**Test Drive:**
```bash
curl -X POST http://localhost:8000/integrations/google/test-drive \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "Test Document",
    "content": "This is a test document from Meeting Intelligence"
  }'
```

---

## 3️⃣ Slack Integration (Optional - 5 minutes)

### Get Slack Webhook URL

1. **Go to Slack API**
   ```
   https://api.slack.com/apps
   ```

2. **Create New App**
   - Click "Create New App"
   - Choose "From scratch"
   - App Name: "Meeting Intelligence Bot"
   - Workspace: Choose your workspace
   - Click "Create App"

3. **Enable Incoming Webhooks**
   - Click "Incoming Webhooks" in sidebar
   - Toggle "Activate Incoming Webhooks" to ON
   - Click "Add New Webhook to Workspace"
   - Choose channel (e.g., #general or #meetings)
   - Click "Allow"

4. **Copy Webhook URL**
   - Copy the webhook URL (starts with `https://hooks.slack.com/services/...`)

5. **Add to .env**
   ```bash
   nano backend/.env
   ```
   
   Add this line:
   ```
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```

### Test Slack

```bash
curl -X POST http://localhost:8000/integrations/slack/test \
  -H "Content-Type: application/json" \
  -d '{
    "message": "🎉 Meeting Intelligence is connected!"
  }'
```

---

## 4️⃣ Verify Auto-Distribution Works

Once all integrations are configured, test the full workflow:

### Upload a Meeting

1. **Go to upload page**
   ```
   http://localhost:8000/upload-ui
   ```

2. **Upload a meeting transcript**
   - Drag & drop a .docx file with action items
   - Wait for processing

3. **Check auto-distribution**
   - ✅ Linear issues created for each action item
   - ✅ Calendar events created for deadlines
   - ✅ Emails sent to assignees
   - ✅ Slack notifications sent
   - ✅ Documents saved to Google Drive

### Check the Dashboard

```
http://localhost:8000/dashboard-ui
```

You should see:
- Meeting parsed
- Action items with owners
- Distribution status for each integration

---

## 🔧 Configuration Summary

After completing all steps, your `.env` should have:

```env
# Linear
LINEAR_API_KEY=lin_api_YOUR_KEY_HERE

# Google OAuth (already configured)
GOOGLE_CLIENT_ID=***REMOVED***
GOOGLE_CLIENT_SECRET=***REMOVED***
GOOGLE_REDIRECT_URI=http://localhost:8000/integrations/google/callback

# Slack (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Feature Flags (enable after testing)
ENABLE_EMAIL_SEND=true
ENABLE_CALENDAR_BOOKING=true
ENABLE_LINEAR_SYNC=true
ENABLE_SLACK_NOTIFICATIONS=true
```

---

## 📊 What Happens After Upload

```
User uploads meeting transcript
         ↓
3-Agent parsing extracts:
  - Action items
  - Owners
  - Deadlines
  - Decisions
         ↓
AUTO-DISTRIBUTION RUNS:
         ↓
┌────────────────────────────────┐
│  For each action item:         │
│                                │
│  1. Linear: Create issue       │
│     - Title: action item       │
│     - Assignee: owner          │
│     - Due date: deadline       │
│     - Labels: from meeting     │
│                                │
│  2. Calendar: Create event     │
│     - Title: "Deadline: X"     │
│     - Date: due date           │
│     - Attendees: owner         │
│                                │
│  3. Gmail: Send solution       │
│     - To: owner email          │
│     - Subject: "Task: X"       │
│     - Body: AI-generated       │
│            solution            │
│                                │
│  4. Slack: Notify team         │
│     - Channel: #meetings       │
│     - Message: task assigned   │
│                                │
│  5. Drive: Save documents      │
│     - Meeting notes            │
│     - Task details             │
│     - All in shared folder     │
└────────────────────────────────┘
         ↓
✅ Everyone has what they need
   in the tools they already use!
```

---

## 🚨 Troubleshooting

### Linear Issues

**Error: "Linear API key not configured"**
- Check `.env` has `LINEAR_API_KEY=lin_api_...`
- Restart server: `uvicorn app.main:app --reload`

**Error: "Team not found"**
- Get team ID from Linear URL or API
- Add to action item creation

### Google Issues

**Error: "Access token expired"**
- Reconnect: http://localhost:8000/integrations/google/connect

**Error: "Insufficient permissions"**
- Re-check OAuth scopes in Google Cloud Console
- Re-authorize the app

**Error: "API not enabled"**
- Enable APIs in Google Cloud Console
- Wait 1-2 minutes for propagation

### General

**Server not starting**
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill if needed
kill -9 <PID>

# Restart
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

---

## 🎯 Next Steps

1. **Set up Linear** (2 min) - Get API key, add to .env
2. **Enable Google APIs** (5 min) - Gmail, Calendar, Drive
3. **Connect Google account** (2 min) - OAuth flow
4. **Test each integration** (3 min) - Use curl commands above
5. **Upload test meeting** (1 min) - Verify auto-distribution
6. **Enable feature flags** - Turn on all integrations in .env

**Total time: ~15-20 minutes**

---

## ✅ Success Criteria

You know it's working when:
- ✅ Upload meeting → Linear tasks appear automatically
- ✅ Calendar shows deadline events
- ✅ Assignees receive emails with solutions
- ✅ Slack channel gets notifications
- ✅ Google Drive has all meeting documents
- ✅ **NO MANUAL WORK REQUIRED**

---

Need help? Check the logs:
```bash
tail -f backend/logs/app.log
```

Or check the terminal where the server is running for real-time errors.



