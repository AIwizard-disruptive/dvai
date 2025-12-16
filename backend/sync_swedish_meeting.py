#!/usr/bin/env python3
"""
Sync Swedish meeting to Linear
Creates project and all tasks from "Veckomöte - Team Meeting"
"""
import asyncio
import sys
from datetime import datetime, timedelta
from supabase import create_client
from app.config import settings
from app.integrations.linear import get_linear_client
from gql import gql


async def sync_swedish_meeting():
    """Create Linear project and tasks from Swedish meeting."""
    
    # Known meeting ID from earlier
    meeting_id = "1f75abf8-a5c3-4a40-af45-540925629dc8"
    
    print("\n" + "=" * 80)
    print("SYNCING SWEDISH MEETING TO LINEAR")
    print("=" * 80)
    
    # Connect to database
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Get meeting data
    print(f"\n📊 Fetching meeting: {meeting_id[:8]}...")
    meeting_response = supabase.table('meetings').select('*').eq('id', meeting_id).execute()
    
    if not meeting_response.data:
        print("❌ Meeting not found!")
        return
    
    meeting = meeting_response.data[0]
    print(f"✓ Found: {meeting['title']}")
    
    # Get participants
    participants = supabase.table('meeting_participants').select('people(*)').eq('meeting_id', meeting_id).execute()
    attendees = [p['people'] for p in participants.data if p.get('people')]
    print(f"✓ Attendees: {len(attendees)}")
    
    # Get action items
    actions = supabase.table('action_items').select('*').eq('meeting_id', meeting_id).execute().data
    print(f"✓ Action items: {len(actions)}")
    
    # Get decisions
    decisions = supabase.table('decisions').select('*').eq('meeting_id', meeting_id).execute().data
    print(f"✓ Decisions: {len(decisions)}")
    
    # Connect to Linear
    print(f"\n📊 Connecting to Linear...")
    client = get_linear_client()
    
    teams = await client.get_teams()
    if not teams:
        print("❌ No teams found in Linear")
        return
    
    team_id = teams[0]['id']
    team_name = teams[0]['name']
    print(f"✓ Team: {team_name} ({team_id[:8]}...)")
    
    # Fetch Linear users for assignee mapping
    print(f"\n👥 Fetching Linear users...")
    linear_users = await _get_linear_users(client)
    print(f"✓ Found {len(linear_users)} Linear users")
    for user in linear_users:
        print(f"  - {user['name']} ({user['email']})")
    
    # Create name mapping
    user_mapping = _create_user_mapping(linear_users, attendees)
    
    # CREATE LINEAR PROJECT
    print(f"\n🎯 Creating Linear project...")
    
    project_name = f"{meeting['title']} ({meeting.get('meeting_date', 'N/A')})"
    
    # Linear project description limited to 255 chars
    attendee_names = ', '.join([a.get('name', '').split()[0] for a in attendees[:4]])  # First names only
    if len(attendees) > 4:
        attendee_names += f" +{len(attendees)-4} more"
    
    project_description = f"{attendee_names} | {len(actions)} tasks | {len(decisions)} decisions | {meeting.get('meeting_date', 'N/A')}"
    
    # Keep it under 255 chars
    if len(project_description) > 250:
        project_description = project_description[:247] + "..."
    
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
    
    project_result = await client.client.execute_async(
        mutation,
        variable_values={
            "input": {
                "teamIds": [team_id],
                "name": project_name,
                "description": project_description,
            }
        }
    )
    
    linear_project = project_result['projectCreate']['project']
    print(f"✓ Project created: {linear_project['name']}")
    print(f"✓ URL: {linear_project['url']}")
    
    # CREATE TASKS
    print(f"\n📋 Creating {len(actions)} Linear tasks...")
    
    tasks_created = []
    
    for idx, action in enumerate(actions, 1):
        try:
            # Get assignee(s) from action
            owner_name = action.get('owner_name', '')
            assignees = _parse_assignees(owner_name)
            
            # Find Linear user IDs for assignees
            linear_assignee_ids = []
            for assignee_name in assignees:
                linear_id = user_mapping.get(assignee_name.strip())
                if linear_id:
                    linear_assignee_ids.append((assignee_name, linear_id))
            
            # Primary assignee (first one)
            primary_assignee_id = linear_assignee_ids[0][1] if linear_assignee_ids else None
            
            # Additional assignees (tag in description)
            additional_assignees = linear_assignee_ids[1:] if len(linear_assignee_ids) > 1 else []
            
            # Build description with assignee tags
            description = _build_task_description_with_assignees(
                action, meeting, meeting_id, assignees, additional_assignees
            )
            
            # Map priority
            priority_map = {'urgent': 1, 'high': 2, 'medium': 3, 'low': 4}
            priority = priority_map.get(action.get('priority', 'medium').lower(), 3)
            
            # Set dates
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Due date: Use transcript deadline if exists, otherwise 2 weeks from today
            if action.get('due_date'):
                due_date = action['due_date']
            else:
                two_weeks_later = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
                due_date = two_weeks_later
            
            # Create issue with assignee, start date, and due date
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
            
            # Try to link to project (might fail if project ID format is wrong)
            try:
                update_mutation = gql("""
                    mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
                        issueUpdate(id: $id, input: $input) {
                            success
                            issue {
                                id
                            }
                        }
                    }
                """)
                
                await client.client.execute_async(
                    update_mutation,
                    variable_values={
                        "id": issue['id'],
                        "input": {
                            "projectId": linear_project['id']
                        }
                    }
                )
            except:
                pass  # If project linking fails, task is still created
            
            # Show assignee status
            assignee_status = "Unassigned"
            if primary_assignee_id:
                primary_name = assignees[0] if assignees else "Unknown"
                if len(assignees) > 1:
                    assignee_status = f"{primary_name} (+ {len(assignees)-1} more)"
                else:
                    assignee_status = primary_name
            else:
                assignee_status = f"{action.get('owner_name', 'Unassigned')} (not in Linear)"
            
            # Show due date source
            due_date_source = "from transcript" if action.get('due_date') else "default 2 weeks"
            
            tasks_created.append({
                'identifier': issue['identifier'],
                'title': issue['title'],
                'url': issue['url'],
                'assignee': assignee_status,
                'due_date': due_date,
                'due_date_source': due_date_source
            })
            
            print(f"   ✓ [{idx}/{len(actions)}] {issue['identifier']}: {action['title']}")
            print(f"      → {assignee_status} | Due: {due_date} ({due_date_source})")
            
        except Exception as e:
            print(f"   ✗ [{idx}/{len(actions)}] {action['title']}: {str(e)}")
    
    print("\n" + "=" * 80)
    print("✅ SYNC COMPLETE")
    print("=" * 80)
    print(f"\n📊 Results:")
    print(f"  ✓ Project: {linear_project['name']}")
    print(f"  ✓ Tasks created: {len(tasks_created)}/{len(actions)}")
    print(f"\n🔗 Open in Linear:")
    print(f"  {linear_project['url']}")
    print("\n" + "=" * 80)
    
    # Save results
    print(f"\n📝 Tasks created:")
    for task in tasks_created:
        print(f"  {task['identifier']}: {task['title']} → {task['assignee']}")


