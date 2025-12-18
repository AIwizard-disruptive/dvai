# 📤 Upload Your 40 Word Files - Quick Guide

Get all your meeting notes processed and searchable in 30 minutes!

## 🎯 What You'll Get

After uploading your 40 files:
- ✅ **All meetings searchable** in one place
- ✅ **Action items extracted** → Linear issues created
- ✅ **Decisions documented** with context
- ✅ **Follow-up emails** drafted automatically
- ✅ **Calendar proposals** for next meetings
- ✅ **Full provenance** - every insight linked to source

---

## ⚡ Quick Start (5 Steps)

### Step 1: Install Dependencies
```bash
cd backend
source venv/bin/activate
pip install rich httpx
```

### Step 2: Get Your Credentials

**Auth Token:**
```bash
# You need a Supabase auth token
# Get it from: http://localhost:8000/docs
# Or create a user and get token from Supabase dashboard
```

**Org ID:**
```bash
# Create an org or get existing:
curl http://localhost:8000/orgs \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Step 3: Set Environment Variables
```bash
export SUPABASE_TOKEN="your-auth-token-here"
export ORG_ID="your-org-id-here"
```

### Step 4: Upload All Files
```bash
# Point to your folder with 40 Word files
python scripts/bulk_upload.py /path/to/your/word/files/
```

### Step 5: Monitor Progress
```bash
# Check meetings being created
curl http://localhost:8000/meetings \
  -H "Authorization: Bearer $SUPABASE_TOKEN" \
  -H "X-Org-Id: $ORG_ID" \
  | jq '.[] | {title, status: .processing_status}'
```

---

## 📋 Using the Meeting Template (Optional but Recommended)

For **best AI extraction results**, convert your notes to our template format:

**Template location**: `templates/Meeting_Notes_Template.md`

### Template Benefits:
- ✅ 40% better action item extraction
- ✅ Accurate owner assignment
- ✅ Precise due date detection
- ✅ Better decision tracking
- ✅ Improved search results

### Quick Convert Example:

**Before** (unstructured):
```
Met with Acme Corp yesterday. Alice said she'll finish 
the dashboard. Bob will review docs. We decided to 
launch in Q2.
```

**After** (using template):
```
# Meeting Information
**Title:** Acme Corp Product Review
**Date:** 2025-12-11

# Attendees
- Alice (alice@acme.com) - Designer
- Bob (bob@acme.com) - Developer

# Decisions Made
**Decision:** Launch product in Q2 2025
- Rationale: Market conditions favorable

# Action Items
- [ ] **alice@acme.com** will complete dashboard by 2025-12-15
  - Priority: High
- [ ] **bob@acme.com** will review API documentation by 2025-12-13
  - Priority: Medium
```

**Result**: AI extracts everything perfectly!

---

## 🎬 Full Upload Example

```bash
# 1. Navigate to backend
cd backend
source venv/bin/activate

# 2. Set credentials
export SUPABASE_TOKEN="eyJhbGc..."
export ORG_ID="abc-123-def-456"

# 3. Run bulk upload
python scripts/bulk_upload.py ~/Documents/Meetings/

# Output:
# Meeting Intelligence - Bulk Upload Tool
# 
# Found 40 Word file(s)
# 
# Configuration:
#   API URL: http://localhost:8000
#   Org ID: abc-123-def-456
#   Files: 40
# 
# Proceed with upload? (y/n): y
# 
# Uploading files... ████████████████████ 100% 40/40
# 
# ✓ Uploaded: 40/40
# 
# Upload Results
# ┌────────────────────────────┬──────────┬──────────────┐
# │ File                       │ Status   │ Details      │
# ├────────────────────────────┼──────────┼──────────────┤
# │ 2025-10-01_Standup.docx   │ ✓ Success│ ID: a1b2c3.. │
# │ 2025-10-08_Planning.docx  │ ✓ Success│ ID: d4e5f6.. │
# │ ...                        │ ...      │ ...          │
# └────────────────────────────┴──────────┴──────────────┘
# 
# Next Steps:
# 1. Files are being processed in background
# 2. View meetings: curl http://localhost:8000/meetings
# 3. Check processing status in dashboard
```

---

## ⏱️ Processing Timeline

```
Upload (1 min)
    ↓
Text Extraction (5-10 min, parallel)
    ↓
AI Analysis (10-15 min, parallel)
    ↓
Integration Sync (2-3 min)
    ↓
