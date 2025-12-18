# 🔗 Complete Integrations Guide

Quick reference for all available integrations in your Meeting Intelligence Platform.

## 📊 Integration Status Dashboard

| Integration | Status | Setup Time | Documentation |
|-------------|--------|------------|---------------|
| **OpenAI** | ✅ Active | Done! | Built-in |
| **Google Workspace** | 📝 Ready | 5 min | GOOGLE_QUICKSTART.md |
| **Linear** | 📝 Ready | 2 min | LINEAR_QUICKSTART.md |
| **Supabase** | ⏳ In Progress | 5 min | SETUP_NOW.md |
| **Klang** | ⏳ Optional | 2 min | Built-in |
| **Mistral** | ⏳ Optional | 2 min | Built-in |

---

## 🚀 Quick Setup Links

### 1. OpenAI (✅ Already Done!)
**Purpose**: AI transcription and extraction  
**Status**: Configured with your API key  
**What it does**:
- Transcribes audio with Whisper
- Extracts summaries, decisions, action items with GPT-4
- Provides confidence scores

**No action needed** - already working!

---

### 2. Google Workspace (5 min)
**Purpose**: Email drafts and calendar events  
**Documentation**: `GOOGLE_QUICKSTART.md`

**Quick setup**:
```bash
# 1. Get credentials from console.cloud.google.com
# 2. Add to .env:
GOOGLE_CLIENT_ID=your-id
GOOGLE_CLIENT_SECRET=your-secret

# 3. Connect account:
open "http://localhost:8000/integrations/google/oauth?org_id=$ORG_ID"
```

**Features**:
- 📧 Auto-create email drafts with meeting summaries
- 📅 Create calendar event proposals
- ⚠️ Safe defaults: drafts/proposals only
- 🔓 Optional: Enable auto-send/book

**See also**: `GOOGLE_INTEGRATION.md` (detailed guide)

---

### 3. Linear (2 min)
**Purpose**: Sync action items to Linear issues  
**Documentation**: `LINEAR_QUICKSTART.md`

**Quick setup**:
```bash
# 1. Get API key from linear.app/settings/api

# 2. Add integration:
curl -X POST http://localhost:8000/integrations \
  -d '{
    "provider": "linear",
    "secrets": {"api_key": "lin_api_..."},
    "config": {"team_id": "your-team-id"}
  }'
```

**Features**:
- 📋 Action items → Linear issues
- 👤 Auto-assign owners
- 📅 Set due dates
- 🔄 Status sync (bidirectional coming soon)

**See also**: `LINEAR_INTEGRATION.md` (detailed guide)

---

## 🎯 Integration Workflows

### Workflow 1: Complete Meeting → Everything

```mermaid
Meeting Upload
    ↓
OpenAI Transcription (Whisper)
    ↓
OpenAI Extraction (GPT-4)
    ├─→ Summary
    ├─→ Decisions
    └─→ Action Items
    ↓
Parallel Sync
    ├─→ Gmail: Create draft email
    ├─→ Calendar: Create event proposal
    └─→ Linear: Create issues
```

### Workflow 2: Linear-Only

```
Meeting → AI Extraction → Action Items → Linear Issues
```

Good for: Teams using Linear, don't need email/calendar

### Workflow 3: Google-Only

```
Meeting → AI Extraction → Gmail Draft + Calendar Proposal
```

Good for: Email-centric teams, no Linear

---

## 🔧 Setup Priority

**Recommended order**:

1. ✅ **OpenAI** (already done)
2. 🥇 **Supabase** (database - see SETUP_NOW.md)
3. 🥈 **Linear** (2 min - immediate value)
4. 🥉 **Google** (5 min - email automation)
5. ⏳ **Alternatives** (only if needed)

---

## 📝 Configuration Reference

### Your `.env` file should have:

```env
# ✅ Already Configured
OPENAI_API_KEY=sk-proj-...
DEFAULT_TRANSCRIPTION_PROVIDER=openai

# ⏳ Add These (Supabase)
SUPABASE_URL=https://gqpupmuzriqarmrsuwev.supabase.co
SUPABASE_ANON_KEY=sb_publishable_-X1shl13fQAH68...
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
DATABASE_URL=postgresql+asyncpg://...

# 📝 Add These (Google)
GOOGLE_CLIENT_ID=123-abc.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...
GOOGLE_REDIRECT_URI=http://localhost:8000/integrations/google/callback

# 📝 Add via API (Linear)
# No .env needed - add through API endpoint

# 🚦 Feature Flags (start with false)
ENABLE_EMAIL_SEND=false
ENABLE_CALENDAR_BOOKING=false
```

---

## 🎮 Test All Integrations

### Complete test workflow:

```bash
# 1. Upload test meeting
curl -X POST http://localhost:8000/artifacts/upload \
  -F "file=@test_meeting.mp3"

# 2. Wait for processing (~3 min)
# OpenAI transcribes and extracts ✓

# 3. Check Linear
# Go to linear.app - see new issues ✓

# 4. Check Gmail
# Go to mail.google.com/drafts - see draft email ✓

# 5. Check calendar proposals
curl http://localhost:8000/calendar/proposals

# 6. Approve calendar proposal
curl -X POST http://localhost:8000/calendar/proposals/{id}/approve

# All integrations working! 🎉
```

