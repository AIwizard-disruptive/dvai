#!/usr/bin/env python3
"""
Setup wizard@disruptiveventures.se profile and Google Tasks sync
Run this after setting up the database migrations
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.database import get_db
from sqlalchemy import text

async def setup_wizard():
    """Setup wizard profile and sync configuration"""
    
    print("=" * 70)
    print("SETTING UP WIZARD@DISRUPTIVEVENTURES.SE")
    print("=" * 70)
    print()
    
    async for db in get_db():
        try:
            # Get org_id
            result = await db.execute(text("SELECT id, name FROM orgs LIMIT 1"))
            org = result.fetchone()
            
            if not org:
                print("❌ No org found! Please create an org first.")
                return
            
            org_id, org_name = org
            print(f"✅ Using org: {org_name} (ID: {org_id})")
            print()
            
            # Update or create wizard profile
            print("📝 Updating wizard profile...")
            await db.execute(text("""
                INSERT INTO people (
                    org_id, name, email, work_email, person_type,
                    job_title, department, bio, email_domain
                ) VALUES (
                    :org_id, 'Wizard', 'wizard@disruptiveventures.se', 
                    'wizard@disruptiveventures.se', 'internal',
                    'AI Assistant', 'Operations',
                    'AI-powered assistant helping with task management, meeting automation, and workflow optimization.',
                    'disruptiveventures.se'
                )
                ON CONFLICT (org_id, email) DO UPDATE SET
                    work_email = EXCLUDED.work_email,
                    job_title = EXCLUDED.job_title,
                    department = EXCLUDED.department,
                    bio = EXCLUDED.bio,
                    updated_at = NOW()
                RETURNING id, name, email, job_title
            """), {"org_id": str(org_id)})
            
            wizard = await db.fetchone()
            wizard_id, wizard_name, wizard_email, wizard_title = wizard
            
            print(f"✅ Wizard profile updated:")
            print(f"   ID: {wizard_id}")
            print(f"   Name: {wizard_name}")
            print(f"   Email: {wizard_email}")
            print(f"   Title: {wizard_title}")
            print()
            
            # Check if user_integrations table exists
            result = await db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'user_integrations'
                )
            """))
            table_exists = (await result.fetchone())[0]
            
            if table_exists:
                print("📋 Checking Google integration...")
                # Check if Google integration exists
                result = await db.execute(text("""
                    SELECT id, integration_type, is_active 
                    FROM user_integrations 
                    WHERE person_id = :person_id 
                    AND integration_type = 'google'
                """), {"person_id": str(wizard_id)})
                
                integration = await result.fetchone()
                
                if integration:
                    print(f"✅ Google integration found (Active: {integration[2]})")
                else:
                    print("⚠️  No Google integration found")
                    print("   → Run OAuth flow to connect Google account")
            else:
                print("⚠️  user_integrations table not found")
                print("   → Run migration 005_user_integrations.sql first")
            
            print()
            print("=" * 70)
            print("✅ WIZARD SETUP COMPLETE")
            print("=" * 70)
            print()
            print("NEXT STEPS:")
            print("1. Connect Google account via OAuth:")
            print("   http://localhost:8000/user-integrations/google/connect")
            print()
            print("2. Test Google Tasks sync:")
            print("   python backend/sync_google_tasks.py")
            print()
            
            await db.commit()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(setup_wizard())
