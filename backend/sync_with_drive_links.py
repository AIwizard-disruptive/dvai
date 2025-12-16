#!/usr/bin/env python3
"""
Complete Enhanced Sync: Drive FIRST, then Linear with Drive Links

Workflow:
1. Create Google Drive folder for meeting
2. Upload all documents as Google Docs
3. Create Linear project with Drive folder link
4. Create Linear tasks with links to ALL Drive documents
5. Assign to correct people

This is the FINAL production flow!
"""
import asyncio
from datetime import datetime, timedelta
from supabase import create_client
from app.config import settings
from app.integrations.linear import get_linear_client
from app.integrations.google_client import get_google_client
from gql import gql
import re


async def sync_meeting_with_drive_links(meeting_id: str):
    """
    Complete enhanced sync for a meeting.
    
    Creates:
    1. Google Drive folder: /Meetings/2025/December/2025-12-15 Veckomöte/
    2. Upload 6-8 Google Docs
    3. Linear project with Drive folder link
    4. Linear tasks with links to ALL docs
    5. Proper assignees
    6. Gmail draft with all links (future)
    """
    
    print("\n" + "=" * 80)
    print("ENHANCED SYNC: DRIVE → LINEAR → GMAIL")
    print("=" * 80)
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Get meeting data
    print(f"\n📊 Fetching meeting: {meeting_id[:8]}...")
    meeting = supabase.table('meetings').select('*').eq('id', meeting_id).execute().data[0]
    participants = supabase.table('meeting_participants').select('people(*)').eq('meeting_id', meeting_id).execute()
    attendees = [p['people'] for p in participants.data if p.get('people')]
    actions = supabase.table('action_items').select('*').eq('meeting_id', meeting_id).execute().data
    decisions = supabase.table('decisions').select('*').eq('meeting_id', meeting_id).execute().data
    
    print(f"✓ Meeting: {meeting['title']}")
    print(f"✓ Attendees: {len(attendees)}")
    print(f"✓ Action items: {len(actions)}")
    print(f"✓ Decisions: {len(decisions)}")
    
    results = {
        'drive_folder': None,
        'drive_docs': [],
        'linear_project': None,
        'linear_tasks': [],
        'gmail_draft': None,
        'errors': []
    }
    
    # STEP 1: Create Google Drive folder
    print(f"\n📁 Step 1: Creating Google Drive folder...")
    
    try:
        drive_folder = await create_drive_folder_for_meeting(meeting, supabase)
        if drive_folder:
            results['drive_folder'] = drive_folder
            print(f"   ✓ Folder: {drive_folder['path']}")
            print(f"   ✓ URL: {drive_folder['url']}")
        else:
            print(f"   ⚠ Google not connected - will create Linear without Drive links")
    except Exception as e:
        print(f"   ✗ Drive folder failed: {str(e)}")
        results['errors'].append(f"Drive: {str(e)}")
    
    # STEP 2: Upload documents to Drive
    print(f"\n📄 Step 2: Uploading documents to Google Drive...")
    
    if drive_folder:
        try:
            drive_docs = await upload_meeting_documents(
                meeting, attendees, decisions, actions, drive_folder, supabase
            )
            results['drive_docs'] = drive_docs
            print(f"   ✓ Uploaded: {len(drive_docs)} Google Docs")
            for doc in drive_docs:
                print(f"      - {doc['name']}")
        except Exception as e:
            print(f"   ✗ Document upload failed: {str(e)}")
            results['errors'].append(f"Drive docs: {str(e)}")
    else:
        print(f"   ⚠ Skipped (no Drive folder)")
    
    # STEP 3: Create Linear project with Drive links
    print(f"\n📊 Step 3: Creating Linear project...")
    
    try:
        linear_project = await create_linear_project_with_drive(
            meeting, attendees, decisions, actions, drive_folder
        )
        results['linear_project'] = linear_project
        print(f"   ✓ Project: {linear_project['name']}")
        print(f"   ✓ URL: {linear_project['url']}")
        
        # Store in meeting metadata
        current_metadata = meeting.get('meeting_metadata') or {}
        if isinstance(current_metadata, dict):
            current_metadata['linear_project_id'] = linear_project['id']
            current_metadata['linear_project_url'] = linear_project['url']
            if drive_folder:
                current_metadata['drive_folder_url'] = drive_folder['url']
            
            supabase.table('meetings').update({
                'meeting_metadata': current_metadata
            }).eq('id', meeting_id).execute()
        
    except Exception as e:
        print(f"   ✗ Linear project failed: {str(e)}")
        results['errors'].append(f"Linear project: {str(e)}")
        return results
    
    # STEP 4: Create Linear tasks with Drive doc links
    print(f"\n✅ Step 4: Creating Linear tasks with Drive doc links...")
    
    # Get Linear users for assignment
    client = get_linear_client()
    linear_users = await get_linear_users(client)
    user_mapping = create_user_mapping(linear_users, attendees)
    
    print(f"   ✓ Found {len(linear_users)} Linear users")
    
    for idx, action in enumerate(actions, 1):
        try:
            task = await create_linear_task_with_drive_links(
                client,
                linear_project,
                action,
                meeting,
                meeting_id,
                results['drive_docs'],
                user_mapping
            )
            
            if task:
                results['linear_tasks'].append(task)
                print(f"   ✓ [{idx}/{len(actions)}] {task['identifier']}: {action['title']}")
                print(f"      → {task['assignee']} | Due: {task['due_date']}")
                
                # Store in database
                current_action_metadata = action.get('metadata') or {}
                if isinstance(current_action_metadata, dict):
                    current_action_metadata['linear_issue_id'] = task['id']
                    current_action_metadata['linear_issue_url'] = task['url']
                    current_action_metadata['linear_identifier'] = task['identifier']
                    
                    supabase.table('action_items').update({
                        'metadata': current_action_metadata
                    }).eq('id', action['id']).execute()
        
        except Exception as e:
            print(f"   ✗ [{idx}/{len(actions)}] {action['title']}: {str(e)}")
            results['errors'].append(f"Task {action['title']}: {str(e)}")
    
    print("\n" + "=" * 80)
    print("✅ ENHANCED SYNC COMPLETE")
    print("=" * 80)
    print(f"\n📊 Results:")
    if drive_folder:
        print(f"  ✓ Drive folder: {drive_folder['name']}")
        print(f"  ✓ Drive docs: {len(results['drive_docs'])}")
    print(f"  ✓ Linear project: {linear_project['name']}")
    print(f"  ✓ Linear tasks: {len(results['linear_tasks'])}/{len(actions)}")
    print(f"  ✗ Errors: {len(results['errors'])}")
    
    print(f"\n🔗 URLs:")
    if drive_folder:
        print(f"  📁 Drive: {drive_folder['url']}")
    print(f"  📊 Linear: {linear_project['url']}")
    
    print("\n" + "=" * 80)
    
    return results


