# ⚡ Quick Integration Setup (5 Minutes)

**Get your integrations running NOW**

---

## 🎯 Linear (2 minutes)

### Step 1: Get API Key
```bash
# 1. Open Linear Settings
open https://linear.app/settings/api

# 2. Create Personal API Key
#    - Name: "Meeting Intelligence"
#    - Click "Create"
#    - COPY THE KEY (starts with lin_api_)
```

### Step 2: Add to .env
```bash
cd backend
nano .env
```

Find the line:
```
LINEAR_API_KEY=
```

Paste your key:
```
LINEAR_API_KEY=lin_api_YOUR_KEY_HERE
```

Save: `Ctrl+O`, Exit: `Ctrl+X`

### Step 3: Test It
```bash
# Restart server (if running)
# In the terminal where server is running: Ctrl+C

# Start server
source venv/bin/activate
uvicorn app.main:app --reload

# In another terminal, test Linear:
curl http://localhost:8000/integrations/linear/status
```

Expected response:
```json
{
  "status": "connected",
  "teams": [{"id": "...", "name": "Your Team"}]
}
```

✅ **Linear is ready!** Tasks will auto-create from action items.

---

## 📧 Google (8 minutes)

### Step 1: Enable APIs
```bash
# Open Google Cloud Console
open https://console.cloud.google.com/apis/dashboard

# Enable these 3 APIs:
# 1. Gmail API
# 2. Google Calendar API
# 3. Google Drive API
```

### Step 2: Configure OAuth
```bash
# Go to OAuth consent screen
open https://console.cloud.google.com/apis/credentials/consent

# Click "Edit App" → "Scopes" → "Add or Remove Scopes"
```

Add these scopes:
```
https://www.googleapis.com/auth/gmail.send
https://www.googleapis.com/auth/gmail.compose
https://www.googleapis.com/auth/calendar
https://www.googleapis.com/auth/calendar.events
https://www.googleapis.com/auth/drive.file
```

Click "Update" → "Save and Continue"

###Step 3: Add Test Users (if in Testing mode)
```
# Add your email: wizard@disruptiveventures.se
# Add team members
# Click "Save"
```

### Step 4: Connect Your Account
```bash
# Server should be running
# Open this URL in browser:
open http://localhost:8000/integrations/google/connect

# Click the authorization_url shown
# Sign in with Google
# Click "Allow" for all permissions
```

### Step 5: Test It
```bash
# Check status
curl http://localhost:8000/integrations/google/status
```

✅ **Google is ready!** Emails, calendar events, and Drive docs will auto-sync.

---

## 💬 Slack (Optional - 5 minutes)

### Step 1: Create App
```bash
# Go to Slack API
open https://api.slack.com/apps

# Create New App → From scratch
#   Name: "Meeting Intelligence"
#   Workspace: Your workspace
```

### Step 2: Get Webhook
```bash
# Click "Incoming Webhooks"
# Toggle ON
# "Add New Webhook to Workspace"
# Choose channel (#meetings or #general)
# Copy the webhook URL
```

### Step 3: Add to .env
```bash
nano backend/.env
```

Add:
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Step 4: Test It
```bash
curl -X POST http://localhost:8000/integrations/slack/test \
  -H "Content-Type: application/json" \
  -d '{"message": "🎉 Meeting Intelligence is connected!"}'
```

Check your Slack channel for the message!

✅ **Slack is ready!** Team gets notified of new tasks automatically.

---

## ✅ Verify Everything Works

### Check Integration Dashboard
```bash
open http://localhost:8000/integrations/summary
```

Should show:
- ✅ Linear: Connected
- ✅ Google: Connected
- ✅ Slack: Connected (if configured)

### Test Full Workflow

1. **Upload a test meeting**
   ```bash
   open http://localhost:8000/upload-ui
   ```

2. **Upload a .docx file with action items like:**
   ```
   Action Items:
   - Marcus: Review design mockups (High priority, due Friday)
   - Fanny: Update pricing sheet (Medium priority, due Monday)
   ```

3. **Watch the magic happen:**
   - Linear tasks appear automatically
   - Calendar shows deadline events
   - Slack notifications sent
   - Emails delivered with solutions
   - Google Drive has all documents

4. **Check the results:**
   ```bash
   # Dashboard shows everything
   open http://localhost:8000/dashboard-ui
   
   # Linear shows new tasks
   open https://linear.app
   
   # Google Calendar shows events
   open https://calendar.google.com
   
   # Slack channel has notifications
   # Gmail inbox has task solutions
   ```

---

## 🚨 Troubleshooting

### Server won't start?
```bash
cd backend
source venv/bin/activate

# Install missing packages
pip install google-auth-oauthlib gql[all]

# Restart
uvicorn app.main:app --reload
```

### Linear not connecting?
```bash
# Check API key format (should start with lin_api_)
grep LINEAR_API_KEY backend/.env

# Test manually
curl http://localhost:8000/integrations/linear/status
```

### Google not working?
```bash
# 1. APIs enabled? Check console
# 2. Scopes added? Check OAuth consent
# 3. Account connected? Visit /integrations/google/connect
```

### Check logs
```bash
# In terminal where server is running
# Look for errors in real-time
```

---

## 📊 What Happens After Setup

```
User uploads meeting
         ↓
3-Agent parsing (automatic)
         ↓
AUTO-DISTRIBUTION (automatic):
  
  ✅ Linear: Tasks created
  ✅ Calendar: Events added
  ✅ Slack: Team notified
  ✅ Email: Solutions sent
  ✅ Drive: Docs saved
         ↓
END USERS GET EVERYTHING
(zero manual work!)
```

---

## ⏱️ Time Investment

- **Linear**: 2 minutes
- **Google**: 8 minutes  
- **Slack**: 5 minutes (optional)
- **Testing**: 2 minutes

**Total: 15-20 minutes to full automation**

---

## 🎉 Success!

Once configured, you never need to manually:
- ❌ Create Linear tasks
- ❌ Add calendar events
- ❌ Send reminder emails
- ❌ Notify team members
- ❌ Save meeting documents

Everything happens **automatically** after uploading a meeting transcript!

---

**Need help?** Check the full guide: `INTEGRATION_SETUP_GUIDE.md`

**Ready to test?** Upload a meeting: http://localhost:8000/upload-ui


