#!/usr/bin/env python3
"""
Fix assignee matching and autocorrect Kassi → Cassi

Current Linear users:
- niklas@disruptiveventures.se
- jakob@disruptiveventures.se
- cassie@disruptiveventures.se  (note: Cassie, not Kassi!)
- wizard@disruptiveventures.se
- peo@disruptiveventures.se
- Serge Lachapelle

Meeting attendees:
- Henrik
- Hugo Carlsten
- Niklas Jansson
- Mikaela Jansson
- Fanny Lundin
- Serge Lachapelle ✅ (matches!)

Fix:
1. Autocorrect Kassi → Cassi everywhere
2. Map Niklas Jansson → niklas@disruptiveventures.se
3. Map names to emails for better matching
"""
import asyncio
from datetime import datetime, timedelta
from supabase import create_client
from app.config import settings
from app.integrations.linear import get_linear_client
from gql import gql


async def fix_and_resync():
    """Fix Kassi→Cassi and improve assignee matching."""
    
    print("\n" + "=" * 80)
    print("FIX ASSIGNEES AND KASSI → CASSI")
    print("=" * 80)
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    meeting_id = "1f75abf8-a5c3-4a40-af45-540925629dc8"
    
    # STEP 1: Fix Kassi → Cassi in database
    print("\n1. Fixing Kassi → Cassi in all documents...")
    
    # Update action items
    actions = supabase.table('action_items').select('*').eq('meeting_id', meeting_id).execute().data
    
    for action in actions:
        if 'Kassi' in action.get('title', '') or 'Kassi' in action.get('description', '') or 'Kassi' in action.get('owner_name', ''):
            updated_data = {}
            if 'Kassi' in action.get('title', ''):
                updated_data['title'] = action['title'].replace('Kassi', 'Cassi')
            if 'Kassi' in action.get('description', ''):
                updated_data['description'] = action['description'].replace('Kassi', 'Cassi')
            if 'Kassi' in action.get('owner_name', ''):
                updated_data['owner_name'] = action['owner_name'].replace('Kassi', 'Cassi')
            
            if updated_data:
                supabase.table('action_items').update(updated_data).eq('id', action['id']).execute()
                print(f"   ✓ Fixed: {action['title']}")
    
    # Update participants
    participants = supabase.table('meeting_participants').select('id, people(*)').eq('meeting_id', meeting_id).execute()
    
    for participant in participants.data:
        person = participant.get('people')
        if person and 'Kassi' in person.get('name', ''):
            person_id = person['id']
            supabase.table('people').update({
                'name': person['name'].replace('Kassi', 'Cassi')
            }).eq('id', person_id).execute()
            print(f"   ✓ Fixed participant: {person['name']} → Cassi")
    
    # STEP 2: Get Linear users and create better mapping
    print("\n2. Creating enhanced user mapping...")
    
    client = get_linear_client()
    
    query = gql("""
        query GetUsers {
            users {
                nodes {
                    id
                    name
                    email
                    displayName
                    active
                }
            }
        }
    """)
    
    result = await client.client.execute_async(query)
    linear_users = result['users']['nodes']
    
    print(f"\n📊 Linear users found:")
    for lu in linear_users:
        print(f"  - {lu.get('name') or lu.get('displayName', 'No name')} | {lu.get('email')}")
    
    # Create smart mapping with corrections
    mapping = create_smart_user_mapping(linear_users)
    
    print(f"\n📋 User mapping:")
    for name, linear_id in mapping.items():
        linear_user = next((u for u in linear_users if u['id'] == linear_id), None)
        if linear_user:
            print(f"  {name} → {linear_user.get('email')}")
    
    print("\n✅ Mapping ready with Kassi→Cassi correction!")
    print("\nTo apply: Re-run the sync or manually assign in Linear")


def create_smart_user_mapping(linear_users: list) -> dict:
    """
    Create smart mapping with known name variations.
    
    Linear users we know about:
    - cassie@disruptiveventures.se (Kassi → Cassi)
    - niklas@disruptiveventures.se (Niklas Jansson)
    - serge@disruptiveventures.se (Serge Lachapelle) ✅
    - wizard@disruptiveventures.se (Marcus)
    """
    
    mapping = {}
    
    # Manual mappings for known people
    manual_mappings = {
        # Kassi → Cassi correction
        'Kassi': 'cassie@disruptiveventures.se',
        'Cassi': 'cassie@disruptiveventures.se',
        
        # Niklas variations
        'Niklas': 'niklas@disruptiveventures.se',
        'Niklas Jansson': 'niklas@disruptiveventures.se',
        
        # Serge (already working)
        'Serge': 'serge@disruptiveventures.se',
        'Serge Lachapelle': 'serge@disruptiveventures.se',
        
        # Marcus
        'Marcus': 'wizard@disruptiveventures.se',
        'Marcus Löwegren': 'wizard@disruptiveventures.se',
    }
    
    # Match emails to Linear user IDs
    for name, email in manual_mappings.items():
        for lu in linear_users:
            if lu.get('email', '').lower() == email.lower():
                mapping[name] = lu['id']
                break
    
    return mapping


if __name__ == "__main__":
    asyncio.run(fix_and_resync())



