"""Linear API integration for task management."""
import httpx
from typing import List, Optional
from app.config import settings


class LinearService:
    """Service for Linear API integration."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.linear_api_key
        if not self.api_key:
            raise ValueError("Linear API key not configured")
        
        self.api_url = settings.linear_api_url or "https://api.linear.app/graphql"
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def create_issue(
        self,
        title: str,
        description: str,
        team_id: str,
        assignee_name: Optional[str] = None,
        priority: str = "medium",
        due_date: Optional[str] = None
    ) -> dict:
        """
        Create a Linear issue from action item.
        
        Args:
            title: Issue title
            description: Issue description
            team_id: Linear team ID
            assignee_name: Name of assignee (will lookup by name)
            priority: Priority level (low/medium/high/urgent)
            due_date: Due date in YYYY-MM-DD format
        
        Returns:
            Created issue data with ID and URL
        """
        
        # Map priority to Linear priority values (0-4)
        priority_map = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "urgent": 4
        }
        linear_priority = priority_map.get(priority.lower(), 2)
        
        # Build mutation
        mutation = """
        mutation IssueCreate($input: IssueCreateInput!) {
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
        """
        
        variables = {
            "input": {
                "teamId": team_id,
                "title": title,
                "description": description,
                "priority": linear_priority
            }
        }
        
        # Add optional fields
        if due_date:
            variables["input"]["dueDate"] = due_date
        
        # TODO: Lookup assignee by name
        # Would need to query Linear users first and match by name
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                json={"query": mutation, "variables": variables},
                headers=self.headers,
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise ValueError(f"Linear API error: {response.text}")
            
            data = response.json()
            
            if data.get("errors"):
                raise ValueError(f"Linear GraphQL errors: {data['errors']}")
            
            issue_data = data.get("data", {}).get("issueCreate", {}).get("issue", {})
            
            return {
                "id": issue_data.get("id"),
                "identifier": issue_data.get("identifier"),
                "title": issue_data.get("title"),
                "url": issue_data.get("url")
            }
    
    async def get_teams(self) -> List[dict]:
        """Get all teams in the workspace."""
        
        query = """
        query Teams {
          teams {
            nodes {
              id
              name
              key
            }
          }
        }
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                json={"query": query},
                headers=self.headers,
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise ValueError(f"Linear API error: {response.text}")
            
            data = response.json()
            teams = data.get("data", {}).get("teams", {}).get("nodes", [])
            
            return teams




