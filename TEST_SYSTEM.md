# 🧪 System Testing Guide

## What You've Built

A **GDPR-compliant, multi-tenant meeting intelligence platform** that:
- ✅ Uploads and processes meeting recordings/transcripts
- ✅ Extracts action items, decisions, insights with AI
- ✅ Syncs with Linear (tasks) and Google Calendar
- ✅ Enforces strict row-level security for multi-org isolation

---

## 🚀 Quick Start: Test in 5 Minutes

### Prerequisites

1. **Start Backend Server**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

2. **Verify Server is Running**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Meeting Intelligence Platform",
  "environment": "development"
}
```

---

## 📋 **Test Method 1: Upload UI (No Auth Required - Dev Mode)**

### Step 1: Open Upload UI

Open in browser:
```
http://localhost:8000/upload-ui
```

You'll see a beautiful drag-and-drop interface!

### Step 2: Upload Test Files

**Supported formats:**
- `.docx` - Word documents with meeting notes
- `.mp3`, `.wav`, `.m4a`, `.ogg` - Audio recordings

**What happens:**
1. Files are saved to `/tmp/dev-uploads/`
2. In production: Would trigger AI processing pipeline
3. Returns upload confirmation with file ID

**Test with:**
- Drag & drop multiple files at once
- Click to browse and select files
- Upload up to 100 files in one batch

### Step 3: Check Response

Each file gets:
```json
{
  "id": "uuid-here",
  "filename": "Meeting_Notes.docx",
  "file_type": "docx",
  "file_size": 12345,
  "status": "uploaded",
  "mode": "development"
}
```

---

## 📋 **Test Method 2: API with cURL**

### 1. Test Health Check

```bash
curl http://localhost:8000/health
```

### 2. Test Root Endpoint

```bash
curl http://localhost:8000/
```

### 3. Upload a File (Dev Mode - No Auth)

```bash
curl -X POST http://localhost:8000/artifacts/upload-dev \
  -F "file=@/path/to/your/file.docx"
```

Expected response:
```json
{
  "id": "artifact-id",
  "filename": "file.docx",
  "file_type": "docx",
  "file_size": 12345,
  "status": "uploaded",
  "mode": "development",
  "message": "File saved locally. Database and processing disabled in dev mode.",
  "path": "/tmp/dev-uploads/uuid/file.docx"
}
```

---

## 📋 **Test Method 3: Full Production Flow (With Auth)**

### Prerequisites:
1. Create a Supabase user
2. Get JWT token
3. Have org_id

### Step 1: Create Organization

```bash
# In Supabase SQL Editor:
INSERT INTO orgs (name, settings)
VALUES ('Test Company', '{}')
RETURNING id;
```

Copy the returned `id`.

### Step 2: Add Yourself to Org

```bash
# Get your user_id from: Supabase Dashboard → Authentication → Users
INSERT INTO org_memberships (org_id, user_id, role)
VALUES (
  'YOUR-ORG-ID',
  'YOUR-USER-ID',
  'owner'
);
```

### Step 3: Get Auth Token

```bash
# Option A: Via Supabase Auth UI
# Go to Supabase Dashboard → Authentication → sign in

# Option B: Via API
curl -X POST 'https://YOUR-PROJECT.supabase.co/auth/v1/token?grant_type=password' \
  -H "apikey: YOUR-ANON-KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "password": "your-password"
  }'
```

Copy the `access_token` from response.

### Step 4: Create a Meeting

```bash
TOKEN="your-jwt-token-here"

curl -X POST http://localhost:8000/meetings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Q1 Strategy Review",
    "meeting_date": "2024-01-15",
    "meeting_type": "strategy",
    "company": "Acme Corp"
  }'
```

Response:
```json
{
  "id": "meeting-uuid",
  "org_id": "org-uuid",
  "title": "Q1 Strategy Review",
  "meeting_date": "2024-01-15",
  "processing_status": "pending"
}
```

### Step 5: Upload Artifact to Meeting

```bash
MEETING_ID="meeting-uuid-from-above"
TOKEN="your-jwt-token"

curl -X POST http://localhost:8000/artifacts/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/meeting-recording.mp3"
```

---

## 🧪 **Test AI Processing Pipeline**

### Prerequisites:
- Set `OPENAI_API_KEY` in `backend/.env`
- Have Celery worker running

### Start Celery Worker:

```bash
cd backend
source venv/bin/activate
celery -A app.worker.celery_app worker --loglevel=info
```

### Trigger Processing:

```bash
TOKEN="your-jwt-token"
MEETING_ID="your-meeting-id"

curl -X POST http://localhost:8000/meetings/$MEETING_ID/process \
  -H "Authorization: Bearer $TOKEN"
```

**What happens:**
1. Artifact is transcribed (if audio) or extracted (if docx)
2. AI analyzes transcript
3. Extracts:
   - ✅ Action items (with owners, due dates, priority)
   - ✅ Decisions (with rationale, confidence scores)
   - ✅ Summary (key points, outcomes)
   - ✅ Named entities (companies, products, people)

### Check Results:

```bash
# Get meeting with all extracted data
curl http://localhost:8000/meetings/$MEETING_ID \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔄 **Test Integrations**

### Linear Integration

