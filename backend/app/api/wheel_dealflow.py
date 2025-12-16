"""Deal Flow Wheel - Investment Pipeline & Opportunities."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from supabase import create_client
from app.config import settings
from app.api.styles import get_dv_styles
from app.api.sidebar_component import get_admin_sidebar

router = APIRouter(prefix="/wheels", tags=["Wheels - Dealflow"])


@router.get("/dealflow", response_class=HTMLResponse)
async def dealflow_wheel():
    """Deal Flow wheel - Investment pipeline and opportunities."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get current user - Markus Löwegren
        people = supabase.table('people').select('*').execute().data
        current_user = next((p for p in people if 'marcus' in p.get('name', '').lower() or 'markus' in p.get('name', '').lower()), None)
        if not current_user:
            current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        
        # Get meetings related to deals
        meetings = supabase.table('meetings').select('*').order('created_at', desc=True).limit(20).execute().data
        
    except Exception as e:
        current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        meetings = []
        print(f"Error: {e}")
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Deal Flow - Admin</title>
    {get_dv_styles()}
</head>
<body>
    {get_admin_sidebar('dealflow', current_user.get('name', 'Admin User'), current_user.get('email', ''), current_user.get('linkedin_url', ''))}
    
    <div class="main-content">
        <div class="page-header">
            <div class="page-header-left">
                <h1 class="page-title">Deal Flow</h1>
                <p class="page-description">Investment pipeline and opportunities</p>
            </div>
        </div>
        
        <div class="container">
            <div class="dashboard-stats">
                <div class="stat-card">
                    <div class="stat-number">{len(meetings)}</div>
                    <div class="stat-label">Deal Meetings</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">12</div>
                    <div class="stat-label">Active Deals</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">5</div>
                    <div class="stat-label">Due Diligence</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">3</div>
                    <div class="stat-label">Term Sheets</div>
                </div>
            </div>
            
            <div class="info-box" style="padding: 16px; border: 1px solid var(--gray-200); border-radius: 8px; background: white; text-align: center;">
                <p style="color: var(--gray-600); font-size: 14px;">Deal flow tracking and pipeline visualization coming soon.</p>
                <p style="color: var(--gray-500); font-size: 13px; margin-top: 8px;">Most deal tracking happens in Linear.</p>
            </div>
        </div>
    </div>
</body>
</html>
    """
    
    return HTMLResponse(content=html)


@router.get("/dealflow/leads", response_class=HTMLResponse)
async def dealflow_leads():
    """Deal Flow - Leads page."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        people = supabase.table('people').select('*').limit(1).execute().data
        current_user = people[0] if people else {'name': 'Admin User', 'email': '', 'linkedin_url': ''}
    except:
        current_user = {'name': 'Admin User', 'email': '', 'linkedin_url': ''}
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Leads - Deal Flow</title>
    {get_dv_styles()}
</head>
<body>
    {get_admin_sidebar('leads', current_user.get('name', 'Admin User'), current_user.get('email', ''), current_user.get('linkedin_url', ''))}
    
    <div class="main-content">
        <div class="page-header">
            <div class="page-header-left">
                <h1 class="page-title">Leads</h1>
                <p class="page-description">Early-stage opportunities and sourcing pipeline</p>
            </div>
        </div>
        
        <div class="container">
            <div style="padding: 16px; border: 1px solid var(--gray-200); border-radius: 8px; background: white; text-align: center;">
                <p style="color: var(--gray-600); font-size: 14px;">Lead tracking and sourcing pipeline coming soon.</p>
                <p style="color: var(--gray-500); font-size: 13px; margin-top: 8px;">Most lead tracking happens in Linear.</p>
            </div>
        </div>
    </div>
</body>
</html>
    """
    return HTMLResponse(content=html)


@router.get("/dealflow/deals", response_class=HTMLResponse)
async def dealflow_deals():
    """Deal Flow - Active Deals page."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        people = supabase.table('people').select('*').limit(1).execute().data
        current_user = people[0] if people else {'name': 'Admin User', 'email': '', 'linkedin_url': ''}
    except:
        current_user = {'name': 'Admin User', 'email': '', 'linkedin_url': ''}
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Deals - Deal Flow</title>
    {get_dv_styles()}
</head>
<body>
    {get_admin_sidebar('deals', current_user.get('name', 'Admin User'), current_user.get('email', ''), current_user.get('linkedin_url', ''))}
    
    <div class="main-content">
        <div class="page-header">
            <div class="page-header-left">
                <h1 class="page-title">Active Deals</h1>
                <p class="page-description">Due diligence and decision pipeline</p>
            </div>
        </div>
        
        <div class="container">
            <div style="padding: 16px; border: 1px solid var(--gray-200); border-radius: 8px; background: white; text-align: center;">
                <p style="color: var(--gray-600); font-size: 14px;">Active deal tracking and due diligence dashboard coming soon.</p>
                <p style="color: var(--gray-500); font-size: 13px; margin-top: 8px;">Most deal management happens in Linear.</p>
            </div>
        </div>
    </div>
</body>
</html>
    """
    return HTMLResponse(content=html)


@router.get("/dealflow/docs", response_class=HTMLResponse)
async def dealflow_docs():
    """Deal Flow - Documents page."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        people = supabase.table('people').select('*').limit(1).execute().data
        current_user = people[0] if people else {'name': 'Admin User', 'email': '', 'linkedin_url': ''}
    except:
        current_user = {'name': 'Admin User', 'email': '', 'linkedin_url': ''}
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Deal Documents - Deal Flow</title>
    {get_dv_styles()}
</head>
<body>
    {get_admin_sidebar('dealflow-docs', current_user.get('name', 'Admin User'), current_user.get('email', ''), current_user.get('linkedin_url', ''))}
    
    <div class="main-content">
        <div class="page-header">
            <div class="page-header-left">
                <h1 class="page-title">Deal Documents</h1>
                <p class="page-description">Term sheets, due diligence materials, legal docs</p>
            </div>
        </div>
        
        <div class="container">
            <div style="padding: 16px; border: 1px solid var(--gray-200); border-radius: 8px; background: white; text-align: center;">
                <p style="color: var(--gray-600); font-size: 14px;">Deal document library and repository coming soon.</p>
                <p style="color: var(--gray-500); font-size: 13px; margin-top: 8px;">Most documents stored in Google Drive.</p>
            </div>
        </div>
    </div>
</body>
</html>
    """
    return HTMLResponse(content=html)


