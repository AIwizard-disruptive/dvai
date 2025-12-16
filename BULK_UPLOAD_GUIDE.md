# Bulk Upload Guide

Process multiple Word documents at once and extract meeting intelligence from all of them.

## 🎯 What This Does

Upload 40+ Word files → AI processes all → Get:
- Meeting summaries
- Action items → Linear issues
- Decisions with context
- Email drafts
- Calendar proposals

All automatically!

---

## 📋 Meeting Notes Template

We've created a template for consistent meeting documentation:

**Location**: `templates/Meeting_Notes_Template.md`

### Template Structure

```markdown
# Meeting Information
- Title, Date, Type, Location
- Attendees with emails

# Discussion Notes
- Topic-by-topic breakdown
- Key points

# Decisions Made
- Clear statements with rationale

# Action Items
- [Who] will [what] by [when]
- With priorities and context

# Follow-up Meetings
- Next steps planned
```

### Why Use the Template?

✅ **Better AI extraction** - Structured format helps AI understand context  
✅ **Consistent format** - Easy to search across meetings  
✅ **Complete provenance** - Every insight links to source  
✅ **Clear ownership** - Action items have explicit owners  
✅ **Date precision** - AI extracts due dates accurately  

---

## 🚀 Bulk Upload Your 40 Files

### Option 1: Automated Script (Recommended)

**Install dependencies:**
```bash
cd backend
source venv/bin/activate
pip install rich httpx
```

**Set environment variables:**
```bash
export SUPABASE_TOKEN="your-auth-token-here"
export ORG_ID="your-org-id-here"
export API_URL="http://localhost:8000"  # optional, defaults to localhost
```

**Upload all files in a directory:**
```bash
python scripts/bulk_upload.py /path/to/your/word/files/
```

**Or specific files:**
```bash
python scripts/bulk_upload.py /path/to/files/*.docx
```

**What happens:**
```
✓ Found 40 Word file(s)

Uploading files... ████████████████████ 100% 40/40

✓ Uploaded: 40/40

Upload Results
┌─────────────────────────┬─────────┬──────────────┐
│ File                    │ Status  │ Details      │
├─────────────────────────┼─────────┼──────────────┤
│ meeting_2025_01.docx   │ ✓ Success│ ID: abc123.. │
│ meeting_2025_02.docx   │ ✓ Success│ ID: def456.. │
│ ...                     │ ...     │ ...          │
└─────────────────────────┴─────────┴──────────────┘
```

---

### Option 2: Web UI (Coming Soon)

Upload via dashboard:
1. Go to `http://localhost:3000/dashboard/upload`
2. Click "Bulk Upload"
3. Select multiple files
4. Click "Upload All"

---

### Option 3: API Script

**Create a simple upload script:**

```bash
#!/bin/bash
# upload_all.sh

TOKEN="your-token"
ORG_ID="your-org-id"
API_URL="http://localhost:8000"

for file in /path/to/files/*.docx; do
    echo "Uploading: $file"
    curl -X POST "$API_URL/artifacts/upload" \
        -H "Authorization: Bearer $TOKEN" \
        -H "X-Org-Id: $ORG_ID" \
        -F "file=@$file"
    echo ""
done
```

Make it executable and run:
```bash
chmod +x upload_all.sh
./upload_all.sh
```

---

## 📊 What Gets Extracted

For each Word file, the AI extracts:

### 1. Meeting Metadata
- Title (from filename or content)
- Date (parsed from filename or content)
- Type (standup, planning, review, etc.)
- Company/project
- Participants

### 2. Content Analysis
- **Summary**: Concise overview (2-3 paragraphs)
- **Key Points**: Main discussion topics
- **Decisions**: What was decided and why
- **Action Items**: Tasks with owners and due dates
- **Entities**: People, companies, products mentioned
- **Tags**: Categorization

### 3. Automatic Sync
- **Linear**: Issues created for action items
- **Gmail**: Draft follow-up emails
- **Calendar**: Meeting proposals

---

## 🎨 Filename Best Practices

For best results, use descriptive filenames:

✅ **Good filenames:**
```
2025-12-10_ProductPlanning_AcmeCorp.docx
Standup_2025-12-12_Engineering.docx
Q4_Review_Board_Meeting.docx
CustomerCall_BigClient_2025-12-08.docx
```

❌ **Poor filenames:**
```
Meeting1.docx
Notes.docx
Doc123.docx
Untitled.docx
```

The AI uses filenames to infer:
- Meeting date
- Meeting type
- Company/client
- Department/team

---

## 📁 Organizing Your Files

**Before upload, organize by quarter/month:**

```
meetings/
├── 2025-Q4/
│   ├── October/
│   │   ├── 2025-10-05_Standup.docx
│   │   ├── 2025-10-12_Planning.docx
│   │   └── 2025-10-19_Review.docx
│   ├── November/
│   └── December/
├── 2025-Q3/
└── 2025-Q2/
```

**Upload by directory:**
```bash
python scripts/bulk_upload.py meetings/2025-Q4/October/
python scripts/bulk_upload.py meetings/2025-Q4/November/
python scripts/bulk_upload.py meetings/2025-Q4/December/
```

---

## ⚙️ Processing Details