async def _get_linear_users(client) -> list:
    """Fetch all users from Linear workspace."""
    try:
        # Get all users using GraphQL
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
    
    except Exception as e:
        print(f"⚠ Error fetching Linear users: {e}")
        return []


def _create_user_mapping(linear_users: list, attendees: list) -> dict:
    """
    Create mapping from meeting attendee names to Linear user IDs.
    
    Matching strategy:
    1. Match by email (most reliable)
    2. Match by full name
    3. Match by first name only
    4. Match by last name only
    """
    mapping = {}
    
    for attendee in attendees:
        attendee_name = attendee.get('name', '')
        attendee_email = attendee.get('email', '')
        
        # Try email match first (if attendee has @disruptiveventures email)
        if attendee_email and 'disruptiveventures' in attendee_email.lower():
            for lu in linear_users:
                if lu.get('email', '').lower() == attendee_email.lower():
                    mapping[attendee_name] = lu['id']
                    mapping[attendee_name.split()[0]] = lu['id']  # First name
                    print(f"  ✓ Mapped (email): {attendee_name} → {lu['email']}")
                    break
        
        # If no email match, try name matching
        if attendee_name not in mapping:
            for lu in linear_users:
                linear_name = lu.get('name', '') or lu.get('displayName', '')
                
                # Full name match
                if attendee_name.lower() == linear_name.lower():
                    mapping[attendee_name] = lu['id']
                    mapping[attendee_name.split()[0]] = lu['id']  # First name
                    print(f"  ✓ Mapped (name): {attendee_name} → {linear_name}")
                    break
                
                # First name match
                attendee_first = attendee_name.split()[0] if attendee_name else ''
                linear_first = linear_name.split()[0] if linear_name else ''
                
                if attendee_first and attendee_first.lower() == linear_first.lower():
                    mapping[attendee_name] = lu['id']
                    mapping[attendee_first] = lu['id']
                    print(f"  ✓ Mapped (first name): {attendee_name} → {linear_name}")
                    break
    
    return mapping


