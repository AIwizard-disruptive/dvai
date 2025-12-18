"""
Pipedrive CRM Integration Client
=================================
Fetches deals, organizations, and persons from Pipedrive API
"""

import httpx
from typing import List, Dict, Optional
from datetime import datetime


class PipedriveClient:
    """Client for Pipedrive CRM API."""
    
    def __init__(self, api_token: str, company_domain: str = ""):
        """
        Initialize Pipedrive client.
        
        Args:
            api_token: Pipedrive API token
            company_domain: Company domain (e.g., 'coeo.pipedrive.com')
        """
        self.api_token = api_token
        self.base_url = "https://api.pipedrive.com/v1"
        self.company_domain = company_domain
    
    async def get_deals(
        self, 
        status: str = "all_not_deleted",
        stage_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get deals from Pipedrive.
        
        Args:
            status: 'open', 'won', 'lost', 'deleted', 'all_not_deleted'
            stage_id: Filter by specific stage
            limit: Max number of deals to return
        
        Returns:
            List of deal dictionaries
        """
        params = {
            "api_token": self.api_token,
            "status": status,
            "limit": limit,
            "sort": "update_time DESC"
        }
        
        if stage_id:
            params["stage_id"] = stage_id
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/deals",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get('success') and data.get('data'):
                    return data['data']
                return []
        
        except Exception as e:
            print(f"Error fetching Pipedrive deals: {e}")
            return []
    
    async def get_stages(self) -> List[Dict]:
        """Get all pipeline stages."""
        params = {"api_token": self.api_token}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/stages",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get('success') and data.get('data'):
                    return data['data']
                return []
        
        except Exception as e:
            print(f"Error fetching Pipedrive stages: {e}")
            return []
    
    async def get_organizations(self, limit: int = 100) -> List[Dict]:
        """Get organizations (companies) from Pipedrive."""
        params = {
            "api_token": self.api_token,
            "limit": limit
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/organizations",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get('success') and data.get('data'):
                    return data['data']
                return []
        
        except Exception as e:
            print(f"Error fetching Pipedrive organizations: {e}")
            return []
    
    async def get_persons(self, limit: int = 100) -> List[Dict]:
        """Get persons (contacts) from Pipedrive."""
        params = {
            "api_token": self.api_token,
            "limit": limit
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/persons",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get('success') and data.get('data'):
                    return data['data']
                return []
        
        except Exception as e:
            print(f"Error fetching Pipedrive persons: {e}")
            return []
    
    def normalize_deal(self, deal: Dict) -> Dict:
        """
        Normalize Pipedrive deal to standard format.
        
        Returns:
            {
                'id': str,
                'title': str,
                'value': float,
                'currency': str,
                'status': str,
                'stage_name': str,
                'stage_id': int,
                'organization_name': str,
                'person_name': str,
                'owner_name': str,
                'created_at': str,
                'updated_at': str,
                'expected_close_date': str,
            }
        """
        return {
            'id': str(deal.get('id', '')),
            'title': deal.get('title', 'Untitled Deal'),
            'value': deal.get('value', 0),
            'currency': deal.get('currency', 'SEK'),
            'status': deal.get('status', 'open'),
            'stage_name': deal.get('stage_name', 'Unknown'),
            'stage_id': deal.get('stage_id'),
            'organization_name': deal.get('org_name', '') if deal.get('org_id') else '',
            'person_name': deal.get('person_name', '') if deal.get('person_id') else '',
            'owner_name': deal.get('owner_name', '') if deal.get('user_id') else '',
            'created_at': deal.get('add_time', ''),
            'updated_at': deal.get('update_time', ''),
            'expected_close_date': deal.get('expected_close_date', ''),
            'probability': deal.get('probability'),
            'visible_to': deal.get('visible_to'),
        }

