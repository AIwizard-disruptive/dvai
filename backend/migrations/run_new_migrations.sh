#!/bin/bash

# Run new migrations (009-012) for 4-wheel VC Operating System
# Usage: ./run_new_migrations.sh

set -e  # Exit on error

echo "============================================"
echo "Running New Migrations (009-012)"
echo "4-Wheel VC Operating System"
echo "============================================"
echo ""

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL environment variable is not set"
    echo "Please set it first:"
    echo "  export DATABASE_URL='postgresql://user:pass@host:port/dbname'"
    exit 1
fi

echo "Database: $DATABASE_URL"
echo ""

# Run each migration
echo "→ Running migration 009: PEOPLE Wheel..."
psql "$DATABASE_URL" -f 009_people_wheel.sql
echo "✓ Migration 009 completed"
echo ""

echo "→ Running migration 010: DEALFLOW Wheel..."
psql "$DATABASE_URL" -f 010_dealflow_wheel.sql
echo "✓ Migration 010 completed"
echo ""

echo "→ Running migration 011: BUILDING COMPANIES Wheel..."
psql "$DATABASE_URL" -f 011_building_companies_wheel.sql
echo "✓ Migration 011 completed"
echo ""

echo "→ Running migration 012: ADMIN Wheel..."
psql "$DATABASE_URL" -f 012_admin_wheel.sql
echo "✓ Migration 012 completed"
echo ""

echo "============================================"
echo "✓ All migrations completed successfully!"
echo "============================================"
echo ""
echo "Summary:"
echo "  - 009: PEOPLE wheel (policies, contracts, recruitment, competencies)"
echo "  - 010: DEALFLOW wheel (leads, research, outreach)"
echo "  - 011: BUILDING COMPANIES wheel (targets, CEO dashboards, qualification)"
echo "  - 012: ADMIN wheel (DV dashboards, alerts, metrics)"
echo ""
echo "Next steps:"
echo "  1. Review new tables: psql \$DATABASE_URL -c '\\dt'"
echo "  2. Set up Google integrations (see IMPLEMENTATION_STATUS.md)"
echo "  3. Configure Slack and Whisperflow API keys"
echo "  4. Create contact groups in Google Contacts"
echo "  5. Set up custom schemas in Google Workspace Directory"
echo ""


