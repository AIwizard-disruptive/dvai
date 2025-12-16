#!/usr/bin/env python
"""Run database migrations."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine
from app.config import settings
from sqlalchemy import text


async def run_migration(migration_file: Path):
    """Run a SQL migration file."""
    print(f"Running migration: {migration_file.name}")
    
    with open(migration_file, 'r') as f:
        sql = f.read()
    
    async with engine.begin() as conn:
        # Split by semicolons and execute each statement
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        
        for statement in statements:
            if statement:
                try:
                    await conn.execute(text(statement))
                except Exception as e:
                    print(f"Error executing statement: {e}")
                    print(f"Statement: {statement[:100]}...")
                    raise
    
    print(f"✓ Completed: {migration_file.name}")


async def main():
    """Run all migrations."""
    migrations_dir = Path(__file__).parent.parent / "migrations"
    
    if not migrations_dir.exists():
        print(f"Error: Migrations directory not found: {migrations_dir}")
        return
    
    # Get all SQL files sorted by name
    migration_files = sorted(migrations_dir.glob("*.sql"))
    
    if not migration_files:
        print("No migration files found.")
        return
    
    print(f"Found {len(migration_files)} migration(s)")
    print(f"Database: {settings.database_url}")
    print()
    
    for migration_file in migration_files:
        await run_migration(migration_file)
    
    print()
    print("✓ All migrations completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())



