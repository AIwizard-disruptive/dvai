#!/usr/bin/env python3
"""
Delete Linear tasks and projects.
Use this to clean up test tasks before re-running with Drive links.
"""
import asyncio
from app.config import settings
from app.integrations.linear import get_linear_client
from gql import gql


async def delete_linear_tasks():
    """Delete all test tasks from Linear."""
    
    print("\n" + "=" * 80)
    print("DELETE LINEAR TEST TASKS")
    print("=" * 80)
    
    # Task IDs to delete (from your test runs)
    task_identifiers_to_delete = [
        # First run (DIS-8 to DIS-21)
        "DIS-8", "DIS-9", "DIS-10", "DIS-11", "DIS-12", "DIS-13", "DIS-14",
        "DIS-15", "DIS-16", "DIS-17", "DIS-18", "DIS-19", "DIS-20", "DIS-21",
        # Second run (DIS-22 to DIS-35)
        "DIS-22", "DIS-23", "DIS-24", "DIS-25", "DIS-26", "DIS-27", "DIS-28",
        "DIS-29", "DIS-30", "DIS-31", "DIS-32", "DIS-33", "DIS-34", "DIS-35",
        # Third run (DIS-36 to DIS-49)
        "DIS-36", "DIS-37", "DIS-38", "DIS-39", "DIS-40", "DIS-41", "DIS-42",
        "DIS-43", "DIS-44", "DIS-45", "DIS-46", "DIS-47", "DIS-48", "DIS-49",
    ]
    
    client = get_linear_client()
    
    deleted = 0
    errors = 0
    
    print(f"\n🗑️  Deleting {len(task_identifiers_to_delete)} test tasks...")
    
    # Get all issues to find IDs
    query = gql("""
        query GetIssues($filter: IssueFilter) {
            issues(filter: $filter) {
                nodes {
                    id
                    identifier
                    title
                }
            }
        }
    """)
    
    # Get team ID
    teams = await client.get_teams()
    team_id = teams[0]['id']
    
    # Fetch all issues from team
    result = await client.client.execute_async(
        query,
        variable_values={
            "filter": {
                "team": {"id": {"eq": team_id}}
            }
        }
    )
    
    issues = result['issues']['nodes']
    
    print(f"✓ Found {len(issues)} total issues in Linear")
    
    # Delete matching tasks
    delete_mutation = gql("""
        mutation DeleteIssue($id: String!) {
            issueDelete(id: $id) {
                success
            }
        }
    """)
    
    for issue in issues:
        if issue['identifier'] in task_identifiers_to_delete:
            try:
                await client.client.execute_async(
                    delete_mutation,
                    variable_values={"id": issue['id']}
                )
                deleted += 1
                print(f"   ✓ Deleted: {issue['identifier']} - {issue['title']}")
            except Exception as e:
                errors += 1
                print(f"   ✗ Failed to delete {issue['identifier']}: {str(e)}")
    
    print("\n" + "=" * 80)
    print("✅ CLEANUP COMPLETE")
    print("=" * 80)
    print(f"\n📊 Results:")
    print(f"  ✓ Deleted: {deleted} tasks")
    print(f"  ✗ Errors: {errors}")
    print(f"\n🎯 Linear is now clean. Ready for proper sync with Drive links!")


async def delete_test_projects():
    """Delete test projects from Linear."""
    
    print("\n🗑️  Deleting test projects...")
    
    client = get_linear_client()
    
    # Get all projects
    query = gql("""
        query GetProjects {
            projects {
                nodes {
                    id
                    name
                }
            }
        }
    """)
    
    result = await client.client.execute_async(query)
    projects = result['projects']['nodes']
    
    # Find Veckomöte projects
    delete_mutation = gql("""
        mutation DeleteProject($id: String!) {
            projectDelete(id: $id) {
                success
            }
        }
    """)
    
    deleted = 0
    for project in projects:
        if 'Veckomöte' in project['name'] or 'Test' in project['name']:
            try:
                await client.client.execute_async(
                    delete_mutation,
                    variable_values={"id": project['id']}
                )
                deleted += 1
                print(f"   ✓ Deleted project: {project['name']}")
            except Exception as e:
                print(f"   ✗ Failed to delete project {project['name']}: {str(e)}")
    
    print(f"\n✓ Deleted {deleted} test projects")


async def cleanup_all():
    """Delete both tasks and projects."""
    await delete_linear_tasks()
    await delete_test_projects()


if __name__ == "__main__":
    import sys
    
    print("\n⚠️  WARNING: This will delete test tasks and projects from Linear!")
    print("Tasks to delete: DIS-8 through DIS-49 (42 tasks)")
    print("Projects to delete: Any containing 'Veckomöte' or 'Test'")
    print("\nType 'yes' to continue, anything else to cancel: ")
    
    # Auto-confirm for scripting
    if len(sys.argv) > 1 and sys.argv[1] == '--confirm':
        asyncio.run(cleanup_all())
    else:
        # In interactive mode, ask for confirmation
        import sys
        response = input()
        if response.lower() == 'yes':
            asyncio.run(cleanup_all())
        else:
            print("\n❌ Cancelled. No tasks deleted.")



