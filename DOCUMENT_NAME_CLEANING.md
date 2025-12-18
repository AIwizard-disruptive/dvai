# Document Name Cleaning System

## Overview

The document name cleaning system automatically parses and cleans messy filenames from various sources (Google Calendar exports, email attachments, file uploads) into human-readable display names.

## Problem Solved

Meeting files from Google Calendar and other sources often have terrible names like:
- `IK_Disruptive_Ventures_möte_20231005_10-05__IK, Disruptive Ventures`
- `Möte_2023-10-04_Serge_Guelnoji_Peo__2023-10-04__serge _ guelnoji _ peo`
- `Online_Partner_disruptiveventures_Gemini Enterprise SKU, Online Part`

These names are:
- **Duplicated**: Same info repeated multiple times
- **Messy**: Underscores, mixed separators, inconsistent casing
- **Unclear**: Hard to understand at a glance

## Solution

The system automatically transforms these into clean names:
- `Disruptive Ventures Meeting - Oct 5, 2023`
- `Meeting with Serge Guelnoji - Oct 4, 2023`
- `Gemini Enterprise SKU - Online Partner`

## Implementation

### Database Schema

The `uploaded_documents` table now includes a `display_name` field:

```sql
CREATE TABLE uploaded_documents (
    id UUID PRIMARY KEY,
    org_id UUID NOT NULL,
    filename TEXT NOT NULL,              -- Original filename
    display_name TEXT,                    -- Cleaned, human-readable name
    file_hash TEXT UNIQUE NOT NULL,
    ...
);
```

### Parsing Logic

Located in `backend/app/services/document.py`:

#### 1. `parse_filename_metadata(filename: str) -> dict`

Extracts structured metadata from filenames:

```python
{
    'date': '2023-10-05',           # Parsed date
    'time': '10:05',                # Parsed time
    'company': 'Acme Corp',         # Detected company
    'type': 'meeting',              # Meeting type
    'cleaned_name': 'Acme Corp Meeting - Oct 5, 2023'
}
```

**Patterns detected:**
- **Dates**: YYYY-MM-DD, YYYYMMDD, MM/DD/YYYY
- **Times**: HH:MM, HH-MM
- **Companies**: Capitalized words
- **Meeting types**: möte, meeting, intro, call, discussion, team meeting, etc.

#### 2. `clean_document_name(filename: str) -> str`

Main cleaning function that:

1. **Removes file extension**
2. **Splits by delimiters**: `_`, `-`, `__`, spaces
3. **Deduplicates**: Removes repeated information (case-insensitive)
4. **Extracts dates and times**: Converts to readable format
5. **Filters common prefixes**: Removes "IK", "möte", "online", "partner"
6. **Capitalizes properly**: Title case for words
7. **Formats output**: `Subject - Meeting Type - Date`
8. **Limits length**: Max 100 characters

### Integration with Agent 1 Extractor

The cleaning happens automatically during document extraction:

```python
# backend/app/services/agent_1_extractor.py

async def extract(self, file_content: bytes, filename: str, ...):
    # Parse filename and get cleaned name
    filename_metadata = DocumentService.parse_filename_metadata(filename)
    
    # Extract document content...
    result = await self._extract_from_pdf(file_content, source_hash)
    
    # Merge filename metadata into result
    result.metadata.update({
        'original_filename': filename,
        'filename_metadata': filename_metadata,
        'cleaned_name': filename_metadata.get('cleaned_name', filename)
    })
    
    return result
```

## Usage Examples

### Example 1: IK Meeting with Duplicates

**Input:**
```
IK_Disruptive_Ventures_möte_20231005_10-05__IK, Disruptive Ventures
```

**Output:**
```
Disruptive Ventures Meeting - Oct 5, 2023
```

**What happened:**
- Removed "IK" prefix (common)
- Detected "möte" = meeting
- Extracted date: 2023-10-05
- Deduplicated "Disruptive Ventures"
- Formatted as readable name

### Example 2: Meeting with Person Names

**Input:**
```
Möte_2023-10-04_Serge_Guelnoji_Peo__2023-10-04__serge _ guelnoji _ peo
```

**Output:**
```
Serge Guelnoji Meeting - Oct 4, 2023
```

**What happened:**
- Detected "Möte" = meeting
- Extracted person names: Serge Guelnoji
- Deduplicated repeated names (case-insensitive)
- Removed duplicate date
- Formatted date as "Oct 4, 2023"

### Example 3: Online Partner Meeting

**Input:**
```
Online_Partner_disruptiveventures_Gemini Enterprise SKU, Online Part
```

**Output:**
```
Gemini Enterprise SKU - Online Partner
```

**What happened:**
- Detected primary subject: "Gemini Enterprise SKU"
- Secondary context: "Online Partner"
- Removed common prefix "disruptiveventures"
- Deduplicated "Online Part" (partial match)

