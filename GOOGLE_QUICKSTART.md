# Google Integration - 5 Minute Setup

Quick guide to get Google Calendar and Gmail working with your meetings.

## 🎯 What You'll Get

- **Gmail**: Auto-create follow-up email drafts
- **Calendar**: Create meeting proposals and events
- **Smart**: AI suggests optimal meeting times

## ⚡ Quick Setup

### 1. Get Google Cloud Credentials (5 min)

**A. Create Project**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "New Project" → Name: "Meeting Intelligence"
3. Click "Create"

**B. Enable APIs**
1. Go to "APIs & Services" → "Library"
2. Enable these:
   - Gmail API
   - Google Calendar API
   - Google Drive API

**C. Create OAuth Credentials**
1. "APIs & Services" → "Credentials"
2. "Create Credentials" → "OAuth client ID"
3. Choose "Web application"
4. Add redirect URI: `http://localhost:8000/integrations/google/callback`
5. Click "Create"
6. **Save Client ID and Secret**

**D. Configure Consent Screen**
1. "OAuth consent screen" → "External"
2. App name: "Meeting Intelligence"
3. Add your email
4. Add scopes:
   - `gmail.compose` (Create drafts)
   - `gmail.send` (Send emails)
   - `calendar` (Manage calendar)
5. Add yourself as test user
6. Save

### 2. Add to Your Backend

Edit `backend/.env`:

```env
# Google OAuth - ADD THESE
GOOGLE_CLIENT_ID=123456789-abc123.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8000/integrations/google/callback

# Feature Flags (keep false initially)
ENABLE_EMAIL_SEND=false
ENABLE_CALENDAR_BOOKING=false
```

### 3. Connect Your Account

**Start backend** (if not running):
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Connect Google**:
```bash
# Replace $ORG_ID with your org ID
open "http://localhost:8000/integrations/google/oauth?org_id=$ORG_ID"
```

This opens Google login → Grant permissions → Done!

### 4. Test It

**Process a meeting**:
```bash
curl -X POST http://localhost:8000/artifacts/upload \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" \
  -F "file=@meeting.mp3"
```

**Check Gmail drafts**:
- Go to [Gmail](https://mail.google.com)
- Click "Drafts"
- See your meeting follow-up!

**Check calendar proposals**:
```bash
curl http://localhost:8000/calendar/proposals \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

## 📧 Email Draft Features

Each draft includes:
- Meeting summary
- Key decisions with context
- Action items with owners
- Link to full transcript

**Safe by default**: Creates drafts only (doesn't send)

## 📅 Calendar Proposals

**Default behavior**: Creates proposals you can review
- View: `GET /calendar/proposals`
- Approve: `POST /calendar/proposals/{id}/approve`
- Reject: `POST /calendar/proposals/{id}/reject`

**Enable auto-booking** (when ready):
```env
ENABLE_CALENDAR_BOOKING=true
```

## 🚀 API Endpoints

| Endpoint | What It Does |
|----------|--------------|
| `GET /integrations/google/oauth` | Start OAuth flow |
| `POST /sync/google/email/meeting/{id}` | Create email draft |
| `POST /sync/google/calendar/meeting/{id}` | Create calendar proposal |
| `GET /calendar/proposals` | List proposals |
| `POST /calendar/proposals/{id}/approve` | Create actual event |

## 🔐 Security

- Tokens stored encrypted in your database
- Auto-refresh when expired
- Revoke anytime: `DELETE /integrations/google`

## 🐛 Troubleshooting

**"Access blocked: This app hasn't been verified"**
→ Add yourself as test user in OAuth consent screen

**"Redirect URI mismatch"**
→ Check `GOOGLE_REDIRECT_URI` matches exactly

**"Token expired"**
→ Tokens auto-refresh. If not working, reconnect:
```bash
open "http://localhost:8000/integrations/google/oauth?org_id=$ORG_ID"
```

## 📚 Full Documentation

See `GOOGLE_INTEGRATION.md` for:
- Detailed OAuth setup
- Custom email templates
- Smart meeting time suggestions
- Google Docs export (coming soon)

## ✅ Checklist

- [ ] Create Google Cloud project
- [ ] Enable Gmail, Calendar, Drive APIs
- [ ] Create OAuth credentials
- [ ] Add Client ID/Secret to .env
- [ ] Connect your Google account
- [ ] Upload test meeting
- [ ] Check Gmail drafts
- [ ] Review calendar proposals

**Done! Your meetings now auto-sync to Google! 🎉**



