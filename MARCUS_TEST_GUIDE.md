# 🧪 Marcus Test Guide - Google Drive & Gmail

**Test the enhanced distribution with YOUR Google account first**

---

## 🎯 Goal

Create Drive folders and Gmail drafts for **Marcus only** first.  
Once it works perfectly, roll out to the whole team.

---

## ✅ What's Already Working

✅ **Linear:** Connected (API key configured)
✅ **Test page:** Ready at http://localhost:8000/marcus-test
✅ **Test endpoints:** Built and working

---

## 🚀 Quick Start (10 Minutes)

### **Step 1: Enable Google Drive API (2 min)**

```bash
# Open Google Cloud Console
open https://console.cloud.google.com/apis/library/drive.googleapis.com

# Click the blue "ENABLE" button
# Wait 10 seconds for it to enable
```

### **Step 2: Enable Gmail API (1 min)**

```bash
# Open Gmail API page
open https://console.cloud.google.com/apis/library/gmail.googleapis.com

# Click the blue "ENABLE" button
# Wait 10 seconds
```

### **Step 3: Add Required Scopes (3 min)**

```bash
# Open OAuth consent screen
open https://console.cloud.google.com/apis/credentials/consent

# Click "EDIT APP" button
# Scroll to "Scopes for Google APIs"
# Click "ADD OR REMOVE SCOPES"
```

**Add these scopes:**
```
https://www.googleapis.com/auth/drive
https://www.googleapis.com/auth/drive.file
https://www.googleapis.com/auth/gmail.compose
https://www.googleapis.com/auth/gmail.send
https://www.googleapis.com/auth/gmail.readonly
```

**Steps:**
1. Paste each URL in the filter box
2. Check the checkbox
3. Click "UPDATE" at bottom
4. Click "SAVE AND CONTINUE"

### **Step 4: Add Yourself as Test User (1 min)**

Still on OAuth consent screen:
- Scroll to "Test users"
- Click "+ ADD USERS"
- Add: `wizard@disruptiveventures.se` (your email)
- Click "SAVE"

### **Step 5: Open Marcus Test Page (30 sec)**

```bash
# Open the test page
open http://localhost:8000/marcus-test

# You'll see:
# - Status checklist
# - Buttons to enable Google
# - Test buttons for Drive, Gmail, Full flow
```

### **Step 6: Connect Your Google Account (2 min)**

On the Marcus Test page:
1. Click **"Connect Google Account"** button
2. Sign in with `wizard@disruptiveventures.se`
3. Click **"Allow"** for all permissions
4. You'll be redirected back to the app

### **Step 7: Test Drive Folder Creation (30 sec)**

On the Marcus Test page:
1. Click **"Create Test Drive Folder"** button
2. Wait a few seconds
3. Click the **"Open in Google Drive"** link
4. Verify folder created: `/Meetings/2025/December/2025-12-15 Marcus Test Meeting/`

### **Step 8: Test Gmail Draft Creation (30 sec)**

On the Marcus Test page:
1. Click **"Create Test Gmail Draft"** button
2. Wait a few seconds
3. Click **"Open Gmail Drafts"** link
4. Verify draft is in your Drafts folder

### **Step 9: Run Full Test (1 min)**

On the Marcus Test page:
1. Click **"Run Full Test (Drive + Linear + Gmail)"** button
2. Wait ~30 seconds
3. Check results:
   - ✅ Drive folder created
   - ✅ Documents uploaded
   - ✅ Linear project created
   - ✅ Linear tasks created
   - ✅ Gmail draft created

### **Step 10: Verify Everything (2 min)**

**Check Google Drive:**
```bash
open https://drive.google.com

# Look for: /Meetings/2025/December/
# Should see folder with test documents
```

**Check Linear:**
```bash
open https://linear.app

# Look in Projects tab
# Should see: "Marcus Enhanced Distribution Test (2025-12-15)"
# Click it - should have 3 tasks
```

**Check Gmail:**
```bash
open https://mail.google.com/mail/#drafts

# Should see draft: "📋 Action Items from Marcus Enhanced Distribution Test"
# Open it - should show all 3 tasks with links
```

---

## 📊 What Gets Created (Marcus Test)

### **Google Drive:**
```
/Meetings/
  /2025/
    /December/
      /2025-12-15 Marcus Enhanced Distribution Test/
        ├─ Meeting_Notes_SV.docx
        ├─ Meeting_Notes_EN.docx
        ├─ Decision_Update_SV.docx
        ├─ Decision_Update_EN.docx
        ├─ Action_Items_SV.docx
        └─ Action_Items_EN.docx
```

