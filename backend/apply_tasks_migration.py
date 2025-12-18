#!/usr/bin/env python3
"""
Apply tasks migration to create tasks table
"""
from supabase import create_client
from app.config import settings
import sys

# Read the migration file
with open('migrations/013_task_sync_system.sql', 'r') as f:
    sql = f.read()

# Connect to Supabase
try:
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    print("🔄 Applying tasks migration...")
    print(f"   Database: {settings.supabase_url}")
    
    # Execute the SQL
    result = supabase.rpc('exec_sql', {'sql': sql}).execute()
    
    print("✅ Migration applied successfully!")
    print("   Created tables: tasks, task_sync_log, google_task_lists")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 Alternative: Apply migration manually via Supabase SQL Editor:")
    print(f"   1. Go to https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/editor")
    print(f"   2. Open migrations/013_task_sync_system.sql")
    print(f"   3. Copy and paste the SQL")
    print(f"   4. Run it")
    sys.exit(1)

