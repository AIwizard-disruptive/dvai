#!/bin/bash
# Apply tasks migration directly to database

echo "🔄 Applying tasks migration to Supabase..."
echo ""

# Use the database URL from env
export $(grep DATABASE_URL .env | xargs)

# Replace asyncpg with postgresql for psql
DB_URL=$(echo $DATABASE_URL | sed 's/postgresql+asyncpg/postgresql/')

# Apply migration
psql "$DB_URL" -f migrations/013_task_sync_system.sql

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration applied successfully!"
    echo "   Created tables: tasks, task_sync_log, google_task_lists"
    echo ""
    echo "🔄 Now restart your backend server:"
    echo "   The tasks table is ready for two-way Linear sync!"
else
    echo ""
    echo "❌ Migration failed"
    echo ""
    echo "💡 Manual option:"
    echo "1. Go to: https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/editor"
    echo "2. Copy contents of: migrations/013_task_sync_system.sql"
    echo "3. Paste and run in SQL Editor"
fi

