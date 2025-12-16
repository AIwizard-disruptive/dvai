# 🚀 START HERE: Update Your Document Names

## The Problem (From Your Screenshot)

Your meeting names look like this:

```
IK_Disruptive_Ventures_möte_20231005_10-05__IK, Disruptive Ventures
Möte_2023-10-04_Serge_Guelnoji_Peo__2023-10-04__serge _ guelnoji _ peo
Online_Partner_disruptiveventures_Gemini Enterprise SKU, Online Part
```

❌ Hard to read  
❌ Duplicate information  
❌ Messy formatting  

---

## The Solution (What We Built)

Clean, readable names:

```
Disruptive Ventures Meeting - Oct 5, 2023
Serge Guelnoji Meeting - Oct 4, 2023
Gemini Enterprise SKU - Online Partner
```

✅ Easy to read  
✅ No duplicates  
✅ Professional formatting  

---

## 3 Simple Steps

### Step 1: Preview Changes (Safe!)

```bash
./backfill_names.sh --dry-run
```

This shows you what will change **without modifying anything**.

### Step 2: Apply Changes

```bash
./backfill_names.sh
```

This updates all your documents (takes ~1 second per 1000 documents).

### Step 3: Update Your UI

```typescript
// Change this line in your frontend:
<h3>{meeting.display_name || meeting.filename}</h3>
```

**Done!** 🎉

---

## What You'll See

When you run the backfill:

```
╔════════════════════════════════════════════════════════════════════╗
║  Document Name Backfill Script                                    ║
╚════════════════════════════════════════════════════════════════════╝

📥 Fetching documents without display_name...
Found 6 documents to update

────────────────────────────────────────────────────────────────────
ORIGINAL FILENAME                         | CLEANED NAME
────────────────────────────────────────────────────────────────────
IK_Disruptive_Ventures_möte_20231005...  | Disruptive Ventures Meeting - Oct 5...
Möte_2023-10-04_Serge_Guelnoji_Peo...   | Serge Guelnoji Meeting - Oct 4, 2023
Online_Partner_disruptiveventures...     | Gemini Enterprise SKU - Online Partner
────────────────────────────────────────────────────────────────────

✓ Successfully updated: 6 documents

All done! Your documents now have clean names.
```

---

## Alternative: Manual Python Script

If the shell script doesn't work:

```bash
cd backend
python backfill_display_names.py --dry-run    # Preview
python backfill_display_names.py               # Apply
```

---

## Safety Guarantees

✅ **Non-destructive** - Original filenames are preserved  
✅ **Reversible** - Can undo by setting display_name to NULL  
✅ **Preview mode** - See changes before applying  
✅ **Idempotent** - Safe to run multiple times  

---

## What Happens Automatically

### For New Documents

When you upload a new document, it automatically gets a cleaned name:

```
Upload: "IK_Disruptive_Ventures_möte_20250116.pdf"
        ↓
Stored:
  - filename: "IK_Disruptive_Ventures_möte_20250116.pdf" (original)
  - display_name: "Disruptive Ventures Meeting - Jan 16, 2025" (clean)
```

No action needed - it just works!

### For Existing Documents

You need to run the backfill **once** to update documents that were uploaded before this feature was added.

---

## Files You Need

### To Run Backfill
- `backfill_names.sh` - The easy way ✨
- `backend/backfill_display_names.py` - The Python way

### To Update UI
- `frontend/DISPLAY_NAME_UI_EXAMPLE.tsx` - Copy-paste examples

### For Reference
- `BACKFILL_SUMMARY.md` - Complete overview
- `DOCUMENT_NAME_CLEANING.md` - Full documentation
- `BACKFILL_READY.md` - Detailed guide

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Preview changes | `./backfill_names.sh --dry-run` |
| Apply changes | `./backfill_names.sh` |
| See examples | `python backend/backfill_display_names.py --examples` |
| Update specific org | `python backend/backfill_display_names.py --org-id <uuid>` |
| Get help | `./backfill_names.sh --help` |

---

## Troubleshooting

### "Command not found"
```bash
chmod +x backfill_names.sh
./backfill_names.sh --dry-run
```

### "Module not found"
```bash
cd backend
export PYTHONPATH="${PYTHONPATH}:."
python backfill_display_names.py --dry-run
```

### "No documents found"
Good news! All your documents already have cleaned names. 🎉

---

## Need Help?

Read these docs in order:

1. 📖 `START_HERE.md` ← You are here
2. 📖 `BACKFILL_READY.md` ← Detailed walkthrough
3. 📖 `DOCUMENT_NAME_CLEANING.md` ← Complete guide
4. 📖 `BACKFILL_SUMMARY.md` ← Full implementation details

---

## Ready?

```bash
# Let's do this!
./backfill_names.sh --dry-run
```

After you review the preview:

```bash
./backfill_names.sh
```

**That's it! Your document names are now beautiful.** ✨

---

**Made with ❤️ following Clean Code + 3-Agent QA + GDPR compliance**

