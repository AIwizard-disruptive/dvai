#!/usr/bin/env python3
"""
Google Tasks Sync Service for wizard@disruptiveventures.se
Syncs tasks between database and Google Tasks
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.database import get_db
from sqlalchemy import text
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

class GoogleTasksSync:
    """Sync tasks with Google Tasks"""
    
    def __init__(self, access_token: str):
        self.creds = Credentials(token=access_token)
        self.service = build('tasks', 'v1', credentials=self.creds)
    
    async def get_wizard_person_id(self, db):
        """Get wizard's person ID"""
        result = await db.execute(text("""
            SELECT id FROM people 
            WHERE email = 'wizard@disruptiveventures.se'
            LIMIT 1
        """))
        person = await result.fetchone()
        return person[0] if person else None
    
    async def fetch_db_tasks(self, db, person_id: str):
        """Fetch tasks from database for wizard"""
        result = await db.execute(text("""
            SELECT 
                id, title, description, status, priority, 
                due_date, google_task_id, created_at, updated_at
            FROM tasks
            WHERE assigned_to_person_id = :person_id
            OR assigned_to_email = 'wizard@disruptiveventures.se'
            ORDER BY created_at DESC
        """), {"person_id": person_id})
        
        return await result.fetchall()
    
    def fetch_google_tasks(self, tasklist_id: str = '@default'):
        """Fetch tasks from Google Tasks"""
        try:
            results = self.service.tasks().list(
                tasklist=tasklist_id,
                showCompleted=True,
                showHidden=True
            ).execute()
            
            items = results.get('items', [])
            print(f"✅ Found {len(items)} tasks in Google Tasks")
            return items
        except Exception as e:
            print(f"❌ Error fetching Google Tasks: {e}")
            return []
    
    def create_google_task(self, task_data: dict, tasklist_id: str = '@default'):
        """Create task in Google Tasks"""
        try:
            google_task = {
                'title': task_data['title'],
                'notes': task_data.get('description', ''),
                'status': 'completed' if task_data['status'] == 'done' else 'needsAction'
            }
            
            if task_data.get('due_date'):
                google_task['due'] = f"{task_data['due_date']}T00:00:00Z"
            
            result = self.service.tasks().insert(
                tasklist=tasklist_id,
                body=google_task
            ).execute()
            
            print(f"✅ Created Google Task: {result['title']} (ID: {result['id']})")
            return result['id']
        except Exception as e:
            print(f"❌ Error creating Google Task: {e}")
            return None
    
    def update_google_task(self, google_task_id: str, task_data: dict, tasklist_id: str = '@default'):
        """Update task in Google Tasks"""
        try:
            google_task = {
                'id': google_task_id,
                'title': task_data['title'],
                'notes': task_data.get('description', ''),
                'status': 'completed' if task_data['status'] == 'done' else 'needsAction'
            }
            
            if task_data.get('due_date'):
                google_task['due'] = f"{task_data['due_date']}T00:00:00Z"
            
            self.service.tasks().update(
                tasklist=tasklist_id,
                task=google_task_id,
                body=google_task
            ).execute()
            
            print(f"✅ Updated Google Task: {task_data['title']}")
            return True
        except Exception as e:
            print(f"❌ Error updating Google Task: {e}")
            return False
    
    async def sync_db_to_google(self, db, person_id: str):
        """Sync database tasks to Google Tasks"""
        print()
        print("📤 Syncing DB → Google Tasks...")
        print("-" * 50)
        
        db_tasks = await self.fetch_db_tasks(db, person_id)
        
        if not db_tasks:
            print("ℹ️  No tasks found in database")
            return
        
        print(f"Found {len(db_tasks)} tasks in database")
        print()
        
        for task in db_tasks:
            task_id, title, description, status, priority, due_date, google_task_id, created_at, updated_at = task
            
            task_data = {
                'title': title,
                'description': description,
                'status': status,
                'priority': priority,
                'due_date': due_date
            }
            
            if google_task_id:
                # Update existing Google Task
                self.update_google_task(google_task_id, task_data)
            else:
                # Create new Google Task
                new_google_id = self.create_google_task(task_data)
                
                if new_google_id:
                    # Update database with Google Task ID
                    await db.execute(text("""
                        UPDATE tasks
                        SET google_task_id = :google_id,
                            last_synced_to_google_at = NOW()
                        WHERE id = :task_id
                    """), {
                        "google_id": new_google_id,
                        "task_id": str(task_id)
                    })
                    await db.commit()
    
    async def sync_google_to_db(self, db, person_id: str, org_id: str):
        """Sync Google Tasks to database"""
        print()
        print("📥 Syncing Google Tasks → DB...")
        print("-" * 50)
        
        google_tasks = self.fetch_google_tasks()
        
        if not google_tasks:
            print("ℹ️  No tasks found in Google Tasks")
            return
        
        print(f"Processing {len(google_tasks)} Google Tasks")
        print()
        
        for gtask in google_tasks:
            google_id = gtask['id']
            title = gtask.get('title', 'Untitled')
            notes = gtask.get('notes', '')
            status = 'done' if gtask.get('status') == 'completed' else 'todo'
            due_date = gtask.get('due', '').split('T')[0] if gtask.get('due') else None
            
            # Check if task exists in DB
            result = await db.execute(text("""
                SELECT id FROM tasks WHERE google_task_id = :google_id
            """), {"google_id": google_id})
            
            existing = await result.fetchone()
            
            if existing:
                # Update existing task
                await db.execute(text("""
                    UPDATE tasks
                    SET title = :title,
                        description = :description,
                        status = :status,
                        due_date = :due_date,
                        last_synced_to_google_at = NOW(),
                        updated_at = NOW()
                    WHERE google_task_id = :google_id
                """), {
                    "title": title,
                    "description": notes,
                    "status": status,
                    "due_date": due_date,
                    "google_id": google_id
                })
                print(f"✅ Updated: {title}")
            else:
                # Create new task in DB
                await db.execute(text("""
                    INSERT INTO tasks (
                        org_id, assigned_to_person_id, title, description,
                        status, due_date, source, google_task_id,
                        last_synced_to_google_at
                    ) VALUES (
                        :org_id, :person_id, :title, :description,
                        :status, :due_date, 'google_tasks', :google_id,
                        NOW()
                    )
                """), {
                    "org_id": org_id,
                    "person_id": person_id,
                    "title": title,
                    "description": notes,
                    "status": status,
                    "due_date": due_date,
                    "google_id": google_id
                })
                print(f"✅ Created: {title}")
        
        await db.commit()

