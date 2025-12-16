# Quick Start: Backfill Display Names for Existing Documents

## What This Does

Updates all existing documents in your database to have clean, readable names instead of messy filenames.

**Before:**
- `IK_Disruptive_Ventures_möte_20231005_10-05__IK, Disruptive Ventures`
- `Möte_2023-10-04_Serge_Guelnoji_Peo__2023-10-04__serge _ guelnoji _ peo`

**After:**
- `Disruptive Ventures Meeting - Oct 5, 2023`
- `Serge Guelnoji Meeting - Oct 4, 2023`

---

## Step 1: Preview Changes (Recommended)

See what will be updated **without making any changes**:

```bash
cd backend
python backfill_display_names.py --dry-run
```

You'll see a table showing:
- Original filename
- What the cleaned name will be
- How many documents will be updated

---

## Step 2: Apply Changes

Once you're happy with the preview:

```bash
python backfill_display_names.py
```

This will:
- ✅ Update all documents without `display_name`
- ✅ Keep the original filename intact
- ✅ Show progress as it updates
- ✅ Display success/failure count

---

## Options

### Update Specific Organization

```bash
python backfill_display_names.py --org-id <your-org-uuid>
```

### Show Examples Only

```bash
python backfill_display_names.py --examples
```

### Help

```bash
python backfill_display_names.py --help
```

---

## Alternative: SQL Migration

If you prefer SQL:

```bash
# Connect to your database and run:
psql -d your_database -f backend/migrations/015_backfill_display_names.sql
```

**Note:** The Python script provides better cleaning results.

---

## Expected Output

```
================================================================================
BACKFILL DISPLAY NAMES FOR EXISTING DOCUMENTS
================================================================================

📥 Fetching documents without display_name...
Found 6 documents to update

--------------------------------------------------------------------------------
ORIGINAL FILENAME                                  | CLEANED NAME
--------------------------------------------------------------------------------
IK_Disruptive_Ventures_möte_20231005_10-05__IK...  | Disruptive Ventures Meeting - Oct 5...
Möte_2023-10-04_Serge_Guelnoji_Peo__2023-10-04... | Serge Guelnoji Meeting - Oct 4, 2023
Online_Partner_disruptiveventures_Gemini Enter... | Gemini Enterprise SKU - Online Partner
Pokalen_styrelsemöte_2023-11-15__2023-11-15__S... | Pokalen Meeting - Nov 15, 2023
High-Level Plan to AI-ify Disruptive Ventures     | High-Level Plan - Ai-Ify Disruptive...
Veckomöte - Team Meeting (Marcus intro, AI-pro... | Team Meeting (Marcus Intro - Ai-Proj...
--------------------------------------------------------------------------------

✅ UPDATE COMPLETE:
   Successfully updated: 6 documents

================================================================================
```

---

## Safety

✅ **Safe to run multiple times** - Only updates documents where `display_name` IS NULL

✅ **Non-destructive** - Original filenames are preserved

✅ **Dry-run mode** - Preview before making changes

✅ **Org-scoped** - Can limit to specific organization

---

## Troubleshooting

### ModuleNotFoundError

```bash
# Make sure you're in the backend directory
cd backend

# Check Python path
export PYTHONPATH="${PYTHONPATH}:."

# Try again
python backfill_display_names.py --dry-run
```

### No documents found

If you see "No documents need updating", it means:
- All documents already have `display_name` set, OR
- No documents exist in the database yet

### Database connection error

Check your environment variables:
```bash
# Make sure these are set
echo $SUPABASE_URL
echo $SUPABASE_SERVICE_KEY
```

---

## Next Steps

After backfilling:

1. **Update your UI** to display `display_name` instead of `filename`
2. **New documents** will automatically get cleaned names (via Agent 1 Extractor)
3. **No further action needed** - system is fully automated

---

## Questions?

See full documentation: `DOCUMENT_NAME_CLEANING.md`

