"""
Linear User Mapping Service
Maps meeting attendee names to Linear user IDs
Ensures tasks are assigned to the correct person
"""
from typing import Optional, Dict, List
from supabase import create_client
from app.config import settings
from app.integrations.linear import get_linear_client


class LinearUserMapper:
    """
    Maps attendee names (from meetings) to Linear user IDs.
    
    How it works:
    1. Fetch all Linear users in workspace
    2. Store name → Linear user ID mapping
    3. When creating task for "Marcus", look up Marcus's Linear ID
    4. Task gets assigned to Marcus's Linear account
    5. Marcus sees it in "My Issues", others don't
    """
    
    def __init__(self, org_id: str):
        self.org_id = org_id
        self.supabase = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )
    
    async def sync_linear_users(self, linear_api_key: str) -> Dict:
        """
        Fetch all users from Linear and store mappings.
        Run this once when setting up Linear integration.
        
        Returns:
            Dictionary with sync results
        """
        try:
            # Get Linear users
            client = get_linear_client(api_key=linear_api_key)
            
            # Search for all users (empty query returns all)
            users = await client.search_users("")
            
            if not users:
                return {
                    "success": False,
                    "error": "No users found in Linear workspace"
                }
            
            # Store mappings in database
            mappings = []
            for user in users:
                mapping = {
                    'org_id': self.org_id,
                    'person_name': user['name'],
                    'person_email': user.get('email'),
                    'linear_user_id': user['id'],
                    'integration_data': {
                        'display_name': user.get('displayName'),
                        'avatar_url': user.get('avatarUrl'),
                        'is_active': user.get('active', True),
                    }
                }
                mappings.append(mapping)
            
            # Upsert all mappings
            self.supabase.table('linear_user_mappings').upsert(
                mappings,
                on_conflict='org_id,person_email'
            ).execute()
            
            return {
                "success": True,
                "users_synced": len(mappings),
                "users": [
                    {
                        "name": u['name'],
                        "email": u.get('email'),
                        "linear_id": u['id']
                    }
                    for u in users
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_linear_user_id(
        self,
        person_name: Optional[str] = None,
        person_email: Optional[str] = None
    ) -> Optional[str]:
        """
        Get Linear user ID for a person.
        Tries multiple matching strategies.
        
        Args:
            person_name: Name from meeting (e.g., "Marcus", "Fanny")
            person_email: Email if available
        
        Returns:
            Linear user ID or None if no match
        """
        
        # Try email match first (most reliable)
        if person_email:
            result = self.supabase.table('linear_user_mappings').select(
                'linear_user_id'
            ).match({
                'org_id': self.org_id,
                'person_email': person_email
            }).limit(1).execute()
            
            if result.data:
                return result.data[0]['linear_user_id']
        
        # Try exact name match
        if person_name:
            result = self.supabase.table('linear_user_mappings').select(
                'linear_user_id'
            ).match({
                'org_id': self.org_id,
                'person_name': person_name
            }).limit(1).execute()
            
            if result.data:
                return result.data[0]['linear_user_id']
        
        # Try fuzzy name match (case-insensitive, partial)
        if person_name:
            result = self.supabase.table('linear_user_mappings').select(
                'linear_user_id, person_name'
            ).eq('org_id', self.org_id).execute()
            
            if result.data:
                # Normalize names for comparison
                search_name = person_name.lower().strip()
                
                for mapping in result.data:
                    stored_name = mapping['person_name'].lower().strip()
                    
                    # Check if names match (first name, last name, or full name)
                    if search_name in stored_name or stored_name in search_name:
                        return mapping['linear_user_id']
                    
                    # Check first name only
                    search_first = search_name.split()[0] if ' ' in search_name else search_name
                    stored_first = stored_name.split()[0] if ' ' in stored_name else stored_name
                    
                    if search_first == stored_first:
                        return mapping['linear_user_id']
        
        # No match found
        return None
    
    async def add_manual_mapping(
        self,
        person_name: str,
        linear_user_id: str,
        person_email: Optional[str] = None
    ) -> Dict:
        """
        Manually add a name → Linear ID mapping.
        Useful when automatic sync doesn't catch everyone.
        
        Example:
            mapper.add_manual_mapping(
                person_name="Marcus",
                linear_user_id="abc-123-def",
                person_email="marcus@disruptiveventures.se"
            )
        """
        try:
            self.supabase.table('linear_user_mappings').upsert({
                'org_id': self.org_id,
                'person_name': person_name,
                'person_email': person_email,
                'linear_user_id': linear_user_id,
            }, on_conflict='org_id,person_email').execute()
            
            return {"success": True}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_all_mappings(self) -> List[Dict]:
        """Get all Linear user mappings for this org."""
        result = self.supabase.table('linear_user_mappings').select(
            '*'
        ).eq('org_id', self.org_id).execute()
        
        return result.data


async def sync_linear_users_for_org(org_id: str, linear_api_key: str) -> Dict:
    """
    Convenience function to sync Linear users for an organization.
    
    Usage:
        result = await sync_linear_users_for_org(org_id, api_key)
        print(f"Synced {result['users_synced']} users")
    """
    mapper = LinearUserMapper(org_id)
    return await mapper.sync_linear_users(linear_api_key)