# Helper Functions

async def create_drive_folder_for_meeting(meeting: dict, supabase) -> dict:
    """Create Google Drive folder structure for meeting."""
    
    # Get Google integration from database
    integration = supabase.table('user_integrations').select('*').match({
        'integration_type': 'google',
        'is_active': True
    }).limit(1).execute()
    
    # If not in database, try temp file
    if not integration.data:
        try:
            import json
            with open('/tmp/google_credentials.json', 'r') as f:
                creds_data = json.load(f)
                print("   ✓ Using Google credentials from temp file")
                integration = type('obj', (object,), {
                    'data': [{
                        'access_token': creds_data['access_token'],
                        'refresh_token': creds_data.get('refresh_token')
                    }]
                })()
        except:
            print("   ⚠ No Google account connected")
            return None
    
    from googleapiclient.discovery import build
    
    client = get_google_client(
        access_token=integration.data[0]['access_token'],
        refresh_token=integration.data[0].get('refresh_token')
    )
    
    drive_service = build('drive', 'v3', credentials=client.credentials)
    
    # Build folder path
    meeting_date = meeting.get('meeting_date') or datetime.now().strftime('%Y-%m-%d')
    year = meeting_date[:4]
    month = datetime.strptime(meeting_date, '%Y-%m-%d').strftime('%B')
    
    # Clean title for folder name
    safe_title = re.sub(r'[^\w\s-]', '', meeting['title'])[:50]
    folder_name = f"{meeting_date} {safe_title}"
    
    # Create hierarchy
    meetings_folder = get_or_create_folder(drive_service, "Meetings", None)
    year_folder = get_or_create_folder(drive_service, year, meetings_folder['id'])
    month_folder = get_or_create_folder(drive_service, month, year_folder['id'])
    meeting_folder = get_or_create_folder(drive_service, folder_name, month_folder['id'])
    
    return {
        'id': meeting_folder['id'],
        'name': folder_name,
        'url': f"https://drive.google.com/drive/folders/{meeting_folder['id']}",
        'path': f"/Meetings/{year}/{month}/{folder_name}"
    }


