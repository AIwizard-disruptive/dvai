-- =====================================================
-- MIGRATION 016: Add display_title to meetings table
-- Clean up messy meeting names like documents
-- =====================================================

-- Add display_title field to meetings
ALTER TABLE meetings ADD COLUMN IF NOT EXISTS display_title TEXT;

-- Create index for searching
CREATE INDEX IF NOT EXISTS idx_meetings_display_title ON meetings(display_title);

-- Update views to include display_title
CREATE OR REPLACE VIEW v_meetings_with_clean_names AS
SELECT 
    m.id,
    m.org_id,
    m.title AS original_title,
    m.display_title,
    COALESCE(m.display_title, m.title) AS clean_title,
    m.meeting_date,
    m.meeting_type,
    m.company,
    m.duration_minutes,
    m.processing_status,
    m.created_at
FROM meetings m;

COMMENT ON COLUMN meetings.display_title IS 'Cleaned, human-readable meeting title (auto-generated from title)';
COMMENT ON VIEW v_meetings_with_clean_names IS 'Meetings with fallback to display_title for clean names';

-- Verification
SELECT 
    COUNT(*) as total_meetings,
    COUNT(display_title) as with_display_title,
    COUNT(*) - COUNT(display_title) as without_display_title
FROM meetings;
