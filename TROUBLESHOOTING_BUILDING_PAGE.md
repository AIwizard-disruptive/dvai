# Troubleshooting - Building Page Not Switching

## Issue
Cannot switch between tabs or companies on Building Companies page.

## Likely Cause
Browser cache is serving old JavaScript that doesn't have the new functions.

## Solution Steps

### 1. Hard Refresh the Page
**Chrome/Edge:**
- Mac: `Cmd + Shift + R` or `Cmd + Option + R`
- Windows: `Ctrl + Shift + R` or `Ctrl + F5`

**Safari:**
- Mac: `Cmd + Option + R`
- Or: Hold `Shift` while clicking reload button

**Firefox:**
- Mac: `Cmd + Shift + R`
- Windows: `Ctrl + Shift + R`

### 2. Clear Browser Cache
1. Open Developer Tools (F12 or Cmd+Option+I)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

### 3. Try Incognito/Private Mode
Open the page in a private/incognito window:
```
http://localhost:8000/wheels/building
```

### 4. Check Browser Console for Errors
1. Open Developer Tools (F12)
2. Go to Console tab
3. Look for any red JavaScript errors
4. Share errors if any appear

---

## Expected Behavior After Fix

### Company Selector Should:
- ✅ Show logo and company name at top
- ✅ Dropdown shows all 8 portfolio companies
- ✅ Clicking a company updates logo and name
- ✅ All tabs update their headers

### Tab Switching Should:
- ✅ Click "Activities" - Shows activities board
- ✅ Click "Dealflow" - Shows dealflow board  
- ✅ Click "Financial" - Shows financial metrics
- ✅ Click "Team" - Shows team members
- ✅ Filters hide on Financial and Team tabs

### Company Switching Should:
- ✅ Logo changes
- ✅ Name changes
- ✅ Financial metrics update
- ✅ Team members update
- ✅ Activity/Dealflow headers update

---

## Verification Tests

### Test 1: Tab Switching
1. Load http://localhost:8000/wheels/building
2. Open browser console (F12)
3. Click "Dealflow" tab
4. Console should show: `Switching to tab: dealflow`
5. Dealflow board should appear

### Test 2: Company Switching
1. Select "Crystal Alarm" from dropdown
2. Console should show: `Switching to company: [uuid]`
3. Logo should change to Crystal Alarm logo
4. Name should change to "Crystal Alarm"

### Test 3: Financial Data
1. Select "Crystal Alarm"
2. Click "Financial" tab
3. Should show:
   - MRR: 1443k kr
   - ARR: 17.3M kr
   - Investment: 72.7M kr
   - Valuation: 103.9M kr

### Test 4: Team Data
1. Select "Coeo"
2. Click "Team" tab
3. Should show 2 founders:
   - Anders Gunnarsson
   - Tinna Sandström

---

## Alternative: Test with Direct URLs

If switching doesn't work, you can test individual pages directly in new tabs:

```
http://localhost:8000/wheels/building
http://localhost:8000/wheels/admin
http://localhost:8000/wheels/dealflow/companies
```

---

## Still Not Working?

### Check Server Logs:
```bash
tail -50 /tmp/uvicorn_fresh.log
```

### Restart Server:
```bash
cd backend
pkill -f "uvicorn"
source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

### Test in Different Browser:
Try Safari, Chrome, or Firefox to rule out browser-specific issues.

---

## Contact Developer

If issue persists after:
1. ✅ Hard refresh
2. ✅ Clear cache
3. ✅ Try incognito
4. ✅ Check console for errors

Share:
- Browser name and version
- Any console errors (screenshot)
- Which specific action doesn't work (tab click or dropdown change)

---

**Most Common Fix:** Hard refresh with `Cmd + Shift + R` (Mac) or `Ctrl + Shift + R` (Windows)

