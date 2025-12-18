"""
Pipedrive Sync API Endpoints
============================
API endpoints for syncing Pipedrive data to local database.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from supabase import create_client
from app.config import settings
from app.services.pipedrive_sync import PipedriveSyncService

router = APIRouter(prefix="/api/pipedrive", tags=["Pipedrive"])


class SyncRequest(BaseModel):
    """Request to sync Pipedrive data."""
    portfolio_company_id: str


@router.post("/sync-stages")
async def sync_pipeline_stages(request: SyncRequest):
    """
    Sync pipeline stages from Pipedrive for a portfolio company.
    
    This will:
    1. Fetch stages from Pipedrive API
    2. Update local database with stage names and order
    3. Make stages available for Kanban board
    """
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        sync_service = PipedriveSyncService(supabase, settings.encryption_key)
        
        result = await sync_service.sync_pipeline_stages(request.portfolio_company_id)
        
        if result['success']:
            return JSONResponse({
                'success': True,
                'message': f"Successfully synced {result['stages_synced']} stages",
                'stages': result['stage_names']
            })
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Sync failed'))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stages/{portfolio_company_id}")
async def get_pipeline_stages(portfolio_company_id: str):
    """
    Get pipeline stages for a portfolio company.
    
    Returns stages ordered by stage_order, ready for Kanban board.
    """
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        sync_service = PipedriveSyncService(supabase, settings.encryption_key)
        
        stages = await sync_service.get_pipeline_stages(portfolio_company_id)
        
        return JSONResponse({
            'success': True,
            'stages': stages
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-all-companies")
async def sync_all_companies():
    """
    Sync pipeline stages for all portfolio companies with Pipedrive integration.
    """
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        sync_service = PipedriveSyncService(supabase, settings.encryption_key)
        
        # Get all active Pipedrive integrations
        integrations = supabase.table('portfolio_company_integrations') \
            .select('portfolio_company_id, portfolio_companies(organizations(name))') \
            .eq('integration_type', 'pipedrive') \
            .eq('is_active', True) \
            .execute()
        
        results = []
        
        for integration in integrations.data:
            pc_id = integration['portfolio_company_id']
            company_name = integration['portfolio_companies']['organizations']['name']
            
            print(f"Syncing stages for {company_name}...")
            result = await sync_service.sync_pipeline_stages(pc_id)
            
            results.append({
                'company': company_name,
                'portfolio_company_id': pc_id,
                **result
            })
        
        return JSONResponse({
            'success': True,
            'message': f"Synced stages for {len(results)} companies",
            'results': results
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
