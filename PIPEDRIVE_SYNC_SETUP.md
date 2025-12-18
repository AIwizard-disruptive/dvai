# Pipedrive Sync Setup Guide

## Overview

This system syncs Kanban column titles (pipeline stages) and deals from Pipedrive for each portfolio company. When you select a portfolio company like COEO in the Building wheel, the Activities tab will show their Pipedrive deals organized in a Kanban board.

## Architecture

### Database Tables

1. **`portfolio_company_integrations`** - Stores encrypted Pipedrive API credentials per company
2. **`pipeline_stages`** - Stores pipeline stage names and order synced from Pipedrive

### Key Components

- **`pipedrive_client.py`** - Pipedrive API client
- **`pipedrive_sync.py`** - Service for syncing stages and data
- **`pipedrive_sync API`** - REST endpoints for sync operations
- **`wheel_building.py`** - Updated to fetch company-specific activities

## Setup Steps

### 1. Run the Database Migration

```bash
cd backend

# Apply the pipeline_stages table migration
psql $DATABASE_URL -f migrations/021_pipeline_stages.sql
```

### 2. Add COEO's Pipedrive Integration

If not already done, run:

```bash
python add_coeo_pipedrive_to_db.py
```

This encrypts and stores COEO's Pipedrive API token in the database.

### 3. Sync Pipeline Stages from Pipedrive

Run the sync script to fetch COEO's pipeline stages:

```bash
python sync_coeo_stages.py
```

Expected output:
```
🔄 SYNCING COEO PIPELINE STAGES FROM PIPEDRIVE
✅ Found COEO (ID: xxx)
✅ Found COEO Pipedrive integration
📥 Fetching pipeline stages from Pipedrive...
✅ Successfully synced 6 stages!

Stages synced:
  1. Lead
  2. Qualified
  3. Meeting
  4. Demo
  5. Proposal
  6. Closed Won
```

## How It Works

### When You Select a Company

1. **Select COEO** in the company dropdown on the Building wheel
2. **`switchCompany()`** JavaScript function is called
3. **`filterActivitiesByCompany()`** fetches data from `/wheels/building/company-activities/{company_id}`
4. **Backend** gets Pipedrive integration for that company
5. **Decrypts** API token and fetches deals from Pipedrive
6. **Maps** Pipedrive stages to kanban columns:
   - `Lead` → To Do
   - `Qualified` → To Do
   - `Meeting`, `Demo`, `Proposal` → In Progress
   - `Closed Won` → Done
7. **Returns** deals organized by column
8. **Frontend** reloads the kanban board with the new data

### When You Select "Disruptive Ventures"

- Shows Linear tasks instead of Pipedrive deals
- Uses the existing Linear integration

## API Endpoints

### Sync Pipeline Stages

```bash
POST /api/pipedrive/sync-stages
{
  "portfolio_company_id": "uuid"
}
```

### Get Pipeline Stages

```bash
GET /api/pipedrive/stages/{portfolio_company_id}
```

### Sync All Companies

```bash
POST /api/pipedrive/sync-all-companies
```

### Get Company Activities

```bash
GET /wheels/building/company-activities/{company_id}
```

## Testing

### 1. Check Database

```sql
-- View synced stages for COEO
SELECT 
    pc.organizations->>'name' as company,
    ps.stage_name,
    ps.stage_order,
    ps.stage_type,
    ps.source_system,
    ps.synced_at
FROM pipeline_stages ps
JOIN portfolio_companies pc ON ps.portfolio_company_id = pc.id
WHERE pc.organizations->>'name' = 'Coeo'
ORDER BY ps.stage_order;
```

### 2. Test the UI

1. Go to http://localhost:8000/wheels/building
2. Select **"Coeo"** from the dropdown
3. Click the **Activities** tab
4. You should see COEO's Pipedrive deals in a kanban board

### 3. Test the API

```bash
# Get stages
curl http://localhost:8000/api/pipedrive/stages/{coeo_portfolio_company_id}

# Get activities
curl http://localhost:8000/wheels/building/company-activities/{coeo_portfolio_company_id}
```

## Troubleshooting

### SQL Error: "syntax error at or near 'order'"

✅ **FIXED** - The migration file has been updated to use non-reserved column names.

### Company Selector Doesn't Update Activities

✅ **FIXED** - The `switchCompany()` function now properly fetches and reloads the kanban board with company-specific data.

### No Stages Synced

Check:
1. Pipedrive integration exists: `SELECT * FROM portfolio_company_integrations WHERE integration_type = 'pipedrive';`
2. API token is valid (test in Pipedrive UI)
3. Run `python sync_coeo_stages.py` again

### No Deals Showing

Check:
1. Deals exist in Pipedrive
2. API token has permission to read deals
3. Check browser console for errors
4. Check backend logs: `tail -f logs/app.log`

## Automatic Sync

### Option 1: Sync on Company Selection (Current)

Activities are fetched fresh every time you select a company. No caching.

### Option 2: Background Sync (Future Enhancement)

Add a Celery task to sync all company stages periodically:

```python
# backend/app/worker/tasks/pipedrive_sync.py

@celery_app.task(name="sync_all_pipedrive_stages")
def sync_all_pipedrive_stages():
    """Sync pipeline stages for all companies with Pipedrive integration."""
    # Call the sync service for each company
    pass
```

## Next Steps

### For Other Portfolio Companies

1. Add their Pipedrive credentials to `portfolio_company_integrations`
2. Run sync: `python sync_coeo_stages.py` (modify for other companies)
3. Stages will appear in their kanban board

### Fortnox Integration

Similar architecture can be used for Fortnox financial data:
- Create `fortnox_client.py`
- Sync financial KPIs to database
- Display in Financial tab

## Security Notes

- ✅ API tokens are encrypted using Fernet (AES-128)
- ✅ Encryption key stored in `.env` as `ENCRYPTION_KEY`
- ✅ Supabase service role key used for backend operations
- ✅ No API tokens exposed to frontend
- ✅ Decryption only happens server-side

## Files Modified/Created

### New Files
- `backend/migrations/021_pipeline_stages.sql`
- `backend/app/services/pipedrive_sync.py`
- `backend/app/api/pipedrive_sync.py`
- `backend/sync_coeo_stages.py`

### Modified Files
- `backend/app/api/wheel_building.py` - Added company-specific activities endpoint
- `backend/app/main.py` - Registered pipedrive_sync router

## Summary

You can now:
✅ Sync pipeline stages from Pipedrive for each portfolio company
✅ View company-specific deals in the Building wheel
✅ Switch between companies and see their real Pipedrive data
✅ Column titles match Pipedrive's actual stage names
✅ Company selector properly updates all tabs with correct data
