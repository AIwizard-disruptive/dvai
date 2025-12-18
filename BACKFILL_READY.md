# ✅ Document Name Cleaning - Ready to Backfill

## What You Asked For

> "can we rename and parse document info from name instead so name is clear. we should do this when parsing document"

## What Was Built

✅ **Automatic name cleaning during document parsing** (Agent 1 Extractor)  
✅ **Database schema updated** (migration 014 - already ran successfully)  
✅ **Backfill script for existing documents** (this is what you need now!)  
✅ **Full documentation**  
✅ **UI examples**  

---

## Quick Start: Update Your Existing Documents

### Step 1: Preview Changes (Safe - No Updates)

```bash
cd backend
python backfill_display_names.py --dry-run
```

This shows you what will change **without modifying anything**.

### Step 2: Apply Changes

```bash
python backfill_display_names.py
```

This updates all documents that don't have `display_name` yet.

---

## What This Fixes

Your messy meeting names from the screenshot:

| Before (Original Filename) | After (Cleaned Display Name) |
|---------------------------|------------------------------|
| `IK_Disruptive_Ventures_möte_20231005_10-05__IK, Disruptive Ventures` | `Disruptive Ventures Meeting - Oct 5, 2023` |
| `Möte_2023-10-04_Serge_Guelnoji_Peo__2023-10-04__serge _ guelnoji _ peo` | `Serge Guelnoji Meeting - Oct 4, 2023` |
| `Online_Partner_disruptiveventures_Gemini Enterprise SKU, Online Part` | `Gemini Enterprise SKU - Online Partner` |
| `Pokalen_styrelsemöte_2023-11-15__2023-11-15__Styrelsen` | `Pokalen Meeting - Nov 15, 2023` |
| `High-Level Plan to AI-ify Disruptive Ventures` | `High-Level Plan - Ai-Ify Disruptive Ventures` |
| `Veckomöte - Team Meeting (Marcus intro, AI-projekt, uppföljningar)` | `Team Meeting (Marcus Intro - Ai-Projekt)` |

---

## What Was Created

### 1. Core Functionality
- ✅ `backend/app/services/document.py` - Parsing & cleaning logic
- ✅ `backend/app/services/agent_1_extractor.py` - Auto-integration
- ✅ `backend/migrations/014_document_intelligence_system.sql` - Database (ran ✅)

### 2. Backfill Tools (NEW - for existing documents)
- ✅ `backend/backfill_display_names.py` - Python script (recommended)
- ✅ `backend/migrations/015_backfill_display_names.sql` - SQL version

### 3. Documentation
- ✅ `DOCUMENT_NAME_CLEANING.md` - Complete guide
- ✅ `DOCUMENT_NAME_PARSING_COMPLETE.md` - 3-Agent QA summary
- ✅ `BACKFILL_DISPLAY_NAMES_NOW.md` - Quick start guide
- ✅ `BACKFILL_READY.md` - This file
- ✅ `frontend/DISPLAY_NAME_UI_EXAMPLE.tsx` - UI examples

### 4. Testing
- ✅ `backend/test_document_name_cleaning.py` - Test cases

---

## How It Works

### For New Documents (Automatic)

When Agent 1 processes a new document:

```python
# Automatically happens during extraction
result = await extractor.extract(file_content, filename)

# Cleaned name is included in metadata
cleaned_name = result.metadata['cleaned_name']

# Store in database
await db.execute("""
    INSERT INTO uploaded_documents (filename, display_name, ...)
    VALUES (?, ?, ...)
""", filename, cleaned_name, ...)
```

### For Existing Documents (Manual Backfill)

Run the backfill script once:

```bash
python backfill_display_names.py
```

---

## Update Your UI

Use `display_name` instead of `filename`:

```typescript
// ❌ Old way (messy)
<h3>{meeting.filename}</h3>

// ✅ New way (clean)
<h3>{meeting.display_name || meeting.filename}</h3>
```

See `frontend/DISPLAY_NAME_UI_EXAMPLE.tsx` for complete examples.

---

## Command Reference

```bash
# Preview what will change (safe, no updates)
python backfill_display_names.py --dry-run

# Update all documents
python backfill_display_names.py

# Update specific organization only
python backfill_display_names.py --org-id <uuid>

# Show examples of cleaning
python backfill_display_names.py --examples

# Help
python backfill_display_names.py --help
```

---

## Safety Features

✅ **Dry-run mode** - Preview before making changes  
✅ **Non-destructive** - Original filenames are preserved  
✅ **Idempotent** - Safe to run multiple times  
✅ **Org-scoped** - Can limit to specific organization  
✅ **Rollback** - Original filename always available  

---

## Expected Output

When you run the backfill:

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

## Next Steps

1. **Run backfill** (see "Quick Start" above)
2. **Update your UI** to use `display_name` (see `frontend/DISPLAY_NAME_UI_EXAMPLE.tsx`)
3. **Done!** New documents will automatically get cleaned names

---

## FAQ

**Q: Will this break anything?**  
A: No. Original filenames are preserved. This only adds cleaned names.

**Q: What if I run it twice?**  
A: It only updates documents where `display_name IS NULL`, so it's safe.

**Q: Can I undo it?**  
A: Yes, just set `display_name = NULL` to reset. Original filenames are never changed.

**Q: What about new documents?**  
A: They automatically get cleaned names via Agent 1 Extractor. No action needed.

**Q: Do I need to restart the server?**  
A: No. This is a one-time database update.

---

## Summary

🎯 **You're ready to backfill!**

Run these two commands:

```bash
cd backend
python backfill_display_names.py --dry-run    # Preview
python backfill_display_names.py               # Apply
```

That's it! Your messy document names will be transformed into clean, readable names. 🎉


