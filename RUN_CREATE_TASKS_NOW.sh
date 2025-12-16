#!/bin/bash
# Simple script to create tasks - just run this

cd "$(dirname "$0")/backend"

# Load DATABASE_URL from .env
export $(cat .env | grep DATABASE_URL)

# Run the SQL
psql $DATABASE_URL -f migrations/CREATE_TASKS_SERGE_WIZARD.sql

echo ""
echo "✅ Done! Tasks created for serge@ and wizard@"
echo ""
echo "Next: Run 'python3 backend/sync_google_tasks.py' to sync to Google Tasks"