### Timeline
```
Upload 40 files
    ↓ ~1 minute
All uploaded to Supabase Storage
    ↓ ~5-10 minutes (parallel)
Text extracted from all files
    ↓ ~10-15 minutes (parallel)
AI extraction complete
    ↓ ~2-3 minutes
Sync to integrations
    ↓
✓ Done!
```

**Total time for 40 files**: ~20-30 minutes

### Monitoring Progress

**Check Celery worker logs:**
```bash
# In terminal where Celery is running
# You'll see processing status for each file
```

**Check meeting status via API:**
```bash
curl http://localhost:8000/meetings \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" \
  | jq '.[] | {title, status: .processing_status}'
```

**View processing runs:**
```bash
curl http://localhost:8000/meetings/{meeting_id}/runs \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

---

## 🔍 After Upload - Search & Filter

### View All Meetings
```bash
curl http://localhost:8000/meetings \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

### Filter by Status
```bash
# Only completed
curl http://localhost:8000/meetings?status=completed

# Still processing
curl http://localhost:8000/meetings?status=processing

# Failed (to retry)
curl http://localhost:8000/meetings?status=failed
```

### Filter by Date Range
```bash
# Meetings from last 30 days
curl http://localhost:8000/meetings?since=30d

# Meetings in Q4 2025
curl http://localhost:8000/meetings?start_date=2025-10-01&end_date=2025-12-31
```

### Search by Company/Type
```bash
# All Acme Corp meetings
curl http://localhost:8000/meetings?company=Acme

# All standups
curl http://localhost:8000/meetings?type=standup
```

---

## 📊 Bulk Analytics

### Get Action Item Summary
```sql
-- Run in Supabase SQL editor
SELECT 
  m.title as meeting,
  m.meeting_date,
  COUNT(a.id) as action_items,
  SUM(CASE WHEN a.status = 'done' THEN 1 ELSE 0 END) as completed,
  SUM(CASE WHEN a.status = 'open' THEN 1 ELSE 0 END) as open
FROM meetings m
LEFT JOIN action_items a ON m.id = a.meeting_id
WHERE m.org_id = 'your-org-id'
GROUP BY m.id, m.title, m.meeting_date
ORDER BY m.meeting_date DESC;
```

### Get Decisions Summary
```sql
SELECT 
  m.title as meeting,
  COUNT(d.id) as decisions_made,
  AVG(d.confidence) as avg_confidence
FROM meetings m
LEFT JOIN decisions d ON m.id = d.meeting_id
WHERE m.org_id = 'your-org-id'
GROUP BY m.id, m.title
ORDER BY decisions_made DESC;
```

---

## 🔧 Troubleshooting

### Files Not Processing

**Check Celery is running:**
```bash
celery -A app.worker.celery_app inspect active
```

**Check Redis:**
```bash
redis-cli ping
# Should return: PONG
```

**Restart worker:**
```bash
celery -A app.worker.celery_app worker --loglevel=info
```

### Extraction Quality Issues

**Use the template** - Structured format helps AI significantly

**Check file format:**
```bash
file your-meeting.docx
# Should be: Microsoft Word 2007+
```

**Validate content:**
- Has clear sections
- Uses headers/bold for topics
- Includes participant names
- Has date information

### Upload Failures

**Check token:**
```bash
curl http://localhost:8000/health \
  -H "Authorization: Bearer $TOKEN"
```

**Check org membership:**
```bash
curl http://localhost:8000/orgs \
  -H "Authorization: Bearer $TOKEN"
```

**File size limit:**
- Max: 50MB per file
- If larger, split into multiple files

---

## 📈 Best Practices

### 1. Start Small
Upload 5 files first, review results, then upload all 40

### 2. Use Template
Convert existing notes to template format for consistency

### 3. Review AI Output
Check first few extractions for accuracy, adjust template if needed

### 4. Batch by Time Period
Upload month-by-month for easier tracking

### 5. Monitor Resources
Watch Celery worker memory usage with many concurrent uploads

### 6. Backup First
Keep originals safe before any conversion

---

## ✅ Bulk Upload Checklist

- [ ] Backend running with Celery worker
- [ ] Redis running
- [ ] OpenAI API key configured
- [ ] Auth token obtained
- [ ] Org ID obtained
- [ ] Files organized with good names
- [ ] Template reviewed (optional)
- [ ] Bulk upload script installed
- [ ] Environment variables set
- [ ] Test upload with 1-2 files
- [ ] Monitor first few completions
- [ ] Upload all 40 files
- [ ] Verify in meetings list
- [ ] Check Linear/Gmail/Calendar syncs
- [ ] Review extraction quality

---

## 🎯 Quick Start Commands

```bash
# 1. Setup
cd backend
source venv/bin/activate
pip install rich httpx

# 2. Configure
export SUPABASE_TOKEN="your-token"
export ORG_ID="your-org-id"

# 3. Upload
python scripts/bulk_upload.py /path/to/your/40/files/

# 4. Monitor
curl http://localhost:8000/meetings | jq '.[] | {title, status: .processing_status}'

# 5. View results
curl http://localhost:8000/meetings/{meeting_id}
```

---

**Ready to process those 40 files? Let's do it! 🚀**




