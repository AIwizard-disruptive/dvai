-- =====================================================
-- MIGRATION 015: Backfill display_name for existing documents
-- =====================================================
-- 
-- This migration creates a function to clean document names
-- and backfills the display_name field for existing documents.
--
-- Note: The cleaning logic here is a simplified SQL version.
-- For full cleaning logic, use the Python script: backfill_display_names.py
--
-- =====================================================

-- Function to extract date from filename (simplified)
CREATE OR REPLACE FUNCTION extract_date_from_filename(filename TEXT)
RETURNS TEXT AS $$
DECLARE
    date_match TEXT;
BEGIN
    -- Try to find YYYY-MM-DD pattern
    date_match := (regexp_matches(filename, '(\d{4})-(\d{2})-(\d{2})'))[1];
    IF date_match IS NOT NULL THEN
        RETURN date_match;
    END IF;
    
    -- Try to find YYYYMMDD pattern
    date_match := (regexp_matches(filename, '(\d{4})(\d{2})(\d{2})'))[1];
    IF date_match IS NOT NULL THEN
        RETURN date_match;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to clean document name (simplified SQL version)
CREATE OR REPLACE FUNCTION clean_document_name_sql(filename TEXT)
RETURNS TEXT AS $$
DECLARE
    cleaned TEXT;
    date_str TEXT;
    date_formatted TEXT;
BEGIN
    -- Remove file extension
    cleaned := regexp_replace(filename, '\.[^.]+$', '');
    
    -- Extract and format date
    date_str := extract_date_from_filename(filename);
    
    -- Replace common delimiters with spaces
    cleaned := regexp_replace(cleaned, '[_-]+', ' ', 'g');
    
    -- Remove duplicate spaces
    cleaned := regexp_replace(cleaned, '\s+', ' ', 'g');
    
    -- Remove common prefixes
    cleaned := regexp_replace(cleaned, '(?i)^\s*(ik|möte|meeting|online|partner)\s+', '', 'g');
    
    -- Remove duplicate date if present
    IF date_str IS NOT NULL THEN
        cleaned := regexp_replace(cleaned, date_str, '', 'g');
    END IF;
    
    -- Clean up spaces
    cleaned := trim(cleaned);
    
    -- Add formatted date if found
    IF date_str IS NOT NULL THEN
        BEGIN
            date_formatted := to_char(date_str::date, 'Mon DD, YYYY');
            cleaned := cleaned || ' - ' || date_formatted;
        EXCEPTION WHEN OTHERS THEN
            -- Invalid date, skip formatting
            NULL;
        END;
    END IF;
    
    -- Remove multiple dashes
    cleaned := regexp_replace(cleaned, '\s*-\s*-\s*', ' - ', 'g');
    
    -- Final cleanup
    cleaned := trim(both ' -' from cleaned);
    
    -- Limit length
    IF length(cleaned) > 100 THEN
        cleaned := substring(cleaned, 1, 97) || '...';
    END IF;
    
    -- Fallback if empty
    IF cleaned = '' OR cleaned IS NULL THEN
        cleaned := 'Document';
    END IF;
    
    RETURN cleaned;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- =====================================================
-- Backfill existing documents
-- =====================================================

-- Show what will be updated (for review)
DO $$
DECLARE
    doc_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO doc_count
    FROM uploaded_documents
    WHERE display_name IS NULL;
    
    RAISE NOTICE 'Found % documents without display_name', doc_count;
END $$;

-- Create a temporary table to preview changes (optional - comment out if not needed)
CREATE TEMP TABLE IF NOT EXISTS display_name_preview AS
SELECT 
    id,
    filename AS original_filename,
    clean_document_name_sql(filename) AS new_display_name
FROM uploaded_documents
WHERE display_name IS NULL
LIMIT 20;

-- Show preview
DO $$
DECLARE
    preview_rec RECORD;
BEGIN
    RAISE NOTICE 'Preview of first 20 documents:';
    RAISE NOTICE '========================================';
    
    FOR preview_rec IN 
        SELECT original_filename, new_display_name 
        FROM display_name_preview
    LOOP
        RAISE NOTICE 'Original: %', preview_rec.original_filename;
        RAISE NOTICE 'Cleaned:  %', preview_rec.new_display_name;
        RAISE NOTICE '----------------------------------------';
    END LOOP;
END $$;

-- =====================================================
-- ACTUAL UPDATE (uncomment to run)
-- =====================================================

-- WARNING: This will update all documents without display_name
-- Review the preview above before uncommenting this section

/*
UPDATE uploaded_documents
SET display_name = clean_document_name_sql(filename)
WHERE display_name IS NULL;

-- Show results
DO $$
DECLARE
    updated_count INTEGER;
BEGIN
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RAISE NOTICE 'Updated % documents with cleaned display_name', updated_count;
END $$;
*/

-- =====================================================
-- Verification query
-- =====================================================

-- Check documents with display_name
SELECT 
    COUNT(*) as total_docs,
    COUNT(display_name) as docs_with_display_name,
    COUNT(*) - COUNT(display_name) as docs_without_display_name
FROM uploaded_documents;

-- Show sample of cleaned names
SELECT 
    filename,
    display_name,
    created_at
FROM uploaded_documents
WHERE display_name IS NOT NULL
ORDER BY created_at DESC
LIMIT 10;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON FUNCTION clean_document_name_sql IS 'Simplified SQL version of document name cleaning. For full cleaning logic, use Python script: backfill_display_names.py';
COMMENT ON FUNCTION extract_date_from_filename IS 'Extract date from filename using regex patterns';

-- =====================================================
-- NOTES
-- =====================================================

-- For best results, use the Python script instead:
--   cd backend
--   python backfill_display_names.py --dry-run  # Preview changes
--   python backfill_display_names.py            # Apply changes
--
-- The Python version includes:
--   - More sophisticated name parsing
--   - Deduplication logic
--   - Better date formatting
--   - Swedish language handling
--   - Company name extraction
--   - Meeting type detection