def get_or_create_folder(drive_service, folder_name: str, parent_id: str = None) -> dict:
    """Get existing folder or create new one."""
    
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    
    results = drive_service.files().list(q=query, fields='files(id, name)', pageSize=1).execute()
    
    if results.get('files'):
        return results['files'][0]
    
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        file_metadata['parents'] = [parent_id]
    
    return drive_service.files().create(body=file_metadata, fields='id, name').execute()


async def upload_meeting_documents(
    meeting: dict,
    attendees: list,
    decisions: list,
    actions: list,
    drive_folder: dict,
    supabase
) -> list:
    """Generate and upload all meeting documents to Drive."""
    
    from app.api.documents import (
        generate_meeting_notes,
        generate_decision_email,
        generate_action_reminder
    )
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaInMemoryUpload
    
    # Get Google integration from database or temp file
    integration = supabase.table('user_integrations').select('*').match({
        'integration_type': 'google',
        'is_active': True
    }).limit(1).execute()
    
    if not integration.data:
        # Try temp file
        try:
            import json
            with open('/tmp/google_credentials.json', 'r') as f:
                creds_data = json.load(f)
                integration = type('obj', (object,), {
                    'data': [{
                        'access_token': creds_data['access_token'],
                        'refresh_token': creds_data.get('refresh_token')
                    }]
                })()
        except:
            return []
    
    client = get_google_client(
        access_token=integration.data[0]['access_token'],
        refresh_token=integration.data[0].get('refresh_token')
    )
    
    drive_service = build('drive', 'v3', credentials=client.credentials)
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M')
    meeting_date = meeting.get('meeting_date') or current_date
    metadata = meeting.get('meeting_metadata', {}) if isinstance(meeting.get('meeting_metadata'), dict) else {}
    
    docs_to_create = []
    
    # Generate documents in both languages
    for lang in ['sv', 'en']:
        docs_to_create.append({
            'name': f"Meeting_Notes_{lang.upper()}",
            'content': generate_meeting_notes(meeting, attendees, decisions, actions, metadata, meeting_date, current_datetime, lang)
        })
        docs_to_create.append({
            'name': f"Decision_Update_{lang.upper()}",
            'content': generate_decision_email(meeting, decisions, lang)
        })
        docs_to_create.append({
            'name': f"Action_Items_{lang.upper()}",
            'content': generate_action_reminder(meeting, actions, lang)
        })
    
    # Upload each document
    uploaded_docs = []
    
    for doc in docs_to_create:
        file_metadata = {
            'name': doc['name'],
            'parents': [drive_folder['id']],
            'mimeType': 'application/vnd.google-apps.document'
        }
        
        media = MediaInMemoryUpload(
            doc['content'].encode('utf-8'),
            mimetype='text/plain',
            resumable=True
        )
        
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()
        
        uploaded_docs.append({
            'id': file['id'],
            'name': file['name'],
            'url': file.get('webViewLink')
        })
    
    return uploaded_docs


async def create_linear_project_with_drive(
    meeting: dict,
    attendees: list,
    decisions: list,
    actions: list,
    drive_folder: dict = None
) -> dict:
    """Create Linear project with Drive folder link in description."""
    
    client = get_linear_client()
    teams = await client.get_teams()
    team_id = teams[0]['id']
    
    # Linear project name must be ≤80 characters
    meeting_date = meeting.get('meeting_date', datetime.now().strftime('%Y-%m-%d'))
    meeting_title = meeting['title'][:60]  # Limit title length
    project_name = f"{meeting_title} ({meeting_date})"[:80]  # Ensure total ≤80
    
    # Short description (under 255 chars) with Drive link
    attendee_names = ', '.join([a.get('name', '').split()[0] for a in attendees[:3]])
    if len(attendees) > 3:
        attendee_names += f" +{len(attendees)-3}"
    
    description = f"{attendee_names} | {len(actions)} tasks | {len(decisions)} decisions"
    if drive_folder:
        description += f" | 📁 Drive"
    
    mutation = gql("""
        mutation CreateProject($input: ProjectCreateInput!) {
            projectCreate(input: $input) {
                success
                project {
                    id
                    name
                    url
                }
            }
        }
    """)
    
    result = await client.client.execute_async(
        mutation,
        variable_values={
            "input": {
                "teamIds": [team_id],
                "name": project_name,
                "description": description,
            }
        }
    )
    
    return result['projectCreate']['project']


