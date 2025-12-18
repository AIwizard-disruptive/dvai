"""Deal Flow Wheel - Investment Pipeline & Opportunities."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from supabase import create_client
from app.config import settings
from app.api.styles import get_dv_styles
from app.api.sidebar_component import get_admin_sidebar
from app.services.company_enrichment import enrich_companies_from_people

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


@router.get("/dealflow/companies", response_class=HTMLResponse)
async def dealflow_companies():
    """Deal Flow - Companies page with email domain extraction and logos."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get current user
        people = supabase.table('people').select('*').execute().data
        current_user = next((p for p in people if 'marcus' in p.get('name', '').lower() or 'markus' in p.get('name', '').lower()), None)
        if not current_user:
            current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        
        # Get portfolio companies from database
        portfolio_result = supabase.table('portfolio_companies') \
            .select('*, organizations(*)') \
            .eq('status', 'active') \
            .execute()
        
        # Extract companies from all people's email addresses
        companies = await enrich_companies_from_people(people)
        
        # Add portfolio companies to the list
        for pc in portfolio_result.data:
            org = pc.get('organizations', {})
            domain = org.get('domain', '')
            
            if domain and domain not in companies:
                # Get founders for this company
                founders = supabase.table('people') \
                    .select('*') \
                    .eq('primary_organization_id', org.get('id')) \
                    .execute().data
                
                companies[domain] = {
                    'name': org.get('name', 'Unknown'),
                    'domain': domain,
                    'website': org.get('website_url', f"https://{domain}"),
                    'logo_url': org.get('logo_url', f"https://logo.clearbit.com/{domain}"),
                    'employee_count': len(founders),
                    'employees': [{'name': f.get('name'), 'email': f.get('email')} for f in founders],
                    'is_portfolio': True,
                }
        
        # Sort companies: portfolio companies first, then by employee count
        sorted_companies = sorted(
            companies.values(), 
            key=lambda x: (not x.get('is_portfolio', False), -x['employee_count'])
        )
        
    except Exception as e:
        current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        sorted_companies = []
        print(f"Error: {e}")
    
    # Generate company cards HTML
    company_cards_html = ""
    for company in sorted_companies:
        employees_html = ""
        for emp in company['employees'][:5]:  # Show first 5 employees
            initials = ''.join(word[0] for word in emp['name'].split()[:2]) if emp['name'] else '??'
            employees_html += f"""
                <div class="employee-badge" title="{emp['name']} ({emp['email']})">
                    {initials}
                </div>
            """
        
        if company['employee_count'] > 5:
            employees_html += f"""
                <div class="employee-badge more">
                    +{company['employee_count'] - 5}
                </div>
            """
        
        portfolio_badge = ""
        if company.get('is_portfolio'):
            portfolio_badge = '<span class="portfolio-badge" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Portfolio Company</span>'
        
        company_cards_html += f"""
            <div class="company-card">
                <div class="company-logo-container">
                    <img src="{company['logo_url']}" 
                         alt="{company['name']}" 
                         class="company-logo"
                         onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                    <div class="company-logo-fallback" style="display: none;">
                        {company['name'][0].upper()}
                    </div>
                </div>
                <div class="company-info">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                        <h3 class="company-name" style="margin: 0;">{company['name']}</h3>
                        {portfolio_badge}
                    </div>
                    <p class="company-domain">{company['domain']}</p>
                    <div class="company-stats">
                        <span class="stat-badge">👥 {company['employee_count']} contact{'' if company['employee_count'] == 1 else 's'}</span>
                    </div>
                    <div class="employees-row">
                        {employees_html}
                    </div>
                </div>
                <div class="company-actions">
                    <a href="{company['website']}" target="_blank" class="btn-secondary btn-sm">
                        Visit Website →
                    </a>
                </div>
            </div>
        """
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Companies - Deal Flow</title>
    {get_dv_styles()}
    <style>
        .companies-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
            margin-top: 24px;
        }}
        
        .company-card {{
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 8px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            transition: all 0.2s;
        }}
        
        .company-card:hover {{
            border-color: var(--gray-300);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        
        .company-logo-container {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 80px;
            height: 80px;
            background: var(--gray-50);
            border: 1px solid var(--gray-200);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .company-logo {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            padding: 12px;
        }}
        
        .company-logo-fallback {{
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            font-weight: 700;
            color: var(--gray-500);
            background: linear-gradient(135deg, var(--gray-100) 0%, var(--gray-50) 100%);
        }}
        
        .company-info {{
            flex: 1;
        }}
        
        .company-name {{
            font-size: 18px;
            font-weight: 600;
            color: var(--gray-900);
            margin: 0 0 4px 0;
        }}
        
        .company-domain {{
            font-size: 13px;
            color: var(--gray-500);
            margin: 0 0 12px 0;
        }}
        
        .company-stats {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-bottom: 12px;
        }}
        
        .stat-badge {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 12px;
            padding: 4px 10px;
            background: var(--gray-100);
            color: var(--gray-700);
            border-radius: 12px;
            font-weight: 500;
        }}
        
        .employees-row {{
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }}
        
        .employee-badge {{
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: 600;
            cursor: help;
        }}
        
        .employee-badge.more {{
            background: var(--gray-200);
            color: var(--gray-700);
        }}
        
        .company-actions {{
            display: flex;
            gap: 8px;
        }}
        
        .btn-sm {{
            padding: 6px 12px;
            font-size: 13px;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 48px 24px;
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 8px;
        }}
        
        .empty-state h3 {{
            font-size: 16px;
            font-weight: 600;
            color: var(--gray-900);
            margin: 0 0 8px 0;
        }}
        
        .empty-state p {{
            font-size: 14px;
            color: var(--gray-600);
            margin: 0;
        }}
    </style>
</head>
<body>
    {get_admin_sidebar('companies', current_user.get('name', 'Admin User'), current_user.get('email', ''), current_user.get('linkedin_url', ''))}
    
    <div class="main-content">
        <div class="page-header">
            <div class="page-header-left">
                <h1 class="page-title">Companies</h1>
                <p class="page-description">Automatically extracted from email domains</p>
            </div>
        </div>
        
        <div class="container">
            <div class="dashboard-stats">
                <div class="stat-card">
                    <div class="stat-number">{len(sorted_companies)}</div>
                    <div class="stat-label">Companies Found</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{sum(c['employee_count'] for c in sorted_companies)}</div>
                    <div class="stat-label">Total Contacts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len([c for c in sorted_companies if c['employee_count'] > 1])}</div>
                    <div class="stat-label">Multi-Contact Orgs</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len([c for c in sorted_companies if c['employee_count'] == 1])}</div>
                    <div class="stat-label">Single Contact</div>
                </div>
            </div>
            
            {'<div class="companies-grid">' + company_cards_html + '</div>' if sorted_companies else '''
            <div class="empty-state">
                <h3>No Companies Found</h3>
                <p>Add people with business email addresses to see companies here.</p>
            </div>
            '''}
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



