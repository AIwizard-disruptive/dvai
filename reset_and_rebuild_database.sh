#!/bin/bash
# Reset and rebuild database from scratch
# ⚠️  WARNING: This will DELETE ALL DATA

set -e  # Exit on error

echo "🔥 DATABASE RESET SCRIPT"
echo "======================="
echo ""
echo "⚠️  WARNING: This will DELETE ALL DATA in your database!"
echo ""
read -p "Are you sure you want to continue? (type 'yes' to proceed): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Aborted"
    exit 1
fi

echo ""
echo "🔍 Checking for .env file..."

# Source environment variables
if [ -f "backend/.env" ]; then
    export $(grep -v '^#' backend/.env | xargs)
    echo "✓ Loaded backend/.env"
elif [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✓ Loaded .env"
else
    echo "❌ No .env file found!"
    echo ""
    echo "Please ensure you have one of these files with SUPABASE_DB_URL:"
    echo "  - backend/.env"
    echo "  - .env"
    exit 1
fi

# Check for database URL
if [ -z "$SUPABASE_DB_URL" ]; then
    echo "❌ SUPABASE_DB_URL not found in .env file!"
    echo ""
    echo "Add this to your .env file:"
    echo "SUPABASE_DB_URL=postgresql://postgres.[YOUR-PROJECT-REF].supabase.co:5432/postgres"
    exit 1
fi

echo "✓ Database URL found"
echo ""
echo "🗑️  Dropping all tables and rebuilding schema..."
echo ""

# Run the reset migration
psql "$SUPABASE_DB_URL" -f backend/migrations/RESET_DATABASE.sql

echo ""
echo "✅ DATABASE RESET COMPLETE!"
echo ""
echo "Next steps:"
echo "  1. Start your backend: cd backend && uvicorn app.main:app --reload"
echo "  2. Create an org and upload files via the API"
echo ""




