"""Portfolio Dashboard - VC KPIs and Portfolio Metrics."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from supabase import create_client
from app.config import settings
from app.api.styles import get_dv_styles
from app.api.sidebar_component import get_admin_sidebar

router = APIRouter(prefix="/wheels", tags=["Wheels - Portfolio"])


@router.get("/admin", response_class=HTMLResponse)
async def portfolio_dashboard():
    """Portfolio Dashboard - VC KPIs and portfolio metrics."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get current user - Markus Löwegren
        people = supabase.table('people').select('*').execute().data
        current_user = next((p for p in people if 'marcus' in p.get('name', '').lower() or 'markus' in p.get('name', '').lower()), None)
        if not current_user:
            current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        
    except Exception as e:
        current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        print(f"Error: {e}")
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfolio Dashboard - Admin</title>
    {get_dv_styles()}
    <style>
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }}
        
        .kpi-section {{
            margin-bottom: 32px;
        }}
        
        .section-title {{
            font-size: 14px;
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 16px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
    </style>
</head>
<body>
    {get_admin_sidebar('admin', current_user.get('name', 'Admin User'), current_user.get('email', ''), current_user.get('linkedin_url', ''))}
    
    <div class="main-content">
        <div class="page-header">
            <div class="page-header-left">
                <h1 class="page-title">Portfolio Dashboard</h1>
                <p class="page-description">VC KPIs and portfolio performance metrics</p>
            </div>
        </div>
        
        <div class="container">
            <!-- Portfolio KPIs -->
            <div class="kpi-section">
                <h2 class="section-title">Portfolio Overview</h2>
                <div class="kpi-grid">
                    <div class="stat-card">
                        <div class="stat-number">18</div>
                        <div class="stat-label">Active Companies</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">$8.4M</div>
                        <div class="stat-label">Total Invested</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">$24.2M</div>
                        <div class="stat-label">Current Valuation</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">2.9x</div>
                        <div class="stat-label">Portfolio Multiple</div>
                    </div>
                </div>
            </div>
            
            <!-- Performance Metrics -->
            <div class="kpi-section">
                <h2 class="section-title">Performance Metrics</h2>
                <div class="kpi-grid">
                    <div class="stat-card">
                        <div class="stat-number">42%</div>
                        <div class="stat-label">Avg Revenue Growth</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">85%</div>
                        <div class="stat-label">Survival Rate</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">12</div>
                        <div class="stat-label">Exits (All Time)</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">3.2x</div>
                        <div class="stat-label">Avg Exit Multiple</div>
                    </div>
                </div>
            </div>
            
            <!-- Fund Metrics -->
            <div class="kpi-section">
                <h2 class="section-title">Fund Metrics</h2>
                <div class="kpi-grid">
                    <div class="stat-card">
                        <div class="stat-number">$45M</div>
                        <div class="stat-label">Fund Size</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">72%</div>
                        <div class="stat-label">Deployed Capital</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">$12.8M</div>
                        <div class="stat-label">Dry Powder</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">24</div>
                        <div class="stat-label">Investments</div>
                    </div>
                </div>
            </div>
            
            <!-- Note -->
            <div class="info-box" style="padding: 16px; border: 1px solid var(--gray-200); border-radius: 8px; background: white;">
                <p style="color: var(--gray-600); font-size: 13px; line-height: 1.6;">
                    <strong style="color: var(--gray-900);">Note:</strong> These are template KPIs for layout purposes. 
                    Connect to your data sources to display real portfolio metrics. 
                    Detailed analytics and reporting happen in Linear and Google Sheets.
                </p>
            </div>
        </div>
    </div>
</body>
</html>
    """
    
    return HTMLResponse(content=html)