### **Linear:**
```
Project: "Marcus Enhanced Distribution Test (2025-12-15)"

Tasks:
├─ DIS-X: Review Google Drive integration [HIGH] - Marcus
├─ DIS-Y: Test Gmail draft creation [MEDIUM] - Marcus
└─ DIS-Z: Verify Linear project linking [LOW] - Marcus

Each task description includes:
- Meeting context
- Links to ALL Drive documents
- Link to project
```

### **Gmail:**
```
Draft to: marcus@disruptiveventures.se

Subject: 📋 Action Items from Marcus Enhanced Distribution Test

Body:
- Summary
- Marcus's Tasks (3 tasks listed)
- Links to Drive folder
- Links to Linear project
- Links to all documents
```

---

## 🔧 Troubleshooting

### **"Google not connected"**

**Fix:**
```bash
# Make sure you clicked "Connect Google Account"
# and authorized access
open http://localhost:8000/marcus-test
# Click the Connect button again
```

### **"API not enabled"**

**Fix:**
```bash
# Enable the APIs in Google Cloud Console
open https://console.cloud.google.com/apis/library

# Search for: "Gmail API"
# Click "ENABLE"

# Search for: "Drive API"  
# Click "ENABLE"

# Wait 1-2 minutes for propagation
```

### **"Insufficient permissions"**

**Fix:**
```bash
# Check OAuth consent screen has all scopes
open https://console.cloud.google.com/apis/credentials/consent

# Verify these scopes are added:
# - drive.file
# - gmail.compose
# - gmail.send
```

### **"No drafts in Gmail"**

**Check:**
1. Draft might be in **"All Mail"** folder
2. Try searching for: `in:draft "Action Items"`
3. Check Spam folder (unlikely but possible)
4. Check server logs for errors

---

## 🎯 Success Criteria

You know it works when:

- [ ] Marcus Test page loads successfully
- [ ] Status shows Linear connected
- [ ] Status shows Google connected
- [ ] Drive folder test creates folder
- [ ] Can open Drive folder in browser
- [ ] Gmail draft test creates draft
- [ ] Can see draft in Gmail Drafts
- [ ] Full test creates everything
- [ ] Linear project appears with tasks
- [ ] Tasks have Drive doc links
- [ ] Everything cross-linked

---

## 🚀 After Marcus Test Works

### **Next Steps:**

**1. Run database migrations:**
```sql
-- In Supabase SQL Editor
-- Run: migrations/005_user_integrations.sql
-- Run: migrations/006_linear_user_mappings.sql
```

**2. Enable user-level integrations:**
- Users can connect their own Google accounts
- Each person gets their own Drive folders
- Each person's drafts in their own Gmail

**3. Roll out to team:**
- Share integration settings page
- Team members click "Connect"
- Everyone set up in 30 seconds each

---

## 📖 Test URLs

| Page | URL |
|------|-----|
| **Marcus Test Page** | http://localhost:8000/marcus-test |
| **Google Connect** | http://localhost:8000/integrations/google/connect |
| **Integration Status** | http://localhost:8000/integrations/summary |
| **Upload (Real Test)** | http://localhost:8000/upload-ui |

---

## 🎬 Demo Script

**To show your team:**

1. Open Marcus Test page
2. Click "Run Full Test"
3. Open Google Drive → Show folder
4. Open Linear → Show project with tasks
5. Open Gmail Drafts → Show consolidated email
6. Click any link in email → Goes to right doc
7. "This happens automatically for every meeting!"

---

## ⏱️ Time Required

- Enable APIs: 3 min
- Add scopes: 3 min
- Connect Google: 2 min
- Run tests: 2 min
- **Total: 10 minutes**

---

## ✅ Checklist

Before starting:
- [ ] Linear is connected (already done ✅)
- [ ] Server is running on port 8000
- [ ] You have access to Google Cloud Console
- [ ] You have wizard@disruptiveventures.se account

Setup:
- [ ] Enable Drive API
- [ ] Enable Gmail API
- [ ] Add scopes to OAuth
- [ ] Add test user (yourself)
- [ ] Connect Google account

Testing:
- [ ] Open Marcus Test page
- [ ] Test Drive folder creation
- [ ] Test Gmail draft creation
- [ ] Run full test
- [ ] Verify in Drive
- [ ] Verify in Linear
- [ ] Verify in Gmail

---

## 🎉 Ready!

**Everything is built and ready to test!**

**Next:** Open the Marcus Test page and let's see it work!

```bash
open http://localhost:8000/marcus-test
```

---

**Let me know when you're ready to start the Google setup!** 🚀



