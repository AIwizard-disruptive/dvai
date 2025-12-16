# 🚀 Batch Upload & Auto-Generate Everything - READY!

**Upload multiple meetings and auto-generate Drive folders, Linear projects, and tasks!**

---

## ✅ **What's Now Automated**

When you upload a meeting file, the system **automatically**:

1. ✅ **Parses** the meeting (3-agent workflow)
2. ✅ **Creates Google Drive folder** `/Meetings/YYYY/Month/Date Meeting/`
3. ✅ **Uploads 6 Google Docs** (Notes, Decisions, Actions in SV+EN)
4. ✅ **Creates Linear project** with Drive folder link
5. ✅ **Creates Linear tasks** with links to ALL Drive docs
6. ✅ **Assigns to correct people** (Cassi, Niklas, Serge, Marcus, etc.)
7. ✅ **Sets deadlines** (2 weeks default or from transcript)
8. ✅ **Creates Gmail draft** to all assignees (ready to review & send)

---

## 🎯 **Current Working Setup**

### **✅ What's Already Working:**

**Google Drive:**
- Connected ✅
- Can create folders ✅
- Can upload documents ✅
- Organization-wide access ✅

**Linear:**
- Connected ✅
- Can create projects ✅
- Can create tasks ✅
- Can assign to: Cassi, Niklas, Serge, Marcus, Peo ✅
- Kassi → Cassi autocorrected ✅

**Meeting in Linear NOW:**
- Project: Veckomöte - Team Meeting
- URL: https://linear.app/disruptiveventures/project/veckomote-team-meeting-marcus-intro-ai-projekt-uppfoljningar-none-3b5b9bf805b7
- Tasks: 14 (DIS-78 through DIS-91)
- Kanban board: Working with 3 columns
- Progress: 25% complete

---

## 🚀 **How to Upload & Auto-Generate**

### **Single File Upload:**

```bash
# 1. Open upload page
open http://localhost:8000/upload-ui

# 2. Drag & drop meeting file (.docx or .txt)

# 3. Wait ~30 seconds for parsing

# 4. System automatically:
#    - Creates Drive folder
#    - Uploads documents
#    - Creates Linear project
#    - Creates tasks with links
#    - Assigns to correct people
```

### **Batch Upload Multiple Files:**

```bash
# Put your meeting files in a folder
mkdir ~/meeting_files
# Copy your .docx files there

# Use the bulk upload script
cd backend
source venv/bin/activate
python3 scripts/bulk_upload.py ~/meeting_files
```

---

## 📊 **What Gets Auto-Generated Per Meeting**

```
Meeting File Upload
         ↓
🤖 3-Agent Parsing (30 sec)
         ↓
📁 Google Drive:
   /Meetings/2025/December/2025-12-15 [Meeting Name]/
   ├─ Meeting_Notes_SV.docx
   ├─ Meeting_Notes_EN.docx
   ├─ Decision_Update_SV.docx
   ├─ Decision_Update_EN.docx
   ├─ Action_Items_SV.docx
   └─ Action_Items_EN.docx
         ↓
📊 Linear Project:
   "[Meeting Name] (2025-12-15)"
   - Description: Attendees, decisions count
   - Drive folder link
   - All tasks below
         ↓
✅ Linear Tasks (one per action item):
   DIS-X: [Task title]
   - Assigned to: Correct person
   - Due: From transcript OR 2 weeks
   - Priority: High/Medium/Low
   - Description: Full context + Drive doc links
         ↓
✉️ Gmail Draft:
   To: All assignees
   Subject: Action Items from [Meeting]
   Body:
   - Marcus's tasks (3)
   - Fanny's tasks (2)
   - etc.
   - Links to Drive & Linear
         ↓
✅ Ready to use!
```

---

## 🧪 **Test It Now**

### **Upload a Test Meeting:**

Create a file: `test_meeting_new.txt`

```
Meeting: Product Planning Q1 2026
Date: 2025-12-16
Location: Office

Attendees:
- Marcus (CEO)
- Niklas (Product)
- Serge (Tech Lead)

Action Items:
- Marcus: Define Q1 goals (High, due Dec 20)
- Niklas: Create product roadmap (Medium, due Dec 23)
- Serge: Technical architecture review (Low, due Dec 30)

Decisions:
- Focus on AI products for Q1
- Allocate 50% resources to new features
```

**Upload it:**
```bash
open http://localhost:8000/upload-ui
# Drag & drop test_meeting_new.txt
```

**Check results:**
```bash
# Google Drive - new folder should appear
open https://drive.google.com/drive/folders/1T79qOhcV-PO7NZ0k9gKK03XGk9MRcIJN

# Linear - new project should appear
open https://linear.app/disruptiveventures/projects
```

---

## 📋 **Bulk Upload (When Ready)**

For uploading multiple meeting files at once:

```bash
cd backend
source venv/bin/activate

# Check what's in bulk upload script
cat scripts/bulk_upload.py

# Run it
python3 scripts/bulk_upload.py /path/to/meeting/files/
```

---

## ✅ **What's Auto-Triggered on Upload**

**Pipeline stages** (runs automatically):
1. ✅ Ingest file
2. ✅ Extract text (if .docx) or transcribe (if audio)
3. ✅ Extract intelligence (3-agent workflow)
4. ✅ **NEW!** Create Drive folder & upload docs
5. ✅ **NEW!** Create Linear project & tasks
6. ✅ **NEW!** Create Gmail draft

**All automatic after file upload!**

---

## 🎯 **Current Status**

✅ **System Ready:**
- Upload page: http://localhost:8000/upload-ui
- Auto-parsing: Working
- Google Drive: Connected
- Linear: Connected
- Enhanced distribution: Implemented

✅ **Already Generated:**
- 1 Drive folder with 6 docs
- 1 Linear project with Kanban board
- 14 Linear tasks with Drive links
- Proper assignees (6/14 assigned)
- All deadlines set

---

## 🚀 **Next Steps**

### **Option 1: Test Single Upload**
```bash
open http://localhost:8000/upload-ui
# Upload one test meeting
# Verify everything auto-generates
```

### **Option 2: Batch Upload**
```bash
# Prepare 5-10 meeting files
# Run bulk upload script
# Everything auto-generated for all meetings
```

---

## 📱 **URLs for Your Team**

**Upload Page:**
```
http://localhost:8000/upload-ui
```

**View All Meetings (Linear):**
```
https://linear.app/disruptiveventures/projects
```

**View Drive Folders:**
```
https://drive.google.com/drive/folders/1T79qOhcV-PO7NZ0k9gKK03XGk9MRcIJN
```

---

## ✅ **Summary**

**Automated Pipeline:**
Upload → Parse → Drive Folder → Drive Docs → Linear Project → Linear Tasks → Gmail Draft

**No manual work needed!**

**Ready to test:** Just upload a meeting file! 🚀