async def main():
    """Main sync function"""
    print("=" * 70)
    print("GOOGLE TASKS SYNC - wizard@disruptiveventures.se")
    print("=" * 70)
    
    # Get access token
    print()
    print("⚠️  Need Google OAuth access token")
    print()
    print("Get it by:")
    print("1. Go to http://localhost:8000/integration-test")
    print("2. Click 'Connect Google'")
    print("3. Authorize")
    print("4. Copy the access_token from response")
    print()
    
    access_token = input("Paste access_token here (or press Enter to skip): ").strip()
    
    if not access_token:
        print()
        print("ℹ️  No token provided - showing what would happen:")
        print()
        
        async for db in get_db():
            # Get wizard person ID
            result = await db.execute(text("""
                SELECT id, name, email FROM people 
                WHERE email = 'wizard@disruptiveventures.se'
            """))
            person = await result.fetchone()
            
            if person:
                print(f"✅ Found wizard: {person[1]} ({person[2]})")
                
                # Show existing tasks
                result = await db.execute(text("""
                    SELECT title, status, google_task_id 
                    FROM tasks
                    WHERE assigned_to_person_id = :person_id
                    OR assigned_to_email = 'wizard@disruptiveventures.se'
                """), {"person_id": str(person[0])})
                
                tasks = await result.fetchall()
                
                if tasks:
                    print(f"\n📋 Wizard has {len(tasks)} tasks:")
                    for task in tasks:
                        sync_status = "✅ Synced" if task[2] else "⏳ Not synced"
                        print(f"   - {task[0]} [{task[1]}] {sync_status}")
                else:
                    print("\n📋 Wizard has no tasks yet")
            else:
                print("❌ Wizard profile not found")
                print("   Run: python backend/setup_wizard_sync.py")
        
        return
    
    # Run sync
    try:
        sync = GoogleTasksSync(access_token)
        
        async for db in get_db():
            # Get org and person info
            result = await db.execute(text("SELECT id FROM orgs LIMIT 1"))
            org = await result.fetchone()
            org_id = str(org[0]) if org else None
            
            person_id = await sync.get_wizard_person_id(db)
            
            if not person_id:
                print("❌ Wizard profile not found")
                print("   Run: python backend/setup_wizard_sync.py")
                return
            
            print(f"✅ Wizard person ID: {person_id}")
            
            # Bidirectional sync
            await sync.sync_db_to_google(db, person_id)
            await sync.sync_google_to_db(db, person_id, org_id)
            
            print()
            print("=" * 70)
            print("✅ SYNC COMPLETE")
            print("=" * 70)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
