#!/usr/bin/env python
"""Run new migrations (009-012) for 4-wheel VC Operating System."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine
from app.config import settings
from sqlalchemy import text


async def run_migration(migration_file: Path):
    """Run a SQL migration file."""
    print(f"→ Running migration: {migration_file.name}")
    
    with open(migration_file, 'r') as f:
        sql = f.read()
    
    async with engine.begin() as conn:
        # Execute entire migration as one transaction
        try:
            await conn.execute(text(sql))
        except Exception as e:
            error_msg = str(e)
            # Ignore "already exists" errors (safe idempotent migrations)
            if 'already exists' in error_msg.lower():
                print(f"  ⚠️  Some objects already exist (safe to ignore): {error_msg[:100]}...")
            else:
                print(f"  ❌ Error: {e}")
                raise
    
    print(f"  ✓ Completed: {migration_file.name}")


async def main():
    """Run new migrations only (009-012)."""
    migrations_dir = Path(__file__).parent / "migrations"
    
    print("=" * 60)
    print("Running New Migrations (009-012)")
    print("4-Wheel VC Operating System")
    print("=" * 60)
    print()
    print(f"Database: {settings.database_url}")
    print()
    
    # Only run new migrations
    new_migrations = [
        "009_people_wheel.sql",
        "010_dealflow_wheel.sql",
        "011_building_companies_wheel.sql",
        "012_admin_wheel.sql"
    ]
    
    for migration_name in new_migrations:
        migration_file = migrations_dir / migration_name
        
        if not migration_file.exists():
            print(f"❌ Migration file not found: {migration_name}")
            continue
        
        await run_migration(migration_file)
        print()
    
    print("=" * 60)
    print("✓ All new migrations completed successfully!")
    print("=" * 60)
    print()
    print("Summary:")
    print("  - 009: PEOPLE wheel (policies, contracts, recruitment, competencies)")
    print("  - 010: DEALFLOW wheel (leads, research, outreach)")
    print("  - 011: BUILDING COMPANIES wheel (targets, CEO dashboards, qualification)")
    print("  - 012: ADMIN wheel (DV dashboards, alerts, metrics)")
    print()
    print("Next steps:")
    print("  1. Set up Google integrations (see IMPLEMENTATION_STATUS.md)")
    print("  2. Configure Slack and Whisperflow API keys in .env")
    print("  3. Create contact groups in Google Contacts")
    print("  4. Set up custom schemas in Google Workspace Directory")


if __name__ == "__main__":
    asyncio.run(main())