---

## 📊 What Each Integration Gets You

### OpenAI
**Input**: Raw audio/document  
**Output**: 
- Transcript with speaker labels
- Confidence scores
- Meeting summary (markdown)
- Key decisions with rationale
- Action items with owners/dates
- Entity extraction

### Google Gmail
**Input**: Meeting intelligence  
**Output**:
- Draft email (or sent if enabled)
- To: All participants
- Subject: "Follow-up: [Meeting Title]"
- Body: Summary, decisions, action items
- Link to full transcript

### Google Calendar
**Input**: Meeting intelligence + action items  
**Output**:
- Event proposal (or booked if enabled)
- Title: "Follow-up: [Meeting Topic]"
- Attendees: All participants
- Description: Meeting notes + action items
- Suggested time based on due dates

### Linear
**Input**: Action items  
**Output**:
- Linear issue per action item
- Title: From AI extraction
- Assignee: Matched by name/email
- Due date: From AI extraction
- Description: Meeting context + source quote
- Labels: `from-meeting`
- Link: Back to transcript

---

## 🔐 Security & Privacy

All integrations:
- ✅ Tokens encrypted at rest (pgcrypto)
- ✅ Per-organization isolation (RLS)
- ✅ Revocable anytime
- ✅ Audit trail in `external_refs`
- ✅ Safe defaults (no auto-send/book)

---

## 🐛 Universal Troubleshooting

### Check All Integration Status
```bash
curl http://localhost:8000/integrations \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

### Test Specific Integration
```bash
# Test Linear
POST /integrations/test/linear

# Test Google
POST /integrations/test/google

# Test OpenAI
POST /integrations/test/openai
```

### View Sync History
```bash
# All external syncs
GET /external-refs

# For specific meeting
GET /meetings/{id}/external-refs

# For specific action item
GET /action-items/{id}/external-refs
```

### Check Celery Queue
```bash
celery -A app.worker.celery_app inspect active
celery -A app.worker.celery_app inspect scheduled
```

---

## 📚 Documentation Index

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **ALL_INTEGRATIONS.md** | This document | Reference |
| **GOOGLE_QUICKSTART.md** | Google 5-min setup | 5 min |
| **GOOGLE_INTEGRATION.md** | Google detailed guide | 15 min |
| **LINEAR_QUICKSTART.md** | Linear 2-min setup | 2 min |
| **LINEAR_INTEGRATION.md** | Linear detailed guide | 15 min |
| **INTEGRATIONS_OVERVIEW.md** | Overview + status | 10 min |
| **SETUP_NOW.md** | Initial platform setup | 10 min |
| **CONFIGURATION_STATUS.md** | Setup checklist | Reference |

---

## ✅ Complete Setup Checklist

### Core Platform
- [x] OpenAI API key added
- [ ] Supabase credentials configured
- [ ] Database migrations run
- [ ] Backend API running
- [ ] Celery worker running
- [ ] Frontend running (optional)

### Integrations
- [ ] Linear API key added
- [ ] Linear team ID configured
- [ ] Linear integration tested
- [ ] Google OAuth credentials obtained
- [ ] Google account connected
- [ ] Google integration tested

### Testing
- [ ] Test meeting uploaded
- [ ] Transcription successful
- [ ] AI extraction working
- [ ] Linear issues created
- [ ] Gmail draft created
- [ ] Calendar proposal created
- [ ] End-to-end workflow verified

### Production Ready
- [ ] Feature flags configured
- [ ] Team member mappings added
- [ ] Email templates customized (optional)
- [ ] Calendar times optimized (optional)
- [ ] Monitoring set up
- [ ] Backups configured

---

## 🎯 Quick Commands Cheat Sheet

```bash
# Add Linear
curl -X POST http://localhost:8000/integrations \
  -d '{"provider":"linear","secrets":{"api_key":"lin_api_..."},"config":{"team_id":"..."}}'

# Connect Google
open "http://localhost:8000/integrations/google/oauth?org_id=$ORG_ID"

# Upload meeting
curl -X POST http://localhost:8000/artifacts/upload -F "file=@meeting.mp3"

# Sync to Linear
curl -X POST http://localhost:8000/sync/linear/meeting/$MEETING_ID

# Create email draft
curl -X POST http://localhost:8000/sync/google/email/meeting/$MEETING_ID

# Create calendar proposal
curl -X POST http://localhost:8000/sync/google/calendar/meeting/$MEETING_ID

# List proposals
curl http://localhost:8000/calendar/proposals

# Approve proposal
curl -X POST http://localhost:8000/calendar/proposals/$ID/approve
```

---

## 🚀 Get Started Now

**Start here**: 

1. **Finish Supabase setup** (if not done):
   ```bash
   # See what's missing
   cat CONFIGURATION_STATUS.md
   ```

2. **Add Linear** (2 minutes):
   ```bash
   # Follow LINEAR_QUICKSTART.md
   ```

3. **Add Google** (5 minutes):
   ```bash
   # Follow GOOGLE_QUICKSTART.md
   ```

4. **Test everything**:
   ```bash
   # Upload a meeting and watch the magic! ✨
   ```

---

**All integrations documented and ready! Pick what you need and start connecting! 🎉**