```bash
# Sync meeting action items to Linear
curl -X POST http://localhost:8000/sync/meeting/$MEETING_ID/linear \
  -H "Authorization: Bearer $TOKEN"
```

Requires: `LINEAR_API_KEY` in `.env`

### Google Calendar

```bash
# Create calendar proposal
curl -X POST http://localhost:8000/calendar/proposals \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": "meeting-uuid",
    "proposed_times": ["2024-01-20T10:00:00Z"],
    "attendee_emails": ["attendee@example.com"]
  }'
```

---

## 📊 **API Endpoints Overview**

### Core Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | No | Health check |
| `/upload-ui` | GET | No | Upload interface (dev) |
| `/artifacts/upload-dev` | POST | No | Upload file (dev mode) |
| `/artifacts/upload` | POST | Yes | Upload file (production) |
| `/meetings` | GET/POST | Yes | List/create meetings |
| `/meetings/{id}` | GET/PUT/DELETE | Yes | Manage meeting |
| `/meetings/{id}/process` | POST | Yes | Trigger AI processing |
| `/action-items` | GET | Yes | List action items |
| `/decisions` | GET | Yes | List decisions |
| `/sync/meeting/{id}/linear` | POST | Yes | Sync to Linear |
| `/calendar/proposals` | GET/POST | Yes | Calendar scheduling |

### Interactive API Docs

```
http://localhost:8000/docs
```

Full Swagger UI with "Try it out" buttons!

---

## 🧪 **Test RLS (Row-Level Security)**

### Verify Multi-Tenant Isolation:

1. **Create two orgs and users**
2. **Try to access other org's data**

Should fail:
```bash
# User A tries to access User B's meeting
curl http://localhost:8000/meetings/$USER_B_MEETING_ID \
  -H "Authorization: Bearer $USER_A_TOKEN"
```

Expected: `404 Not Found` (RLS blocks access)

---

## 🐛 **Troubleshooting**

### "Connection failed" error
```bash
# Check database connection
cd backend
python scripts/test_connection.py
```

### "Authentication failed"
- Verify JWT token is valid
- Check `SUPABASE_JWT_SECRET` in `.env`
- Token format: `Bearer eyJhbGciOi...`

### "File upload fails"
- Check file size (< 50MB)
- Verify file type (.docx, .mp3, .wav, m4a)
- Check `/tmp/` directory permissions

### "AI processing not working"
- Verify `OPENAI_API_KEY` in `.env`
- Start Celery worker: `celery -A app.worker.celery_app worker`
- Check Redis is running: `redis-cli ping` → should return `PONG`

---

## ✅ **Verification Checklist**

- [ ] Server starts without errors
- [ ] `/health` returns healthy
- [ ] `/upload-ui` loads in browser
- [ ] Can upload files via UI
- [ ] Can upload files via API
- [ ] Can create meetings (with auth)
- [ ] Can list meetings
- [ ] AI processing extracts action items
- [ ] AI processing extracts decisions
- [ ] RLS blocks cross-org access
- [ ] Linear integration works (if configured)

---

## 📚 **Sample Test Files**

Create a test `.docx` file with:

```
Meeting Notes - Q1 Planning
Date: January 15, 2024

Attendees:
- Sarah (CEO)
- John (CTO)
- Mike (Product)

Decisions:
- Decided to launch new feature in Q2
- Will allocate $50K budget for marketing

Action Items:
- Sarah: Approve budget by Jan 20
- John: Complete technical spec by Feb 1
- Mike: Create user research plan by Jan 25

Key Discussion:
We need to prioritize the mobile app redesign...
```

Upload this and watch AI extract everything!

---

## 🎯 **Expected Results After Processing**

```json
{
  "meeting": {
    "id": "...",
    "title": "Q1 Planning",
    "date": "2024-01-15",
    "status": "completed"
  },
  "action_items": [
    {
      "title": "Approve budget",
      "owner_name": "Sarah",
      "due_date": "2024-01-20",
      "status": "open"
    },
    {
      "title": "Complete technical spec",
      "owner_name": "John",
      "due_date": "2024-02-01"
    }
  ],
  "decisions": [
    {
      "decision": "Launch new feature in Q2",
      "rationale": "Strategic priority for growth"
    },
    {
      "decision": "Allocate $50K marketing budget",
      "rationale": "Support feature launch"
    }
  ],
  "summary": {
    "content_md": "### Key Points\n- Q2 feature launch approved...",
    "type": "full"
  }
}
```

---

## 🚀 **Next Steps**

1. **Test basic upload** → Use `/upload-ui`
2. **Test with auth** → Create org, get token
3. **Test AI processing** → Upload real meeting notes
4. **Configure integrations** → Add Linear/Google keys
5. **Deploy to production** → Use production `.env` settings

---

## 💡 **Pro Tips**

- Use `/upload-ui` for quick testing (no auth needed)
- Check `/docs` for interactive API playground
- Use `python scripts/test_connection.py` to verify setup
- Monitor Celery logs to see AI processing in real-time
- Check Supabase Dashboard → Database → Tables to see extracted data

---

**Ready to test?** Start with:
```bash
cd backend && source venv/bin/activate && uvicorn app.main:app --reload
```

Then open: http://localhost:8000/upload-ui 🚀



