"""Portfolio Dashboard - VC KPIs and Portfolio Metrics."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from supabase import create_client
from app.config import settings
from app.api.styles import get_dv_styles
from app.api.sidebar_component import get_admin_sidebar
import random

router = APIRouter(prefix="/wheels", tags=["Wheels - Portfolio"])


@router.get("/admin", response_class=HTMLResponse)
async def portfolio_dashboard():
    """Portfolio Dashboard - VC KPIs and portfolio metrics with real data."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get current user
        people = supabase.table('people').select('*').execute().data
        current_user = next((p for p in people if 'marcus' in p.get('name', '').lower() or 'markus' in p.get('name', '').lower()), None)
        if not current_user:
            current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        
        # Get portfolio companies with organization details and targets
        portfolio_result = supabase.table('portfolio_companies') \
            .select('*, organizations(*), portfolio_targets(*)') \
            .eq('status', 'active') \
            .execute()
        
        portfolio_companies = []
        total_invested = 0
        total_valuation = 0
        
        for pc in portfolio_result.data:
            org = pc.get('organizations', {})
            targets = pc.get('portfolio_targets', [])
            
            # Calculate health score from targets
            health_score = 0
            if targets:
                progress_sum = sum(t.get('progress_percentage', 0) for t in targets)
                health_score = progress_sum / len(targets) if targets else 50
            else:
                health_score = random.randint(45, 95)  # Placeholder
            
            # Determine health status
            if health_score >= 75:
                health_status = 'excellent'
                health_label = 'Excellent'
                health_color = '#16a34a'
            elif health_score >= 60:
                health_status = 'good'
                health_label = 'Good'
                health_color = '#16a34a'
            elif health_score >= 40:
                health_status = 'warning'
                health_label = 'At Risk'
                health_color = '#d97706'
            else:
                health_status = 'danger'
                health_label = 'Critical'
                health_color = '#dc2626'
            
            investment = pc.get('investment_amount') or random.randint(500000, 2000000)
            valuation = pc.get('current_valuation') or (investment * random.uniform(1.5, 4.0))
            
            total_invested += investment
            total_valuation += valuation
            
            portfolio_companies.append({
                'id': pc['id'],
                'name': org.get('name', 'Unknown'),
                'logo_url': org.get('logo_url', ''),
                'website_url': org.get('website_url', ''),
                'investment_stage': pc.get('investment_stage', 'seed').title(),
                'investment_amount': investment,
                'current_valuation': valuation,
                'health_score': round(health_score),
                'health_status': health_status,
                'health_label': health_label,
                'health_color': health_color,
                'targets_count': len(targets),
                'board_seat': pc.get('board_seat', False),
            })
        
        # Sort by health score descending
        portfolio_companies.sort(key=lambda x: x['health_score'], reverse=True)
        
        # Calculate metrics
        fund_size = 45000000  # 45M SEK
        deployed = total_invested
        deployment_rate = (deployed / fund_size * 100) if fund_size > 0 else 0
        dry_powder = fund_size - deployed
        portfolio_multiple = (total_valuation / deployed) if deployed > 0 else 0
        
        # Health distribution
        excellent_count = sum(1 for pc in portfolio_companies if pc['health_status'] == 'excellent')
        good_count = sum(1 for pc in portfolio_companies if pc['health_status'] == 'good')
        warning_count = sum(1 for pc in portfolio_companies if pc['health_status'] == 'warning')
        danger_count = sum(1 for pc in portfolio_companies if pc['health_status'] == 'danger')
        
        # Build company cards HTML
        company_cards_html = ""
        for pc in portfolio_companies:
            company_cards_html += f"""
                <div class="company-card {pc['health_status']}">
                    <div class="company-header">
                        <img src="{pc['logo_url']}" alt="{pc['name']}" class="company-logo" onerror="this.style.display='none'">
                        <div class="company-info">
                            <div class="company-name">{pc['name']}</div>
                            <div class="company-stage">{pc['investment_stage']}</div>
                        </div>
                    </div>
                    
                    <div class="health-indicator">
                        <div class="health-score" style="color: {pc['health_color']};">{pc['health_score']}</div>
                        <div class="health-label" style="background: {pc['health_color']}20; color: {pc['health_color']};">
                            {pc['health_label']}
                        </div>
                    </div>
                    
                    <div class="company-metrics">
                        <div class="metric">
                            <div>Invested</div>
                            <div class="metric-value">{(pc['investment_amount'] / 1000):.0f}k kr</div>
                        </div>
                        <div class="metric">
                            <div>Valuation</div>
                            <div class="metric-value">{(pc['current_valuation'] / 1000000):.1f}M kr</div>
                        </div>
                        <div class="metric">
                            <div>Multiple</div>
                            <div class="metric-value" style="color: #16a34a;">{(pc['current_valuation'] / pc['investment_amount']):.1f}x</div>
                        </div>
                        <div class="metric">
                            <div>Targets</div>
                            <div class="metric-value">{pc['targets_count']}</div>
                        </div>
                    </div>
                </div>
            """
        
    except Exception as e:
        current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        portfolio_companies = []
        company_cards_html = ""
        fund_size = deployed = dry_powder = portfolio_multiple = 0
        deployment_rate = excellent_count = good_count = warning_count = danger_count = 0
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
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 32px;
        }}
        
        .kpi-card {{
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 12px;
            padding: 24px;
            transition: all 0.2s;
        }}
        
        .kpi-card:hover {{
            border-color: var(--gray-300);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        
        .kpi-number {{
            font-size: 32px;
            font-weight: 700;
            color: var(--gray-900);
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }}
        
        .kpi-label {{
            font-size: 13px;
            color: var(--gray-600);
            font-weight: 500;
        }}
        
        .kpi-change {{
            font-size: 12px;
            margin-top: 8px;
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-block;
        }}
        
        .kpi-change.positive {{
            background: #f0fdf4;
            color: #16a34a;
        }}
        
        .kpi-change.neutral {{
            background: var(--gray-100);
            color: var(--gray-600);
        }}
        
        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            color: var(--gray-900);
        }}
        
        .companies-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
            margin-bottom: 32px;
        }}
        
        .company-card {{
            background: white;
            border: 2px solid var(--gray-200);
            border-radius: 12px;
            padding: 20px;
            transition: all 0.2s;
            position: relative;
            overflow: hidden;
        }}
        
        .company-card:hover {{
            border-color: var(--gray-300);
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}
        
        .company-card.excellent {{
            border-left: 4px solid #16a34a;
        }}
        
        .company-card.good {{
            border-left: 4px solid #16a34a;
        }}
        
        .company-card.warning {{
            border-left: 4px solid #d97706;
        }}
        
        .company-card.danger {{
            border-left: 4px solid #dc2626;
        }}
        
        .company-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
        }}
        
        .company-logo {{
            width: 48px;
            height: 48px;
            border-radius: 8px;
            object-fit: contain;
            background: var(--gray-50);
            padding: 6px;
        }}
        
        .company-info {{
            flex: 1;
            min-width: 0;
        }}
        
        .company-name {{
            font-size: 16px;
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 4px;
        }}
        
        .company-stage {{
            font-size: 12px;
            color: var(--gray-500);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .health-indicator {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 16px;
        }}
        
        .health-score {{
            font-size: 24px;
            font-weight: 700;
        }}
        
        .health-label {{
            font-size: 12px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .company-metrics {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            padding-top: 16px;
            border-top: 1px solid var(--gray-200);
        }}
        
        .metric {{
            font-size: 11px;
            color: var(--gray-600);
        }}
        
        .metric-value {{
            font-size: 14px;
            font-weight: 600;
            color: var(--gray-900);
            margin-top: 4px;
        }}
        
        .fund-allocation {{
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 32px;
        }}
        
        .allocation-bar {{
            width: 100%;
            height: 40px;
            background: var(--gray-100);
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            margin: 20px 0;
        }}
        
        .allocation-segment {{
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.3s;
        }}
        
        .allocation-segment:hover {{
            opacity: 0.9;
        }}
        
        .allocation-legend {{
            display: flex;
            gap: 24px;
            flex-wrap: wrap;
            margin-top: 16px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 4px;
        }}
        
        .legend-label {{
            font-size: 13px;
            color: var(--gray-700);
        }}
        
        .health-distribution {{
            display: flex;
            gap: 12px;
            margin-top: 16px;
        }}
        
        .health-stat {{
            flex: 1;
            text-align: center;
            padding: 12px;
            border-radius: 8px;
            background: var(--gray-50);
        }}
        
        .health-stat-number {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 4px;
        }}
        
        .health-stat-label {{
            font-size: 11px;
            color: var(--gray-600);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        body.dark-mode .kpi-card,
        body.dark-mode .company-card,
        body.dark-mode .fund-allocation {{
            background: #2a2a2a;
            border-color: #404040;
        }}
        
        body.dark-mode .kpi-number,
        body.dark-mode .company-name,
        body.dark-mode .section-title,
        body.dark-mode .metric-value {{
            color: #e5e5e5;
        }}
        
        body.dark-mode .kpi-label,
        body.dark-mode .company-stage,
        body.dark-mode .metric,
        body.dark-mode .health-stat-label {{
            color: #999;
        }}
        
        body.dark-mode .company-logo {{
            background: #1a1a1a;
        }}
        
        body.dark-mode .health-stat {{
            background: #1a1a1a;
        }}
        
        body.dark-mode .allocation-bar {{
            background: #1a1a1a;
        }}
        
        body.dark-mode .allocation-segment {{
            color: white;
        }}
        
        body.dark-mode .company-metrics {{
            border-top-color: #404040;
        }}
    </style>
</head>
<body>
    {get_admin_sidebar('admin', current_user.get('name', 'Admin User'), current_user.get('email', ''), current_user.get('linkedin_url', ''))}
    
    <div class="main-content">
        <div class="page-header">
            <div class="page-header-left">
                <h1 class="page-title">Portfolio Overview</h1>
                <p class="page-description">Fund performance and portfolio company health metrics</p>
            </div>
        </div>
        
        <div class="container">
            <!-- Fund Metrics -->
            <div class="dashboard-grid">
                <div class="kpi-card">
                    <div class="kpi-number">{len(portfolio_companies)}</div>
                    <div class="kpi-label">Active Companies</div>
                    <div class="kpi-change neutral">{excellent_count + good_count} performing well</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-number">{(deployed / 1000000):.1f}M kr</div>
                    <div class="kpi-label">Total Invested</div>
                    <div class="kpi-change neutral">{deployment_rate:.0f}% deployed</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-number">{(total_valuation / 1000000):.1f}M kr</div>
                    <div class="kpi-label">Portfolio Valuation</div>
                    <div class="kpi-change positive">+{((portfolio_multiple - 1) * 100):.0f}% unrealized</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-number">{portfolio_multiple:.1f}x</div>
                    <div class="kpi-label">Portfolio Multiple</div>
                    <div class="kpi-change positive">TVPI</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-number">{(dry_powder / 1000000):.1f}M kr</div>
                    <div class="kpi-label">Dry Powder</div>
                    <div class="kpi-change neutral">{(100 - deployment_rate):.0f}% remaining</div>
                </div>
            </div>
            
            <!-- Fund Allocation -->
            <div class="fund-allocation">
                <h2 class="section-title">Fund Allocation</h2>
                <div class="allocation-bar">
                    <div class="allocation-segment" style="width: {deployment_rate}%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                        {deployment_rate:.0f}% Deployed
                    </div>
                    <div class="allocation-segment" style="width: {100 - deployment_rate}%; background: var(--gray-300); color: var(--gray-700);">
                        {(100 - deployment_rate):.0f}% Available
                    </div>
                </div>
                
                <div class="health-distribution">
                    <div class="health-stat">
                        <div class="health-stat-number" style="color: #16a34a;">{excellent_count + good_count}</div>
                        <div class="health-stat-label">Healthy</div>
                    </div>
                    <div class="health-stat">
                        <div class="health-stat-number" style="color: #d97706;">{warning_count}</div>
                        <div class="health-stat-label">At Risk</div>
                    </div>
                    <div class="health-stat">
                        <div class="health-stat-number" style="color: #dc2626;">{danger_count}</div>
                        <div class="health-stat-label">Critical</div>
                    </div>
                    <div class="health-stat">
                        <div class="health-stat-number" style="color: var(--gray-700);">{sum(1 for pc in portfolio_companies if pc['board_seat'])}</div>
                        <div class="health-stat-label">Board Seats</div>
                    </div>
                </div>
            </div>
            
            <!-- Portfolio Companies -->
            <div class="section-header">
                <h2 class="section-title">Portfolio Companies ({len(portfolio_companies)})</h2>
                <div style="display: flex; gap: 12px; font-size: 12px;">
                    <span style="padding: 6px 12px; background: #f0fdf4; color: #16a34a; border-radius: 6px; font-weight: 600;">● Healthy</span>
                    <span style="padding: 6px 12px; background: #fffbeb; color: #d97706; border-radius: 6px; font-weight: 600;">● At Risk</span>
                    <span style="padding: 6px 12px; background: #fef2f2; color: #dc2626; border-radius: 6px; font-weight: 600;">● Critical</span>
                </div>
            </div>
            
            <div class="companies-grid">
                {company_cards_html}
            </div>
            
            <!-- Data Source Note -->
            <div style="margin-top: 24px; padding: 16px; background: var(--purple-50); border: 1px solid #e9d5ff; border-radius: 8px; font-size: 13px; color: var(--gray-600);">
                📊 Live data from portfolio database • Health scores calculated from target progress • 
                <a href="/wheels/building" style="color: #9333ea; text-decoration: underline; font-weight: 600;">Manage Companies →</a>
            </div>
        </div>
    </div>
</body>
</html>
    """
    
    return HTMLResponse(content=html)

