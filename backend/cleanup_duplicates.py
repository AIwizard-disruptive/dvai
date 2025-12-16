#!/usr/bin/env python3
"""
Clean up duplicate meetings and their Linear projects.
"""
import asyncio
from supabase import create_client
from app.config import settings
from app.integrations.linear import get_linear_client
from gql import gql


async def cleanup_duplicates():
    """Delete duplicate meetings and Linear projects."""
    
    print("\n" + "=" * 80)
    print("CLEANUP DUPLICATE MEETINGS")
    print("=" * 80)
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Keep only the Swedish meeting with ID we know
    keep_meeting_id = "1f75abf8-a5c3-4a40-af45-540925629dc8"
    
    # Get all meetings
    meetings = supabase.table('meetings').select('id, title, created_at').execute().data
    
    print(f"\n📊 Found {len(meetings)} meetings in database")
    
    # Find duplicates (same title but different ID)
    swedish_meetings = [m for m in meetings if 'Veckomöte' in m['title']]
    
    print(f"✓ Swedish meetings found: {len(swedish_meetings)}")
    for m in swedish_meetings:
        keep = "✓ KEEP" if m['id'] == keep_meeting_id else "✗ DELETE"
        print(f"  {keep} - {m['id'][:8]}... {m['title']}")
    
    # Delete duplicate meetings
    deleted_meetings = 0
    for meeting in swedish_meetings:
        if meeting['id'] != keep_meeting_id:
            try:
                # Delete meeting (cascade will delete related data)
                supabase.table('meetings').delete().eq('id', meeting['id']).execute()
                deleted_meetings += 1
                print(f"   ✓ Deleted meeting: {meeting['id'][:8]}...")
            except Exception as e:
                print(f"   ✗ Failed to delete {meeting['id'][:8]}: {e}")
    
    print(f"\n✓ Deleted {deleted_meetings} duplicate meetings")
    
    # Delete duplicate Linear projects
    print(f"\n📊 Cleaning up duplicate Linear projects...")
    
    client = get_linear_client()
    
    query = gql("""
        query GetProjects {
            projects {
                nodes {
                    id
                    name
                    url
                }
            }
        }
    """)
    
    result = await client.client.execute_async(query)
    projects = result['projects']['nodes']
    
    # Find Veckomöte projects
    vecko_projects = [p for p in projects if 'Veckomöte' in p['name']]
    
    print(f"✓ Found {len(vecko_projects)} Veckomöte projects in Linear")
    
    # Keep only the newest one, delete others
    if len(vecko_projects) > 1:
        # Sort by name to get most recent
        vecko_projects.sort(key=lambda x: x['name'], reverse=True)
        keep_project = vecko_projects[0]
        
        print(f"  ✓ KEEP: {keep_project['name']}")
        
        delete_mutation = gql("""
            mutation DeleteProject($id: String!) {
                projectDelete(id: $id) {
                    success
                }
            }
        """)
        
        for project in vecko_projects[1:]:
            try:
                await client.client.execute_async(
                    delete_mutation,
                    variable_values={"id": project['id']}
                )
                print(f"  ✗ Deleted duplicate: {project['name'][:50]}...")
            except Exception as e:
                print(f"  ⚠ Failed to delete project: {e}")
    
    print("\n" + "=" * 80)
    print("✅ CLEANUP COMPLETE")
    print("=" * 80)
    print(f"\nDatabase cleaned:")
    print(f"  ✓ Kept 1 meeting: Veckomöte...")
    print(f"  ✓ Deleted {deleted_meetings} duplicates")
    print(f"\nLinear cleaned:")
    print(f"  ✓ Kept 1 project")
    print(f"  ✓ Deleted {len(vecko_projects)-1 if len(vecko_projects) > 1 else 0} duplicate projects")
    print("\n✅ Ready for batch processing!")


if __name__ == "__main__":
    asyncio.run(cleanup_duplicates())


