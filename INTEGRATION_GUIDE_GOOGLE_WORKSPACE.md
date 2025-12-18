# How to Connect Google Workspace - Step-by-Step Guide ☁️

**For:** Gmail, Drive, Calendar, Contacts  
**Difficulty:** ⭐⭐ Moderate (20 minutes)  
**Required Access:** Google Cloud Console admin

---

## What You'll Get

Once connected, you'll be able to:
- ✅ Send automated emails to founders and customers
- ✅ Store company documents in Google Drive
- ✅ Create and manage calendar events (board meetings)
- ✅ Sync contacts across companies
- ✅ Integrate with Gmail for communications

---

## Prerequisites

You need:
1. A Google Workspace account (yourcompany@gmail.com or custom domain)
2. Access to Google Cloud Console
3. Admin rights to create projects and enable APIs

---

## Step 1: Create Google Cloud Project

### 1A: Go to Google Cloud Console
Open: https://console.cloud.google.com

### 1B: Create New Project (or select existing)
1. Click the project dropdown (top left, near "Google Cloud")
2. Click **"New Project"**
3. Project name: `DV Portfolio Platform`
4. Organization: Select your organization
5. Click **"Create"**
6. Wait 10-15 seconds for project to be created

---

## Step 2: Enable Required APIs

### 2A: Go to APIs & Services
1. In the left menu, click **"APIs & Services"**
2. Click **"Library"**

### 2B: Enable These APIs (one by one):

**For Email:**
1. Search: "Gmail API"
2. Click on it
3. Click **"Enable"**

**For Files:**
1. Search: "Google Drive API"
2. Click on it
3. Click **"Enable"**

**For Calendar:**
1. Search: "Google Calendar API"
2. Click on it
3. Click **"Enable"**

**For Contacts:**
1. Search: "People API" (or "Contacts API")
2. Click on it
3. Click **"Enable"**

**This takes about 2-3 minutes total**

---

## Step 3: Create OAuth Client

### 3A: Go to Credentials
1. Click **"APIs & Services"** in left menu
2. Click **"Credentials"**
3. Click **"+ Create Credentials"** (top of page)
4. Select **"OAuth client ID"**

### 3B: Configure OAuth Consent Screen (if prompted)
1. Click **"Configure Consent Screen"**
2. User Type: **"Internal"** (if Google Workspace) or **"External"**
3. Click **"Create"**

**Fill in App Information:**
- App name: `DV Portfolio Platform`
- User support email: Your email
- Developer contact: Your email
- Click **"Save and Continue"**

**Scopes:** Skip for now (click "Save and Continue")

**Test users:** Skip for now (click "Save and Continue")

Click **"Back to Dashboard"**

### 3C: Create OAuth Client ID
1. Back to Credentials page
2. Click **"+ Create Credentials"** → **"OAuth client ID"**
3. Application type: **"Web application"**
4. Name: `DV Portfolio Web Client`

**Authorized redirect URIs:**
Add this URL:
```
http://localhost:8000/integrations/google/callback
```

Click **"Create"**

### 3D: Copy Your Credentials
A popup appears with:
- **Client ID**: Looks like `123456-abcdef.apps.googleusercontent.com`
- **Client Secret**: Looks like `GOCSPX-abc123def456`

**Click the download icon** to save as JSON (optional)  
**Or copy both values** to a notepad

---

## Step 4 (Optional): Create Service Account

**For server-to-server access** (no user login required):

### 4A: Create Service Account
1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ Create Credentials"** → **"Service account"**
3. Service account name: `dv-portfolio-service`
4. Description: `Service account for portfolio platform`
5. Click **"Create and Continue"**

**Grant access:** Skip (click "Continue")

**Grant users access:** Skip (click "Done")

### 4B: Create Key
1. Find your new service account in the list
2. Click on it
3. Go to **"Keys"** tab
4. Click **"Add Key"** → **"Create new key"**
5. Key type: **JSON**
6. Click **"Create"**
7. A JSON file downloads automatically
8. **Save this file securely!**

### 4C: Note Service Account Email
It looks like:
```
dv-portfolio-service@project-id.iam.gserviceaccount.com
```

Copy this email address.

### 4D: Share Resources with Service Account

**For Google Drive:**
- Share specific folders with the service account email
- Give "Viewer" or "Editor" access

**For Google Calendar:**
- Share calendars with the service account email
- Give appropriate permissions

**For Gmail:**
- Enable domain-wide delegation (advanced)
- Or use OAuth for user-level access

---

## Step 5: Enable Domain-Wide Delegation (Optional, Advanced)

**Only if you want full workspace access:**

1. Go to your service account
2. Click **"Show Domain-Wide Delegation"**
3. Enable **"Enable Google Workspace Domain-wide Delegation"**
4. Note the **Client ID** (numeric, like 123456789)

5. Go to Google Workspace Admin Console:
   ```
   https://admin.google.com
   ```

