#!/usr/bin/env python3
"""
Delete old tasks and recreate with proper assignees
"""
import asyncio
from app.integrations.linear import get_linear_client
from gql import gql


async def delete_recent_tasks():
    """Delete tasks DIS-50 through DIS-77 (recent test runs)."""
    
    print("\n🗑️  Deleting recent test tasks (DIS-50 to DIS-77)...")
    
    client = get_linear_client()
    
    # Get all issues
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
    
    teams = await client.get_teams()
    team_id = teams[0]['id']
    
    result = await client.client.execute_async(
        query,
        variable_values={
            "filter": {"team": {"id": {"eq": team_id}}}
        }
    )
    
    issues = result['issues']['nodes']
    
    # Delete tasks DIS-50 onwards
    delete_mutation = gql("""
        mutation DeleteIssue($id: String!) {
            issueDelete(id: $id) {
                success
            }
        }
    """)
    
    deleted = 0
    for issue in issues:
        identifier = issue['identifier']
        # Extract number from DIS-XX
        if identifier.startswith('DIS-'):
            num = int(identifier.split('-')[1])
            if num >= 50:  # Delete 50 onwards
                await client.client.execute_async(
                    delete_mutation,
                    variable_values={"id": issue['id']}
                )
                deleted += 1
                print(f"   ✓ Deleted: {identifier}")
    
    print(f"\n✓ Deleted {deleted} tasks")


if __name__ == "__main__":
    asyncio.run(delete_recent_tasks())



