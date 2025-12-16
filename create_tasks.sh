#!/bin/bash
# Create tasks for serge@ and wizard@

echo "════════════════════════════════════════════════════════════"
echo "CREATING TASKS FOR SERGE@ AND WIZARD@"
echo "════════════════════════════════════════════════════════════"
echo ""

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not set!"
    echo ""
    echo "Set it with:"
    echo "export DATABASE_URL='your_supabase_connection_string'"
    exit 1
fi

echo "✅ DATABASE_URL is set"
echo ""

# Run the SQL script
echo "📝 Creating tasks..."
psql $DATABASE_URL -f backend/migrations/CREATE_TASKS_SERGE_WIZARD.sql

if [ $? -eq 0 ]; then
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "✅ TASKS CREATED SUCCESSFULLY!"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "📊 What was created:"
    echo "  - 11 tasks for Serge (investment & strategy)"
    echo "  - 11 tasks for Wizard (admin & support)"
    echo "  - 1 shared task for both"
    echo ""
    echo "🎯 Task types:"
    echo "  - Portfolio management"
    echo "  - Due diligence"
    echo "  - Board meetings"
    echo "  - LP reporting"
    echo "  - Networking"
    echo "  - Admin & scheduling"
    echo "  - Research"
    echo ""
    echo "🚀 NEXT STEPS:"
    echo "1. Run sync to push to Google Tasks:"
    echo "   cd backend"
    echo "   python sync_google_tasks.py"
    echo ""
    echo "2. Check your Google Tasks:"
    echo "   https://tasks.google.com"
    echo ""
    echo "3. Try updating a task in Google Tasks"
    echo "   Then run sync again to see it update in DB!"
    echo ""
else
    echo ""
    echo "❌ Error creating tasks"
    echo "Check the error messages above"
    exit 1
fi
