# Google Sheets Sync Status ℹ️

**Current Status:** Not yet syncing automatically

---

## What's Currently Happening

### Financial Data on Building Page:
- ✅ **Manually imported** from your Q3 2025 KPI report
- ✅ Stored in database (`portfolio_companies` table)
- ✅ Shows real Q3 numbers you provided
- ❌ **NOT auto-updating** from Google Sheets yet

### Data Source:
The Q3 2025 data currently in the system came from the spreadsheet data you pasted earlier:
```
https://docs.google.com/spreadsheets/d/1RbVf3L8LQ1Z96x1NWcyOCssmAw_U5_aHT-m7b9FTqdc/
```

But it was entered manually via the `update_financial_data_from_q3.py` script, not pulled automatically.

---

## What Needs to Be Done for Auto-Sync

### Option 1: Service Account (Recommended)

#### Step 1: Create Service Account
1. Go to: https://console.cloud.google.com
2. Create or select project
3. Enable Google Sheets API
4. Create Credentials → Service Account
5. Download JSON key file

#### Step 2: Share Spreadsheet
1. Open your Q3 KPI spreadsheet
2. Click "Share"
3. Add service account email (looks like: `xxx@project-id.iam.gserviceaccount.com`)
4. Give "Viewer" permission

#### Step 3: Configure in Settings
1. Go to http://localhost:8000/settings
2. Portfolio Companies tab
3. Click "Connect" on Google Sheets for DV
4. Paste spreadsheet URL
5. Paste service account JSON
6. Save

#### Step 4: Run Sync
The system will then be able to:
- Read Q3 data automatically
- Update portfolio_companies table
- Refresh financial metrics
- Run on schedule (daily/weekly)

### Option 2: Public Sheet (Quick but Limited)

If you make the sheet publicly viewable:
1. Right-click sheet → Share → "Anyone with link can view"
2. No authentication needed
3. Can read via Google Sheets JSON API
4. Simpler but less secure

---

## What Will Auto-Sync

When connected, the system will automatically update:

### For Each Portfolio Company:
- **Q3 Revenue** (Jul + Aug + Sep columns)
- **Q3 Profit** (Resultat före skatt)
- **LTM Revenue** (Last 12 months)
- **Growth %** (YoY comparison)
- **Employees** (Latest count)
- **Cash Position** (Likviditet)
- **Status Notes** (Company commentary)

### Update Frequency:
- **Manual**: Click "Sync Now" button
- **Scheduled**: Daily at 7am (can configure)
- **On-demand**: API endpoint to trigger sync

---

## Files Created (Ready for Use)

### Integration Client:
**`app/integrations/google_sheets_client.py`**

Two approaches available:

#### 1. GoogleSheetsClient (Service Account):
```python
client = GoogleSheetsClient(credentials_json)
data = client.get_q3_kpi_data(spreadsheet_url)
```

#### 2. SimpleGoogleSheetsClient (Public Sheet):
```python
data = await SimpleGoogleSheetsClient.read_public_sheet(
    spreadsheet_id="1RbVf3L8LQ1Z96x1NWcyOCssmAw_U5_aHT-m7b9FTqdc"
)
```

---

## How to Enable Auto-Sync

### Quick Test (Public Sheet Method):

1. Make your Q3 spreadsheet public
2. I'll create a sync endpoint
3. Call `/sync/google-sheets/dv` to pull latest data
4. Updates portfolio_companies table automatically

### Production (Service Account Method):

1. Set up service account (see steps above)
2. Share sheet with service account
3. Add credentials via Settings page
4. Enable scheduled sync

---

## Current Data Status

### What You're Seeing:
The financial metrics on the Building page are **real Q3 2025 data** but from a **one-time import** on December 17, 2025.

### Companies with Q3 Data:
1. Crystal Alarm - 5,774 tkr Q3 revenue ✅
2. Alent Dynamic - 2,905 tkr Q3 revenue ✅
3. Vaylo - 282 tkr Q3 revenue ✅
4. LunaLEC - Pre-revenue ✅
5. Basic Safety - 753 tkr Q3 revenue ✅
6. Coeo - 614 tkr Q3 revenue ✅
7. Service Node - 150 tkr Q3 revenue ✅

### To Update:
Either:
- Re-run `update_financial_data_from_q3.py` with new data
- Or set up Google Sheets auto-sync (recommended)

---

## Next Steps

### To Enable Auto-Sync:

**Choose one approach:**

#### A. Service Account (Most Secure):
```bash
# 1. Create service account, download JSON
# 2. Share sheet with service account email
# 3. Add to Settings page
# 4. Run sync
```

#### B. Public Sheet (Quickest):
```bash
# 1. Make sheet "Anyone with link can view"
# 2. I create sync endpoint
# 3. Call /sync/google-sheets/dv
# 4. Data auto-updates
```

---

## Want Me to Implement?

I can build the Google Sheets sync now if you:

1. **Share the spreadsheet** with a service account, OR
2. **Make it publicly viewable** (Anyone with link)

Then I'll create:
- Sync endpoint `/sync/google-sheets/{company_id}`
- Scheduled sync task (Celery)
- "Sync Now" button in UI
- Auto-update every 24 hours

Let me know which approach you prefer! 📊

---

**Bottom Line:**
- ✅ Real Q3 2025 data showing
- ✅ Accurate numbers from your report
- ❌ Not auto-syncing from sheet yet
- ⏳ Ready to implement when you share credentials