### Example 4: Board Meeting

**Input:**
```
Pokalen_styrelsemöte_2023-11-15__2023-11-15__Styrelsen
```

**Output:**
```
Pokalen Meeting - Nov 15, 2023
```

**What happened:**
- Detected "styrelsemöte" = board meeting
- Extracted company: "Pokalen"
- Removed duplicate date
- Formatted date

## How to Use in Your Application

### 1. When Uploading Documents

```python
from app.services.document import DocumentService

# Parse filename
filename = "IK_Disruptive_Ventures_möte_20231005.ics"
metadata = DocumentService.parse_filename_metadata(filename)

# Get cleaned name
cleaned_name = metadata['cleaned_name']
# Result: "Disruptive Ventures Meeting - Oct 5, 2023"

# Store in database
await db.execute(
    """
    INSERT INTO uploaded_documents (
        filename, display_name, file_hash, ...
    ) VALUES (?, ?, ?, ...)
    """,
    filename, cleaned_name, file_hash, ...
)
```

### 2. In Agent 1 Extractor (Automatic)

The extractor automatically includes cleaned names:

```python
from app.services.agent_1_extractor import get_extractor_agent

extractor = get_extractor_agent()
result = await extractor.extract(file_content, filename, mime_type)

# Cleaned name is in metadata
cleaned_name = result.metadata['cleaned_name']
original = result.metadata['original_filename']
parsed_info = result.metadata['filename_metadata']
```

### 3. Displaying in UI

Always use `display_name` instead of `filename`:

```typescript
// Frontend component
<div className="meeting-card">
  <h3>{meeting.display_name || meeting.filename}</h3>
  <p className="text-sm text-gray-500">
    Original: {meeting.filename}
  </p>
</div>
```

## Testing

Run the test script to see cleaning in action:

```bash
cd backend
python3 test_document_name_cleaning.py
```

This will show before/after comparisons for various filename patterns.

## Configuration

### Adding New Meeting Type Keywords

Edit `parse_filename_metadata()` in `document.py`:

```python
meeting_types = [
    "kickoff", "standup", "review", "planning", 
    "retrospective", "demo", "möte", "meeting",
    "intro", "team meeting", "partner",
    "your_new_type_here"  # Add here
]
```

### Adding Common Prefixes to Filter

Edit `clean_document_name()` in `document.py`:

```python
common_prefixes = {
    'ik', 'möte', 'meeting', 'online', 'partner',
    'your_prefix_here'  # Add here
}
```

## Database Queries

### Get documents with cleaned names

```sql
SELECT 
    id,
    filename AS original,
    display_name AS cleaned,
    uploaded_at
FROM uploaded_documents
ORDER BY uploaded_at DESC;
```

### Find documents without cleaned names

```sql
SELECT 
    id,
    filename
FROM uploaded_documents
WHERE display_name IS NULL;
```

### Update existing documents with cleaned names

Use the backfill script to update all existing documents:

```bash
cd backend

# Preview what will be updated (dry run)
python backfill_display_names.py --dry-run

# Actually update all documents
python backfill_display_names.py

# Update documents for specific organization
python backfill_display_names.py --org-id <org-uuid>

# Show examples of name cleaning
python backfill_display_names.py --examples
```

**Example output:**

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

#### Alternative: SQL Migration

You can also use the SQL migration script:

```bash
# Run the SQL migration
psql -d your_database -f backend/migrations/015_backfill_display_names.sql
```

**Note:** The Python script provides better results with more sophisticated cleaning logic.

## Benefits

1. **Improved UX**: Users see clear, readable document names
2. **Better Search**: Cleaned names are more searchable
3. **Consistency**: All documents follow same naming convention
4. **Automatic**: No manual renaming required
5. **Preserves Original**: Original filename is kept for reference
6. **Metadata Extraction**: Dates, times, companies parsed automatically

## Future Enhancements

Potential improvements:

1. **AI-Based Cleaning**: Use LLM to generate even better names
2. **Language Detection**: Better handling of Swedish, English, etc.
3. **Company Detection**: Use existing company database to detect companies
4. **User Preferences**: Allow users to customize cleaning rules
5. **Bulk Rename**: UI for batch renaming existing documents
6. **Smart Suggestions**: Suggest better names based on document content

## Summary

The document name cleaning system:
- ✅ Automatically cleans messy filenames during document parsing
- ✅ Stores both original and cleaned names in database
- ✅ Integrated with Agent 1 Extractor
- ✅ Handles common patterns from Google Calendar, meetings, etc.
- ✅ Provides human-readable display names for UI
- ✅ Preserves original filenames for reference
- ✅ Includes metadata extraction (dates, times, companies)

Use `display_name` in your UI instead of `filename` for a much better user experience!


