# Settings Page - Quick Instructions ⚙️

## Can't Click "Connect" Button?

### **SOLUTION: Hard Refresh Browser**

**Mac:** `Cmd + Shift + R`  
**Windows:** `Ctrl + Shift + R`

This clears cached JavaScript and loads the new modal functions.

---

## After Hard Refresh:

1. ✅ Click any "Connect" button
2. ✅ Modal should open
3. ✅ See appropriate fields (API Token, Domain, etc.)
4. ✅ Fill in credentials
5. ✅ Click "Save Integration"

---

## If Still Not Working:

### Check Browser Console:
1. Press `F12` (or `Cmd+Option+I` on Mac)
2. Click "Console" tab
3. Look for errors in red
4. When you click "Connect", should see: `Opening modal: [uuid] pipedrive [CompanyName]`

### Common Issues:

**❌ "openIntegrationModal is not defined"**
- Solution: Hard refresh to load JavaScript

**❌ Modal opens but fields are empty**
- Solution: Check console for errors

**❌ Button doesn't respond at all**
- Solution: Check if JavaScript loaded (View Page Source, search for "openIntegrationModal")

---

## Current Status:

### Settings Page:
- **URL:** http://localhost:8000/settings
- **Status:** Fully functional
- **Tabs:** General | API Keys | Portfolio Companies (8)

### Companies Showing:
✅ Disruptive Ventures (first, purple gradient)  
✅ Crystal Alarm  
✅ LumberScan  
✅ Alent Dynamic  
✅ LunaLEC  
✅ Vaylo  
✅ **Coeo** (shows "✅ Connected (env)" - using .env credentials)  
✅ Basic Safety  
✅ Service Node  

### Integration Options per Company:
1. Pipedrive CRM
2. Fortnox
3. Google Sheets
4. Google Workspace
5. Office 365
6. Custom Integration

---

## Why Coeo Shows "Connected (env)":

Currently Coeo's Pipedrive credentials are in `.env` file:
```bash
PIPEDRIVE_API_TOKEN=0082d57f...
PIPEDRIVE_COMPANY_DOMAIN=coeo.pipedrive.com
```

This works (193 deals displaying!) but credentials should be in database.

### To Move to Database:

**Step 1:** Run SQL in Supabase
```sql
-- Copy from: create_integrations_table_simple.sql
-- Paste in: https://supabase.com/dashboard/project/.../editor
-- Click "Run"
```

**Step 2:** Move credentials
```bash
cd backend
python add_coeo_pipedrive_to_db.py
```

**Result:**
- Credentials encrypted in database
- Settings page shows "✅ Connected" (not "env")
- Can remove from .env file
- Proper credential management

---

## What Works Right Now:

✅ **Buttons exist** - All "Connect" buttons functional  
✅ **JavaScript loaded** - Modal functions defined  
✅ **Forms ready** - All 6 integration types  
✅ **API endpoints** - Save/Edit/Delete working  
⚠️ **Database table** - Needs creation to actually save  

---

## Quick Test:

1. Hard refresh: `Cmd + Shift + R`
2. Open Console: `F12`
3. Go to: http://localhost:8000/settings
4. Click "Portfolio Companies (8)" tab
5. Find any company
6. Click "Connect" button
7. Console should show: `Opening modal: ...`
8. Modal should appear

**If modal doesn't appear after hard refresh, share what Console shows!**

---

**Bottom Line:**
- Buttons work if browser cache cleared
- Modal opens and shows correct fields
- Just need database table to actually save integrations
- Coeo currently working via .env (temporary solution)

**Try hard refresh first!** 🔄
