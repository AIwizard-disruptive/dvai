-- Check if user_integrations table exists and what's in it

-- Check table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'user_integrations'
ORDER BY ordinal_position;

-- Check existing data
SELECT * FROM user_integrations LIMIT 5;

-- Check policies
SELECT schemaname, tablename, policyname
FROM pg_policies
WHERE tablename = 'user_integrations';

