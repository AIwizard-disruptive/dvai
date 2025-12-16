#!/usr/bin/env python
"""Clean database and show only real data."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from supabase import create_client
from app.config import settings

admin_supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)

meeting_id = '1f75abf8-a5c3-4a40-af45-540925629dc8'

print("=" * 80)
print("DATABASE CLEANUP - REMOVING NON-REAL DATA")
print("=" * 80)

# Show what's in database now
print("\n1. Current database state:")

decisions = admin_supabase.table('decisions').select('*').eq('meeting_id', meeting_id).execute()
print(f"   Decisions: {len(decisions.data)}")
for d in decisions.data:
    print(f"   - {d['decision']}")

actions = admin_supabase.table('action_items').select('*').eq('meeting_id', meeting_id).execute()
print(f"\n   Action Items: {len(actions.data)}")
for a in actions.data:
    print(f"   - {a['title']} (Owner: {a.get('owner_name', 'None')})")

people = admin_supabase.table('people').select('*').execute()
print(f"\n   People: {len(people.data)}")
for p in people.data:
    print(f"   - {p['name']} (Email: {p.get('email', 'None')})")

# Ask user which ones to keep
print("\n" + "=" * 80)
print("REAL ATTENDEES FROM MEETING TRANSCRIPT:")
print("=" * 80)
print("1. Henrik")
print("2. Hugo Carlsten")
print("3. Niklas Jansson")
print("4. Mikaela Jansson")
print("5. Fanny Lundin")
print("6. Serge Lachapelle")

print("\n" + "=" * 80)
print("These should stay. Everything else should be removed.")
print("=" * 80)