6. Security → API Controls → Domain-wide Delegation
7. Click **"Add new"**
8. Client ID: (paste the numeric ID)
9. OAuth Scopes: Add these:
   ```
   https://www.googleapis.com/auth/gmail.readonly
   https://www.googleapis.com/auth/gmail.send
   https://www.googleapis.com/auth/drive.readonly
   https://www.googleapis.com/auth/calendar
   https://www.googleapis.com/auth/contacts.readonly
   ```
10. Click **"Authorize"**

---

## Step 6: Add to DV Platform

### 6A: Go to Settings Page
```
http://localhost:8000/settings
```

### 6B: Click Portfolio Companies Tab
- Third tab: "Portfolio Companies (8)"

### 6C: Find Your Company
- Scroll to find the company
- Or if it's for DV itself, it's the first card (with purple border)

### 6D: Click "Connect" on Google Workspace
- Look for the box labeled **"Google Workspace"**
- Description: "Gmail, Drive, Calendar"
- Click **"Connect"**

### 6E: Fill in the Form

**Client ID:**
```
Paste your Client ID here
(looks like: 123456-abc.apps.googleusercontent.com)
```

**Client Secret:**
```
Paste your Client Secret here
(looks like: GOCSPX-abc123def456)
```

**Service Account Email (optional):**
```
If you created service account, paste email:
dv-portfolio-service@project-id.iam.gserviceaccount.com

Leave blank if only using OAuth
```

### 6F: Click "Save Integration"
- Bottom right button
- Wait for confirmation: **"✅ Integration saved successfully!"**
- Page reloads
- Status changes to **"✅ Connected"**

---

## Step 7: Test the Integration

### Test Email Access:
```python
# Future endpoint: /integrations/google/test-email
# Will send a test email
```

### Test Drive Access:
```python
# Future endpoint: /integrations/google/test-drive
# Will list accessible folders
```

### Test Calendar Access:
```python
# Future endpoint: /integrations/google/test-calendar
# Will list upcoming events
```

---

## What Data Gets Mapped

### Gmail → DV Platform:
- **Inbox**: Read emails for context
- **Sent**: Track outgoing communications
- **Drafts**: Auto-generate follow-ups
- **Labels**: Organize by company/topic

### Google Drive → DV Platform:
- **Folders**: Board materials, financials, contracts
- **Documents**: Meeting notes, reports
- **Spreadsheets**: KPI data (use Google Sheets integration)
- **Attachments**: Link to relevant deals/companies

### Google Calendar → DV Platform:
- **Events**: Board meetings, 1-on-1s, quarterly reviews
- **Attendees**: Link to people in database
- **Notes**: Meeting prep and follow-ups
- **Reminders**: Action items

### Google Contacts → DV Platform:
- **Contacts**: Sync to people table
- **Organizations**: Sync to organizations table
- **Email addresses**: Keep up-to-date
- **Phone numbers**: Contact information

---

## Use Cases

### For Disruptive Ventures:
1. **Email founders** with quarterly updates
2. **Store board materials** in Drive
3. **Schedule board meetings** via Calendar
4. **Manage LP contacts** via Contacts

### For Portfolio Companies:
1. **Customer communication** via Gmail
2. **Document collaboration** via Drive
3. **Meeting scheduling** with customers
4. **Contact database** sync

---

## Scopes Required

When users authorize, they'll be asked to grant:

```
Read, compose, and send emails (Gmail)
View and manage files in Google Drive
View and manage calendars
View contact information
```

Users can revoke access anytime via:
https://myaccount.google.com/permissions

---

## Common Issues

### ❌ "Access denied"
- Enable all required APIs in Cloud Console
- Check OAuth consent screen is configured
- Verify redirect URI is correct

### ❌ "Invalid client"
- Check Client ID is correct
- Check Client Secret is correct
- Both case-sensitive!

### ❌ "Insufficient permissions"
- Add required scopes to OAuth consent screen
- Re-authorize after adding scopes

---

## Cost

**FREE** for reasonable usage:
- Gmail API: 1 billion quota units/day (very generous)
- Drive API: 20,000 requests/day per user
- Calendar API: 1,000,000 requests/day
- Contacts API: 600 requests/minute

You won't hit these limits with normal use!

---

## Summary Checklist

- [ ] Create Google Cloud project
- [ ] Enable APIs (Gmail, Drive, Calendar, People)
- [ ] Create OAuth client ID
- [ ] Set redirect URI
- [ ] Copy Client ID and Secret
- [ ] (Optional) Create service account
- [ ] (Optional) Download service account JSON
- [ ] (Optional) Share resources with service account
- [ ] Go to http://localhost:8000/settings
- [ ] Portfolio Companies tab
- [ ] Find company
- [ ] Connect Google Workspace
- [ ] Paste credentials
- [ ] Save
- [ ] See "✅ Connected"
- [ ] Test functionality

---

**Time Required:** 20 minutes  
**Technical Knowledge:** Following screenshots/instructions  
**Result:** Full Google Workspace integration! 📧📁📅

---

**Questions?** Check Google Cloud Console docs or ask your team's technical lead!

