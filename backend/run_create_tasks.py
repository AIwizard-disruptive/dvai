#!/usr/bin/env python3
"""Actually run the task creation"""
import asyncio
import sys
from pathlib import Path

backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.database import get_db
from sqlalchemy import text

async def create_tasks():
    """Create all tasks for serge and wizard"""
    
    print("Creating tasks...")
    
    async for db in get_db():
        # Read the SQL file
        sql_file = backend_path / "migrations" / "CREATE_TASKS_SERGE_WIZARD.sql"
        
        with open(sql_file, 'r') as f:
            sql = f.read()
        
        # Execute it
        await db.execute(text(sql))
        await db.commit()
        
        print("✅ Tasks created!")

if __name__ == "__main__":
    asyncio.run(create_tasks())