def _parse_assignees(owner_name: str) -> list:
    """
    Parse multiple assignees from owner_name field.
    
    Examples:
        "Fanny Lundin" → ["Fanny Lundin"]
        "Niklas Jansson och Fanny" → ["Niklas Jansson", "Fanny"]
        "Fanny/Mikaela med Serge" → ["Fanny", "Mikaela", "Serge"]
        "Team (Niklas, Henrik, Serge, Marcus)" → ["Niklas", "Henrik", "Serge", "Marcus"]
    """
    if not owner_name:
        return []
    
    # Replace common separators with commas
    normalized = owner_name
    normalized = normalized.replace(' och ', ', ')
    normalized = normalized.replace(' med ', ', ')
    normalized = normalized.replace('/', ', ')
    
    # Extract names from parentheses
    if '(' in normalized and ')' in normalized:
        parts_in_parens = normalized[normalized.index('(')+1:normalized.index(')')].split(',')
        return [p.strip() for p in parts_in_parens if p.strip()]
    
    # Split by comma
    names = [n.strip() for n in normalized.split(',') if n.strip()]
    
    return names if names else [owner_name]


def _build_task_description_with_assignees(
    action: dict,
    meeting: dict,
    meeting_id: str,
    all_assignees: list,
    additional_assignees: list
) -> str:
    """
    Build task description with proper assignee mentions.
    
    Primary assignee gets the task.
    Additional assignees are @mentioned in description for collaboration.
    """
    
    description_parts = []
    
    # Multiple assignees note
    if len(all_assignees) > 1:
        primary = all_assignees[0]
        others = ', '.join(all_assignees[1:])
        description_parts.append(f"**👥 Collaboration task:** Primary: {primary} | Also: {others}")
        description_parts.append("")
    
    # Meeting context
    description_parts.append(f"**From Meeting:** {meeting['title']}")
    description_parts.append(f"**Date:** {meeting.get('meeting_date', 'N/A')}")
    description_parts.append("")
    
    # Task details
    if action.get('description'):
        description_parts.append(f"**Details:**")
        description_parts.append(action['description'])
        description_parts.append("")
    
    # Priority and due date
    if action.get('priority'):
        description_parts.append(f"**Priority:** {action['priority'].upper()}")
    if action.get('due_date'):
        description_parts.append(f"**Due Date:** {action['due_date']}")
    
    # Tag additional assignees (Linear uses @mentions)
    if additional_assignees:
        description_parts.append("")
        description_parts.append("**Additional team members:**")
        for name, linear_id in additional_assignees:
            description_parts.append(f"- {name}")
    
    description_parts.append("")
    description_parts.append(f"**Meeting View:** http://localhost:8000/meeting/{meeting_id}")
    description_parts.append("")
    description_parts.append("---")
    description_parts.append("*Auto-generated from meeting action items*")
    
    return "\n".join(description_parts)


if __name__ == "__main__":
    asyncio.run(sync_swedish_meeting())

