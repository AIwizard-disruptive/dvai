-- Check which tables exist and their columns
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name IN (
    'orgs', 'org_memberships', 'meeting_groups', 'meetings', 
    'people', 'meeting_participants', 'artifacts', 'transcript_chunks',
    'summaries', 'action_items', 'decisions', 'tags', 'meeting_tags',
    'entities', 'meeting_entities', 'links', 'processing_runs', 
    'external_refs', 'integrations'
)
ORDER BY table_name, ordinal_position;