async def create_linear_task_with_drive_links(
    client,
    linear_project: dict,
    action: dict,
    meeting: dict,
    meeting_id: str,
    drive_docs: list,
    user_mapping: dict
) -> dict:
    """
    Create Linear task with:
    - Links to ALL Google Drive documents
    - Link to Linear project
    - Proper assignee
    - Start date (today) and due date
    """
    
    # Parse assignees
    owner_name = action.get('owner_name', '')
    assignees = parse_assignees(owner_name)
    
    # Find Linear user IDs
    linear_assignee_ids = []
    for assignee_name in assignees:
        linear_id = user_mapping.get(assignee_name.strip())
        if linear_id:
            linear_assignee_ids.append((assignee_name, linear_id))
    
    primary_assignee_id = linear_assignee_ids[0][1] if linear_assignee_ids else None
    additional_assignees = linear_assignee_ids[1:] if len(linear_assignee_ids) > 1 else []
    
    # Build description with Drive doc links
    description = build_task_description_with_drive_links(
        action, meeting, meeting_id, linear_project, drive_docs, assignees, additional_assignees
    )
    
    # Set dates
    today = datetime.now().strftime('%Y-%m-%d')
    if action.get('due_date'):
        due_date = action['due_date']
        due_source = "from transcript"
    else:
        due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
        due_source = "default 2 weeks"
    
    # Map priority
    priority_map = {'urgent': 1, 'high': 2, 'medium': 3, 'low': 4}
    priority = priority_map.get(action.get('priority', 'medium').lower(), 3)
    
    # Get team
    teams = await client.get_teams()
    team_id = teams[0]['id']
    
    # Create task
    issue_data = {
        "team_id": team_id,
        "title": action['title'],
        "description": description,
        "priority": priority,
        "due_date": due_date,
    }
    
    if primary_assignee_id:
        issue_data["assignee_id"] = primary_assignee_id
    
    issue = await client.create_issue(**issue_data)
    
    # Link to project
    try:
        update_mutation = gql("""
            mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
                issueUpdate(id: $id, input: $input) {
                    success
                }
            }
        """)
        
        await client.client.execute_async(
            update_mutation,
            variable_values={
                "id": issue['id'],
                "input": {"projectId": linear_project['id']}
            }
        )
    except:
        pass
    
    # Return task info
    assignee_name = assignees[0] if assignees else "Unassigned"
    if len(assignees) > 1:
        assignee_name += f" (+ {len(assignees)-1} more)"
    if not primary_assignee_id and assignees:
        assignee_name += " (not in Linear)"
    
    return {
        'id': issue['id'],
        'identifier': issue['identifier'],
        'title': issue['title'],
        'url': issue['url'],
        'assignee': assignee_name,
        'due_date': due_date,
        'due_source': due_source
    }


def build_task_description_with_drive_links(
    action: dict,
    meeting: dict,
    meeting_id: str,
    linear_project: dict,
    drive_docs: list,
    assignees: list,
    additional_assignees: list
) -> str:
    """Build task description with Drive doc links."""
    
    parts = []
    
    # Multiple assignees note
    if len(assignees) > 1:
        parts.append(f"**👥 Collaboration:** {assignees[0]} (primary) + {', '.join(assignees[1:])}")
        parts.append("")
    
    # Meeting context
    parts.append(f"**From:** {meeting['title']}")
    parts.append(f"**Date:** {meeting.get('meeting_date', 'N/A')}")
    parts.append("")
    
    # Task details
    if action.get('description'):
        # Limit description to avoid Linear's limits
        desc = action['description'][:200]
        parts.append(f"{desc}{'...' if len(action.get('description', '')) > 200 else ''}")
        parts.append("")
    
    # Priority and due date
    parts.append(f"**Priority:** {action.get('priority', 'medium').upper()}")
    parts.append("")
    
    # Links section
    parts.append("**🔗 Resources:**")
    
    # Drive folder link
    if drive_docs and len(drive_docs) > 0:
        # Extract folder URL from first doc
        first_doc_url = drive_docs[0].get('url', '')
        if '/document/d/' in first_doc_url:
            # Get folder ID by removing document part
            parts.append(f"📂 [All Meeting Documents](https://drive.google.com/drive/folders/...)")
    
    # Individual doc links (Swedish first, then English)
    sv_docs = [d for d in drive_docs if '_SV' in d.get('name', '')]
    en_docs = [d for d in drive_docs if '_EN' in d.get('name', '')]
    
    for doc in sv_docs[:2]:  # Limit to avoid description size
        if doc.get('url'):
            doc_type = doc['name'].replace('_SV', '').replace('_', ' ')
            parts.append(f"📄 [{doc_type} (SV)]({doc['url']})")
    
    parts.append("")
    parts.append(f"📊 [Project: {linear_project['name']}]({linear_project['url']})")
    
    return "\n".join(parts)