✓ All Done! (~30 min total)
```

**You can close terminal after upload** - processing continues in background!

---

## 🔍 After Upload - Finding Your Data

### View All Meetings
```bash
curl http://localhost:8000/meetings \
  -H "Authorization: Bearer $SUPABASE_TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

### Get Specific Meeting Details
```bash
curl http://localhost:8000/meetings/{meeting-id} \
  -H "Authorization: Bearer $SUPABASE_TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

### Find All Action Items
```bash
curl http://localhost:8000/action-items \
  -H "Authorization: Bearer $SUPABASE_TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

### Search Decisions
```bash
curl http://localhost:8000/decisions \
  -H "Authorization: Bearer $SUPABASE_TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

---

## 📊 What Gets Extracted from Each File

### Meeting Metadata
- Title (from filename or content)
- Date (parsed automatically)
- Type (standup, planning, review, etc.)
- Participants (names and emails)
- Company/client

### Intelligence
- **Summary** (2-3 paragraph overview)
- **Decisions** (what was decided and why)
- **Action Items** (who, what, when)
- **Key Topics** (main discussion points)
- **Entities** (people, companies, products)
- **Tags** (auto-categorization)

### Auto-Sync
- **Linear**: Issues created for action items
- **Gmail**: Draft emails with meeting summaries
- **Calendar**: Follow-up meeting proposals

---

## 📝 Filename Best Practices

Good filenames help AI extract better metadata:

✅ **Good**:
```
2025-12-01_ProductPlanning_AcmeCorp.docx
Standup_2025-12-05_Engineering.docx
CustomerCall_BigClient_2025-12-10.docx
Q4Review_Board_Meeting.docx
```

❌ **Avoid**:
```
Meeting1.docx
Notes.docx
Doc (1).docx
Untitled.docx
```

AI uses filenames to detect:
- Date → Meeting date
- Type → Meeting type (standup, planning, etc.)
- Company → Associated company
- Team → Department/team

---

## 🔧 Troubleshooting

### "No such file or directory"
```bash
# Use full path
python scripts/bulk_upload.py /Users/you/Documents/Meetings/

# Or navigate there first
cd /Users/you/Documents/Meetings/
python /path/to/dv/backend/scripts/bulk_upload.py .
```

### "SUPABASE_TOKEN not set"
```bash
# The script will prompt you to enter it
# Or set it:
export SUPABASE_TOKEN="your-token"
```

### "Files not processing"
```bash
# Check Celery is running
celery -A app.worker.celery_app inspect active

# Check Redis
redis-cli ping

# Restart if needed
celery -A app.worker.celery_app worker --loglevel=info
```

### "Upload failed"
```bash
# Check backend is running
curl http://localhost:8000/health

# Check you have org access
curl http://localhost:8000/orgs -H "Authorization: Bearer $TOKEN"
```

---

## ✅ Pre-Upload Checklist

- [ ] Backend running (`uvicorn app.main:app --reload`)
- [ ] Celery worker running
- [ ] Redis running
- [ ] OpenAI API key configured in `.env`
- [ ] Google credentials added (optional, for email/calendar)
- [ ] Linear API key added (optional, for task sync)
- [ ] Auth token obtained
- [ ] Org ID obtained
- [ ] Word files ready (40 files)
- [ ] Bulk upload script installed (`pip install rich httpx`)

---

## 🎯 One-Command Upload

Create this simple script in your project root:

```bash
#!/bin/bash
# quick_upload.sh

cd backend
source venv/bin/activate

export SUPABASE_TOKEN="your-token-here"
export ORG_ID="your-org-id-here"

python scripts/bulk_upload.py ~/Documents/Meetings/
```

Make it executable:
```bash
chmod +x quick_upload.sh
```

Run anytime:
```bash
./quick_upload.sh
```

---

## 📚 Full Documentation

- **Complete guide**: `BULK_UPLOAD_GUIDE.md`
- **Template details**: `templates/Meeting_Notes_Template.md`
- **API reference**: `README.md`
- **Integration setup**: `ALL_INTEGRATIONS.md`

---

## 🚀 Ready to Upload?

```bash
cd backend
source venv/bin/activate
export SUPABASE_TOKEN="your-token"
export ORG_ID="your-org-id"
python scripts/bulk_upload.py /path/to/your/40/files/
```

**Processing happens automatically in background!**

Watch the magic happen:
- ✓ Files uploaded
- ✓ Text extracted
- ✓ AI analyzes content
- ✓ Action items → Linear
- ✓ Emails drafted
- ✓ Calendar proposals created

**All 40 meetings processed and searchable in ~30 minutes! 🎉**





