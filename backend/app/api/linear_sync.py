"""Linear user synchronization endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from app.middleware.auth import get_current_user
from app.services.linear_user_mapping import LinearUserMapper
from app.config import settings
from supabase import create_client

router = APIRouter(prefix="/integrations/linear", tags=["Linear Sync"])


@router.post("/sync-users")
async def sync_linear_users(user = Depends(get_current_user)):
    """
    Sync Linear users to database.
    Maps team member names to Linear user IDs.
    
    This ensures:
    - "Marcus's tasks" get assigned to Marcus in Linear
    - Marcus sees only HIS tasks in "My Issues"
    - No clutter from other people's tasks
    """
    
    if not settings.linear_api_key:
        raise HTTPException(400, "Linear API key not configured")
    
    # Get user's org
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    membership = supabase.table('org_memberships').select('org_id').eq('user_id', user.id).limit(1).execute()
    
    if not membership.data:
        raise HTTPException(400, "User not in any organization")
    
    org_id = membership.data[0]['org_id']
    
    # Sync users
    mapper = LinearUserMapper(org_id)
    result = await mapper.sync_linear_users(settings.linear_api_key)
    
    if not result['success']:
        raise HTTPException(500, f"Failed to sync: {result.get('error')}")
    
    return {
        "success": True,
        "users_synced": result['users_synced'],
        "users": result['users'],
        "message": f"Synced {result['users_synced']} Linear users. Tasks will now be assigned correctly!"
    }


@router.get("/user-mappings")
async def get_linear_mappings(user = Depends(get_current_user)):
    """View current name → Linear ID mappings."""
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    membership = supabase.table('org_memberships').select('org_id').eq('user_id', user.id).limit(1).execute()
    
    if not membership.data:
        raise HTTPException(400, "User not in any organization")
    
    org_id = membership.data[0]['org_id']
    
    mapper = LinearUserMapper(org_id)
    mappings = await mapper.get_all_mappings()
    
    return {
        "mappings": mappings,
        "count": len(mappings)
    }