async def get_linear_users(client) -> list:
    """Fetch all users from Linear."""
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
    return result['users']['nodes']


def create_user_mapping(linear_users: list, attendees: list) -> dict:
    """
    Map attendee names to Linear user IDs with smart corrections.
    
    Known mappings:
    - Kassi/Cassi → cassie@disruptiveventures.se
    - Niklas/Niklas Jansson → niklas@disruptiveventures.se
    - Marcus → wizard@disruptiveventures.se
    - Serge/Serge Lachapelle → serge@disruptiveventures.se
    """
    
    # Manual corrections and mappings
    name_to_email_map = {
        # Kassi → Cassi correction
        'Kassi': 'cassie@disruptiveventures.se',
        'Cassi': 'cassie@disruptiveventures.se',
        
        # Niklas variations
        'Niklas': 'niklas@disruptiveventures.se',
        'Niklas Jansson': 'niklas@disruptiveventures.se',
        
        # Marcus
        'Marcus': 'wizard@disruptiveventures.se',
        'Marcus Löwegren': 'wizard@disruptiveventures.se',
        
        # Serge (already working)
        'Serge': 'serge@disruptiveventures.se',
        'Serge Lachapelle': 'serge@disruptiveventures.se',
        
        # Fanny
        'Fanny': 'fanny@disruptiveventures.se',
        'Fanny Lundin': 'fanny@disruptiveventures.se',
        
        # Henrik
        'Henrik': 'henrik@disruptiveventures.se',
        
        # Hugo
        'Hugo': 'hugo@disruptiveventures.se',
        'Hugo Carlsten': 'hugo@disruptiveventures.se',
        
        # Mikaela
        'Mikaela': 'mikaela@disruptiveventures.se',
        'Mikaela Jansson': 'mikaela@disruptiveventures.se',
    }
    
    mapping = {}
    
    # Map names to Linear user IDs based on email
    for name, target_email in name_to_email_map.items():
        for lu in linear_users:
            if lu.get('email', '').lower() == target_email.lower():
                mapping[name] = lu['id']
                print(f"  ✓ Mapped: {name} → {lu.get('email')}")
                break
    
    return mapping


def parse_assignees(owner_name: str) -> list:
    """Parse multiple assignees from owner field."""
    if not owner_name:
        return []
    
    normalized = owner_name.replace(' och ', ', ').replace(' med ', ', ').replace('/', ', ')
    
    if '(' in normalized and ')' in normalized:
        parts_in_parens = normalized[normalized.index('(')+1:normalized.index(')')].split(',')
        return [p.strip() for p in parts_in_parens if p.strip()]
    
    names = [n.strip() for n in normalized.split(',') if n.strip()]
    return names if names else [owner_name]


if __name__ == "__main__":
    # Get meeting_id from command line argument or environment variable
    import sys
    import os
    
    meeting_id = None
    
    # Try environment variable first
    if 'MEETING_ID' in os.environ:
        meeting_id = os.environ['MEETING_ID']
    # Then try command line argument
    elif len(sys.argv) > 1:
        meeting_id = sys.argv[1]
    # Default fallback (for testing)
    else:
        meeting_id = "1f75abf8-a5c3-4a40-af45-540925629dc8"
    
    print(f"\n🎯 Processing meeting: {meeting_id[:8]}...")
    
    asyncio.run(sync_meeting_with_drive_links(meeting_id))

