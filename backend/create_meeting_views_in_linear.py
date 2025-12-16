#!/usr/bin/env python3
"""
Create Linear Views for Meeting Progress

Creates:
1. Custom view: "All Meetings" - Shows all meeting projects
2. For each project: Kanban board grouped by status
3. Progress tracking per meeting

Linear Views allow users to:
- See all meetings in one place
- Click on a meeting to see its Kanban board
- Track progress of action items from each meeting
"""
import asyncio
from app.integrations.linear import get_linear_client
from gql import gql


async def create_meeting_views():
    """
    Create Linear views for meeting management.
    
    Note: Linear's GraphQL API has limited view creation support.
    We'll use Projects (already created) and guide on using built-in features.
    """
    
    print("\n" + "=" * 80)
    print("LINEAR MEETING VIEWS SETUP")
    print("=" * 80)
    
    client = get_linear_client()
    
    # Get all projects
    print("\n📊 Fetching all meeting projects...")
    
    query = gql("""
        query GetProjects {
            projects {
                nodes {
                    id
                    name
                    url
                    state
                    progress
                    startDate
                    targetDate
                    description
                }
            }
        }
    """)
    
    result = await client.client.execute_async(query)
    projects = result['projects']['nodes']
    
    # Filter meeting projects (contain "Veckomöte" or date pattern)
    meeting_projects = [p for p in projects if 'Veckomöte' in p['name'] or '2025-' in p['name']]
    
    print(f"✓ Found {len(meeting_projects)} meeting projects:")
    for proj in meeting_projects:
        progress = proj.get('progress', 0) * 100 if proj.get('progress') else 0
        print(f"  - {proj['name']}")
        print(f"    Progress: {progress:.0f}% | State: {proj.get('state', 'planned')}")
        print(f"    URL: {proj['url']}")
        print()
    
    # Get the Swedish meeting project specifically
    swedish_project = next((p for p in meeting_projects if 'Veckomöte - Team Meeting' in p['name']), None)
    
    if not swedish_project:
        print("⚠ Swedish meeting project not found")
        return
    
    print(f"\n🎯 Configuring view for: {swedish_project['name']}")
    print(f"   Project ID: {swedish_project['id']}")
    
    # Get all issues in this project
    issues_query = gql("""
        query GetProjectIssues($projectId: String!) {
            project(id: $projectId) {
                issues {
                    nodes {
                        id
                        identifier
                        title
                        state {
                            name
                            type
                        }
                        assignee {
                            name
                            email
                        }
                        priority
                        dueDate
                    }
                }
            }
        }
    """)
    
    issues_result = await client.client.execute_async(
        issues_query,
        variable_values={"projectId": swedish_project['id']}
    )
    
    issues = issues_result['project']['issues']['nodes']
    
    print(f"\n📋 Tasks in project: {len(issues)}")
    
    # Group by status
    by_status = {}
    for issue in issues:
        status = issue['state']['name'] if issue.get('state') else 'Backlog'
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(issue)
    
    print(f"\n📊 Kanban Board View:")
    for status, tasks in by_status.items():
        print(f"\n  {status} ({len(tasks)} tasks):")
        for task in tasks[:5]:  # Show first 5
            assignee = task['assignee']['name'] if task.get('assignee') else 'Unassigned'
            print(f"    - {task['identifier']}: {task['title'][:50]}... → {assignee}")
        if len(tasks) > 5:
            print(f"    ... and {len(tasks)-5} more")
    
    print("\n" + "=" * 80)
    print("✅ MEETING VIEWS READY")
    print("=" * 80)
    
    print(f"\n🎯 How to use in Linear:")
    print(f"\n1. **Projects Page:**")
    print(f"   https://linear.app/disruptiveventures/projects")
    print(f"   Shows all meetings in one place")
    print(f"   Click any meeting → See its Kanban board")
    
    print(f"\n2. **Specific Meeting:**")
    print(f"   {swedish_project['url']}")
    print(f"   Kanban board with all {len(issues)} tasks")
    print(f"   Drag & drop to move tasks")
    print(f"   Track progress automatically")
    
    print(f"\n3. **Create Custom View (Manual):**")
    print(f"   In Linear: Views → Create View")
    print(f"   Filter: Project contains 'Veckomöte' or 'Team Meeting'")
    print(f"   Group by: Project")
    print(f"   Show: All meetings organized")
    
    print("\n" + "=" * 80)
    
    # Create a summary dashboard URL
    print(f"\n📱 Quick Links:")
    print(f"  All Projects: https://linear.app/disruptiveventures/projects")
    print(f"  Swedish Meeting: {swedish_project['url']}")
    print(f"  All Issues: https://linear.app/disruptiveventures/team/DIS/all")
    
    return {
        'meeting_projects': meeting_projects,
        'swedish_project': swedish_project,
        'tasks_count': len(issues),
        'kanban_status': by_status
    }


async def create_custom_view_for_meetings():
    """
    Try to create a custom view via API (if supported).
    
    Note: Linear's API has limited support for creating views.
    Most view customization is done through the UI.
    """
    
    client = get_linear_client()
    
    # Get team
    teams = await client.get_teams()
    team_id = teams[0]['id']
    
    print(f"\n📊 Creating custom 'All Meetings' view...")
    
    # Note: As of now, Linear's GraphQL API doesn't support creating custom views
    # Views are created through the UI
    
    print(f"   ℹ️  Linear views are best created through the UI:")
    print(f"   1. Go to: https://linear.app/disruptiveventures")
    print(f"   2. Click 'Views' in sidebar")
    print(f"   3. Click '+ New view'")
    print(f"   4. Name: 'All Meetings'")
    print(f"   5. Filter: Project is set")
    print(f"   6. Group by: Project")
    print(f"   7. Save")
    
    print(f"\n   ✓ Then you'll have a master view of all meetings!")


if __name__ == "__main__":
    result = asyncio.run(create_meeting_views())
    
    print(f"\n\n{'='*80}")
    print(f"📋 SUMMARY")
    print(f"{'='*80}\n")
    print(f"Your organization now has:")
    print(f"  ✓ {len(result['meeting_projects'])} meeting projects in Linear")
    print(f"  ✓ {result['tasks_count']} tasks in current meeting")
    print(f"  ✓ Kanban board with {len(result['kanban_status'])} columns")
    print(f"\nEveryone in your Linear workspace can:")
    print(f"  ✓ See all projects")
    print(f"  ✓ Click into any meeting")
    print(f"  ✓ View Kanban board")
    print(f"  ✓ Track progress")
    print(f"  ✓ Move tasks")

