"""Linear API integration."""
from typing import Optional
import httpx
from gql import Client, gql
from gql.transport.httpx import HTTPXAsyncTransport

from app.config import settings


class LinearClient:
    """Client for Linear API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.linear_api_key
        if not self.api_key:
            raise ValueError("Linear API key not configured")
        
        # Setup GraphQL client
        transport = HTTPXAsyncTransport(
            url=settings.linear_api_url,
            headers={"Authorization": self.api_key},
        )
        self.client = Client(transport=transport, fetch_schema_from_transport=True)
    
    async def create_issue(
        self,
        team_id: str,
        title: str,
        description: Optional[str] = None,
        assignee_id: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: Optional[int] = None,
        labels: Optional[list[str]] = None,
    ) -> dict:
        """
        Create a Linear issue.
        
        Args:
            team_id: Linear team ID
            title: Issue title
            description: Issue description (markdown)
            assignee_id: Assignee user ID
            due_date: Due date (YYYY-MM-DD)
            priority: Priority (0=None, 1=Urgent, 2=High, 3=Normal, 4=Low)
            labels: List of label IDs
        
        Returns:
            Created issue data
        """
        mutation = gql("""
            mutation CreateIssue($input: IssueCreateInput!) {
                issueCreate(input: $input) {
                    success
                    issue {
                        id
                        identifier
                        title
                        url
                    }
                }
            }
        """)
        
        input_data = {
            "teamId": team_id,
            "title": title,
        }
        
        if description:
            input_data["description"] = description
        if assignee_id:
            input_data["assigneeId"] = assignee_id
        if due_date:
            input_data["dueDate"] = due_date
        if priority is not None:
            input_data["priority"] = priority
        if labels:
            input_data["labelIds"] = labels
        
        result = await self.client.execute_async(
            mutation,
            variable_values={"input": input_data},
        )
        
        return result["issueCreate"]["issue"]
    
    async def update_issue(
        self,
        issue_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        state_id: Optional[str] = None,
        assignee_id: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> dict:
        """
        Update a Linear issue.
        
        Args:
            issue_id: Issue ID
            title: New title
            description: New description
            state_id: New state ID
            assignee_id: New assignee ID
            due_date: New due date
        
        Returns:
            Updated issue data
        """
        mutation = gql("""
            mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
                issueUpdate(id: $id, input: $input) {
                    success
                    issue {
                        id
                        identifier
                        title
                        url
                    }
                }
            }
        """)
        
        input_data = {}
        if title:
            input_data["title"] = title
        if description:
            input_data["description"] = description
        if state_id:
            input_data["stateId"] = state_id
        if assignee_id:
            input_data["assigneeId"] = assignee_id
        if due_date:
            input_data["dueDate"] = due_date
        
        result = await self.client.execute_async(
            mutation,
            variable_values={"id": issue_id, "input": input_data},
        )
        
        return result["issueUpdate"]["issue"]
    
    async def get_teams(self) -> list[dict]:
        """
        Get user's Linear teams.
        
        Returns:
            List of teams
        """
        query = gql("""
            query GetTeams {
                teams {
                    nodes {
                        id
                        name
                        key
                    }
                }
            }
        """)
        
        result = await self.client.execute_async(query)
        return result["teams"]["nodes"]
    
    async def get_workflow_states(self, team_id: str) -> list[dict]:
        """
        Get workflow states for a team.
        
        Args:
            team_id: Team ID
        
        Returns:
            List of workflow states
        """
        query = gql("""
            query GetWorkflowStates($teamId: String!) {
                team(id: $teamId) {
                    states {
                        nodes {
                            id
                            name
                            type
                        }
                    }
                }
            }
        """)
        
        result = await self.client.execute_async(
            query,
            variable_values={"teamId": team_id},
        )
        return result["team"]["states"]["nodes"]
    
    async def search_users(self, query: str) -> list[dict]:
        """
        Search for users by name or email.
        
        Args:
            query: Search query
        
        Returns:
            List of matching users
        """
        graphql_query = gql("""
            query SearchUsers($filter: UserFilter) {
                users(filter: $filter) {
                    nodes {
                        id
                        name
                        email
                    }
                }
            }
        """)
        
        result = await self.client.execute_async(
            graphql_query,
            variable_values={
                "filter": {
                    "or": [
                        {"name": {"containsIgnoreCase": query}},
                        {"email": {"containsIgnoreCase": query}},
                    ]
                }
            },
        )
        return result["users"]["nodes"]


def get_linear_client(api_key: Optional[str] = None) -> LinearClient:
    """Get Linear client instance."""
    return LinearClient(api_key=api_key)



