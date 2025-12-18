"""Help & FAQ Page with Searchable Documentation."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from supabase import create_client
from app.config import settings
from app.api.styles import get_dv_styles
from app.api.sidebar_component import get_admin_sidebar
import json

router = APIRouter(prefix="/help", tags=["Help"])


# Comprehensive FAQ Data
FAQ_DATA = [
    {
        "id": "add-portfolio-company",
        "category": "Portfolio Companies",
        "question": "How do I add a new portfolio company?",
        "answer": """
1. Companies are currently added via script (backend/add_portfolio_companies.py)
2. Future: Click "+ Add Company" button in Settings → Portfolio Companies
3. Fill in: Name, website, industry, founders, ownership %
4. Logos are automatically scraped from the website
5. Company appears in all dashboards immediately
        """,
        "tags": ["portfolio", "company", "add", "new"],
        "difficulty": "medium"
    },
    {
        "id": "connect-pipedrive",
        "category": "Integrations",
        "question": "How do I connect Pipedrive CRM?",
        "answer": """
1. Log into your Pipedrive account
2. Go to Settings → Personal Preferences → API
3. Click "Generate new token"
4. Copy the API token
5. Go to DV Platform: http://localhost:8000/settings
6. Click "Portfolio Companies" tab
7. Find your company
8. Click "Connect" on Pipedrive CRM
9. Paste token and enter domain (e.g., coeo.pipedrive.com)
10. Click "Save Integration"
11. See your deals in the Dealflow board!

📚 Full guide: INTEGRATION_GUIDE_PIPEDRIVE.md
        """,
        "tags": ["pipedrive", "crm", "dealflow", "integration", "connect"],
        "difficulty": "easy"
    },
    {
        "id": "connect-fortnox",
        "category": "Integrations",
        "question": "How do I connect Fortnox for financial data?",
        "answer": """
⚠️ More complex - requires developer account approval (2-3 days)

1. Register at https://developer.fortnox.se
2. Create application: "DV Portfolio Platform"
3. Request scopes: invoice, customer, account, voucher
4. Wait for Fortnox approval (1-2 business days)
5. Get OAuth authorization from Fortnox account user
6. Exchange authorization code for access token
7. Go to Settings → Portfolio Companies
8. Click "Connect" on Fortnox
9. Paste access token and client secret
10. See real financial data in Financial tab!

📚 Full guide: INTEGRATION_GUIDE_FORTNOX.md
        """,
        "tags": ["fortnox", "financial", "accounting", "integration", "oauth"],
        "difficulty": "hard"
    },
    {
        "id": "connect-google-workspace",
        "category": "Integrations",
        "question": "How do I connect Google Workspace?",
        "answer": """
1. Go to https://console.cloud.google.com
2. Create project: "DV Portfolio Platform"
3. Enable APIs: Gmail, Drive, Calendar, People
4. Create OAuth client ID
5. Set redirect URI: http://localhost:8000/integrations/google/callback
6. Copy Client ID and Client Secret
7. (Optional) Create service account for server access
8. Go to Settings → Portfolio Companies
9. Click "Connect" on Google Workspace
10. Paste Client ID, Secret, and (optional) service account email
11. Click "Save Integration"

📚 Full guide: INTEGRATION_GUIDE_GOOGLE_WORKSPACE.md
        """,
        "tags": ["google", "workspace", "gmail", "drive", "calendar"],
        "difficulty": "medium"
    },
    {
        "id": "view-deals",
        "category": "Using the Platform",
        "question": "Where can I see my portfolio company's deals?",
        "answer": """
1. Go to: http://localhost:8000/wheels/building
2. Select your company from dropdown at top
3. Click "Dealflow" tab
4. You'll see deals organized by stage:
   - Lead (not yet contacted)
   - Qualified (initial contact made)
   - Meeting (demo or meeting scheduled)
   - Due Diligence (proposal sent)
   - Proposal (negotiating)
   - Closed Won (deal won!)

Note: Company must have Pipedrive connected first
        """,
        "tags": ["deals", "dealflow", "pipeline", "view", "pipedrive"],
        "difficulty": "easy"
    },
    {
        "id": "view-financials",
        "category": "Using the Platform",
        "question": "Where can I see portfolio company financials?",
        "answer": """
Option 1: Individual Company View
1. Go to: http://localhost:8000/wheels/building
2. Select company from dropdown
3. Click "Financial" tab
4. See: MRR, ARR, investment, valuation

Option 2: Portfolio Overview
1. Go to: http://localhost:8000/wheels/admin
2. See all companies with:
   - Health scores
   - Investment amounts
   - Current valuations
   - Performance indicators

Note: Real-time data requires Fortnox integration
        """,
        "tags": ["financial", "revenue", "metrics", "kpi", "mrr", "arr"],
        "difficulty": "easy"
    },
    {
        "id": "add-team-member",
        "category": "Team Management",
        "question": "How do I add a team member to a portfolio company?",
        "answer": """
Currently:
1. Team members are added via database
2. Founders are added automatically when company is created

Future UI:
1. Go to Building page → Select company → Team tab
2. Click "+ Add Team Member" button
3. Fill in: Name, email, role, LinkedIn
4. Click "Save"
5. Member appears in team grid

For now, contact admin to add team members to database.
        """,
        "tags": ["team", "member", "founder", "people", "add"],
        "difficulty": "medium"
    },
    {
        "id": "company-selector",
        "category": "Using the Platform",
        "question": "How do I switch between portfolio companies?",
        "answer": """
1. Go to Building Companies page: http://localhost:8000/wheels/building
2. Look at top of page
3. You'll see company logo and name with dropdown
4. Click the dropdown
5. Select any company:
   - Disruptive Ventures (Our Company)
   - Crystal Alarm
   - LumberScan
   - Alent Dynamic
   - LunaLEC
   - Vaylo
   - Coeo
   - Basic Safety
   - Service Node
6. All tabs update to show that company's data!

Note: Hard refresh (Cmd+Shift+R) if dropdown doesn't work
        """,
        "tags": ["company", "selector", "switch", "dropdown", "select"],
        "difficulty": "easy"
    },
    {
        "id": "tab-not-working",
        "category": "Troubleshooting",
        "question": "Tabs or company selector not working - what do I do?",
        "answer": """
This is almost always a browser cache issue!

FIX: Hard Refresh
- Mac: Cmd + Shift + R
- Windows: Ctrl + Shift + R
- Or: F12 → Right-click refresh → "Empty Cache and Hard Reload"

Why: Browser cached old JavaScript before new functions were added

After hard refresh:
✅ Tabs should switch (Activities, Dealflow, Financial, Team)
✅ Company selector should work
✅ Logo should update when switching
✅ All data should update per company

Still not working? Open Console (F12) and check for JavaScript errors.

📚 Full guide: TROUBLESHOOTING_BUILDING_PAGE.md
        """,
        "tags": ["troubleshooting", "cache", "tabs", "not working", "broken", "refresh"],
        "difficulty": "easy"
    },
    {
        "id": "q3-data-source",
        "category": "Financial Data",
        "question": "Where does the Q3 2025 financial data come from?",
        "answer": """
Current Status:
- ✅ Manually imported from your Q3 KPI report
- ✅ Real numbers from actual spreadsheet
- ❌ NOT auto-syncing from Google Sheets yet

Data Source:
Your Google Sheet: 
https://docs.google.com/spreadsheets/d/1RbVf3L8LQ1Z96x1NWcyOCssmAw_U5_aHT-m7b9FTqdc/

To enable auto-sync:
1. Make sheet public OR share with service account
2. Connect via Settings → Google Sheets
3. System will auto-update daily

📚 Details: GOOGLE_SHEETS_NOT_YET_SYNCING.md
        """,
        "tags": ["q3", "financial", "data", "google sheets", "kpi", "sync"],
        "difficulty": "medium"
    },
    {
        "id": "health-scores",
        "category": "Portfolio Management",
        "question": "How are company health scores calculated?",
        "answer": """
Health scores (0-100) are calculated from portfolio targets:

Formula:
- Average of all target progress percentages
- Example: If company has 3 targets at 75%, 80%, 85% → Score = 80

Color Coding:
- 🟢 75-100: Excellent/Good (healthy)
- 🟠 40-74: At Risk (warning)
- 🔴 0-39: Critical (urgent attention needed)

Targets tracked:
- Revenue (MRR, ARR growth)
- Customer acquisition
- Product development milestones
- Cash runway

View on: http://localhost:8000/wheels/admin
        """,
        "tags": ["health", "score", "metrics", "targets", "kpi", "performance"],
        "difficulty": "easy"
    },
    {
        "id": "add-api-key",
        "category": "Settings",
        "question": "How do I add an API key for a portfolio company?",
        "answer": """
1. Go to: http://localhost:8000/settings
2. Click "Portfolio Companies (8)" tab
3. Find the company you want to configure
4. You'll see 6 integration options:
   - Pipedrive CRM
   - Fortnox
   - Google Sheets
   - Google Workspace
   - Office 365
   - Custom Integration
5. Click "Connect" on the one you want
6. Modal opens with appropriate fields
7. Fill in credentials (see specific integration guides)
8. Click "Save Integration"
9. Credentials encrypted and stored
10. Status changes to "✅ Connected"

Each company can have different credentials!
        """,
        "tags": ["api", "key", "settings", "integration", "connect", "configure"],
        "difficulty": "easy"
    },
    {
        "id": "dark-mode",
        "category": "Using the Platform",
        "question": "How do I enable dark mode?",
        "answer": """
Dark mode automatically follows your system preferences!

To toggle:
- Mac: System Preferences → General → Appearance → Dark
- Windows: Settings → Personalization → Colors → Dark

Or use the dark mode toggle (if available in UI)

All pages support dark mode:
✅ Building Companies
✅ Portfolio Overview  
✅ Settings
✅ Dealflow Companies

Colors automatically adjust for optimal contrast.
        """,
        "tags": ["dark mode", "theme", "appearance", "ui"],
        "difficulty": "easy"
    },
    {
        "id": "deal-stages",
        "category": "Dealflow",
        "question": "What do the different deal stages mean?",
        "answer": """
The 6 standard dealflow stages:

1. **Lead** (Early)
   - Not yet contacted
   - Initial research phase
   - Prospecting

2. **Qualified** (Contact Made)
   - First contact established
   - Interest confirmed
   - Qualified as potential customer

3. **Meeting** (Demo/Discussion)
   - Demo scheduled or completed
   - Active discussions
   - Solution presentation

4. **Due Diligence** (Proposal)
   - Proposal or quote sent
   - Under review
   - Evaluating options

5. **Proposal** (Negotiation)
   - Negotiating terms
   - Finalizing details
   - Almost there!

6. **Closed Won** (Success!)
   - Deal signed
   - Customer acquired
   - Revenue secured

Deals from Pipedrive are automatically mapped to these stages.
        """,
        "tags": ["dealflow", "stages", "pipeline", "sales", "process"],
        "difficulty": "easy"
    },
    {
        "id": "portfolio-overview",
        "category": "Using the Platform",
        "question": "What's on the Portfolio Overview dashboard?",
        "answer": """
URL: http://localhost:8000/wheels/admin

The "helicopter view" showing:

Top Metrics:
- Active companies count
- Total invested (fund level)
- Portfolio valuation
- Portfolio multiple (TVPI)
- Dry powder remaining

Fund Allocation Bar:
- Visual showing deployed vs available capital
- Health distribution (healthy/at-risk/critical)

Company Cards:
- All 8 portfolio companies
- Health scores (0-100)
- Investment amounts
- Current valuations
- Performance multiples
- Target counts

Companies are sorted by health score (best first!)
        """,
        "tags": ["portfolio", "overview", "dashboard", "admin", "metrics", "fund"],
        "difficulty": "easy"
    },
    {
        "id": "page-urls",
        "category": "Navigation",
        "question": "What are all the page URLs?",
        "answer": """
Main Pages:

📊 Building Companies (Company Management)
http://localhost:8000/wheels/building
- Select company, view 4 tabs: Activities | Dealflow | Financial | Team

📈 Portfolio Overview (Fund Dashboard)  
http://localhost:8000/wheels/admin
- Helicopter view, all companies, health scores

🏢 Dealflow Companies (Company Directory)
http://localhost:8000/wheels/dealflow/companies
- All companies with logos, founders, badges

⚙️ Settings (Configuration)
http://localhost:8000/settings
- 3 tabs: General | API Keys | Portfolio Companies (8)

❓ Help & FAQ (This Page)
http://localhost:8000/help
- Searchable documentation and guides

Other Pages:
- People Wheel: http://localhost:8000/wheels/people
- Dealflow Wheel: http://localhost:8000/wheels/dealflow
- Upload Files: http://localhost:8000/upload-ui
        """,
        "tags": ["urls", "pages", "navigation", "links", "where"],
        "difficulty": "easy"
    },
    {
        "id": "team-tab",
        "category": "Team Management",
        "question": "What's on the Team tab?",
        "answer": """
The Team tab shows team members for the selected company:

What You'll See:
- Founder profiles with photos/initials
- Name, job title, role
- Email and LinkedIn buttons
- "Founder" badge for co-founders
- Company-specific team members

Data Source:
- Pulled from database (people table)
- Founders added when company created
- Updates when you switch companies

Location:
http://localhost:8000/wheels/building → Team tab

Future Features:
- Add team members via UI
- Edit roles and information
- Upload profile photos
- Skills and competencies
        """,
        "tags": ["team", "members", "founders", "people", "profiles"],
        "difficulty": "easy"
    },
    {
        "id": "encryption",
        "category": "Security",
        "question": "How are API keys and credentials stored securely?",
        "answer": """
All credentials are encrypted using Fernet (symmetric encryption):

Storage:
- API tokens encrypted before database insert
- Client secrets encrypted
- Refresh tokens encrypted
- Encryption key from ENCRYPTION_KEY environment variable

In Database:
- Stored in portfolio_company_integrations table
- api_token_encrypted, client_secret_encrypted columns
- Per-company isolation (no sharing)

Usage:
- Decrypted only when making API calls
- Never logged
- Never sent to frontend
- Never exposed in API responses

Security Features:
✅ Fernet encryption (cryptography library)
✅ 32-byte encryption key
✅ Encrypted at rest
✅ Per-company credentials
✅ Audit trail (who configured, when)
        """,
        "tags": ["security", "encryption", "api keys", "credentials", "safe"],
        "difficulty": "medium"
    },
    {
        "id": "no-deals-showing",
        "category": "Troubleshooting",
        "question": "I connected Pipedrive but no deals are showing - why?",
        "answer": """
Common causes and fixes:

1. **Browser Cache Issue**
   Fix: Hard refresh (Cmd+Shift+R or Ctrl+Shift+R)

2. **Wrong Company Selected**
   Fix: Make sure correct company is selected in dropdown

3. **Negative Stages Only**
   If all deals are in "Nej tack" or "Inte nu" stages, they're filtered out
   Fix: Check your Pipedrive for open opportunities

4. **API Token Invalid**
   Fix: Go to Settings → Portfolio Companies → Reconfigure with fresh token

5. **Company Domain Wrong**
   Fix: Verify domain matches Pipedrive URL exactly

Check server logs:
tail -50 /tmp/uvicorn_pipedrive.log | grep "Pipedrive"

Should see: "✅ Fetched X deals from Pipedrive"
        """,
        "tags": ["troubleshooting", "deals", "not showing", "empty", "pipedrive"],
        "difficulty": "medium"
    },
    {
        "id": "financial-metrics",
        "category": "Financial Data",
        "question": "What financial metrics can I track?",
        "answer": """
Per Portfolio Company:

Revenue Metrics:
- MRR (Monthly Recurring Revenue)
- ARR (Annual Recurring Revenue)
- Revenue growth % (YoY, MoM)
- Q3 2025 actuals

Investment Metrics:
- Amount invested by DV
- Current valuation (6x ARR multiple)
- Investment multiple (MOIC)
- Ownership percentage

Financial Health:
- Cash position / runway
- Burn rate (monthly)
- Profitability (Q3 actual)
- Employee count

Fund Level:
- Total deployed capital
- Portfolio valuation
- Portfolio multiple (TVPI)
- Dry powder remaining
- Deployment rate %

Data Sources:
- Q3 2025 KPI report (imported)
- Fortnox API (when connected)
- Google Sheets (when connected)
        """,
        "tags": ["financial", "metrics", "revenue", "mrr", "arr", "kpi", "valuation"],
        "difficulty": "easy"
    },
    {
        "id": "who-can-see",
        "category": "Access Control",
        "question": "Who can see portfolio company data?",
        "answer": """
Current Access Model:

Everyone with platform access can see:
✅ All portfolio companies
✅ All financial metrics
✅ All deals and activities
✅ All settings

Future Access Control (Planned):
- Founders: See only their company
- Partners: See all companies they're involved in
- Admins: See everything
- LPs: Limited read-only view

Security Note:
- All API credentials encrypted
- Access tokens not exposed to users
- Audit trail of configuration changes

For production deployment, implement:
- Role-based access control (RBAC)
- Row-level security (RLS) policies
- Per-company data isolation
        """,
        "tags": ["access", "permissions", "security", "who", "see", "view"],
        "difficulty": "medium"
    },
    {
        "id": "update-financial-data",
        "category": "Financial Data",
        "question": "How do I update Q3 financial data to Q4?",
        "answer": """
Option 1: Google Sheets Auto-Sync (Recommended)
1. Update your KPI spreadsheet with Q4 data
2. Connect Google Sheets integration
3. Click "Sync Now" or wait for scheduled sync
4. Data automatically updates in platform

Option 2: Manual Update (Current)
1. Update Q4 data in spreadsheet
2. Copy new numbers
3. Run: python update_financial_data_from_q4.py
4. Script updates database
5. Refresh Building page to see new data

Option 3: Fortnox Integration (Most Accurate)
1. Connect Fortnox for each company
2. Real-time revenue data from actual invoices
3. Automatic MRR/ARR calculations
4. No manual updates needed!

Future: One-click "Sync All Companies" button
        """,
        "tags": ["update", "financial", "data", "q4", "sync", "refresh"],
        "difficulty": "medium"
    },
    {
        "id": "what-is-building",
        "category": "Using the Platform",
        "question": "What is the 'Building Companies' page?",
        "answer": """
The Building Companies page is your command center for managing portfolio companies.

Features:

Company Selector:
- Switch between DV and 8 portfolio companies
- Logo and name displayed
- Dropdown to select

4 Tabs:

1. **Activities**
   - Linear tasks and to-dos
   - Kanban board (Backlog → Done)
   - Company-specific activities (future)

2. **Dealflow**
   - Sales pipeline from Pipedrive
   - 6-stage kanban (Lead → Closed Won)
   - Real customer deals
   - Example: Coeo's 193 deals

3. **Financial**
   - Q3 2025 financial metrics
   - MRR, ARR, valuation
   - Investment details
   - Company-specific numbers

4. **Team**
   - Founders and team members
   - Contact information (email, LinkedIn)
   - Roles and titles
   - Company-specific profiles

URL: http://localhost:8000/wheels/building
        """,
        "tags": ["building", "companies", "page", "what is", "overview"],
        "difficulty": "easy"
    },
    {
        "id": "integration-types",
        "category": "Integrations",
        "question": "What integration types are available?",
        "answer": """
6 integration types, each company can have all:

1. **Pipedrive CRM** ⭐ Easy
   - Sales pipeline
   - Deal tracking
   - Setup: 5 minutes

2. **Fortnox** ⭐⭐⭐ Complex
   - Financial data
   - Invoices and expenses
   - Setup: 2-3 days (requires approval)

3. **Google Sheets** ⭐⭐ Moderate
   - KPI reports
   - Data import
   - Setup: 15 minutes

4. **Google Workspace** ⭐⭐ Moderate
   - Gmail, Drive, Calendar
   - Full Google suite
   - Setup: 20 minutes

5. **Office 365** ⭐⭐ Moderate
   - Outlook, OneDrive, Teams
   - Microsoft suite
   - Setup: 20 minutes

6. **Custom Integration** ⭐⭐ Moderate
   - Any API endpoint
   - Flexible configuration
   - Setup: Varies

Each has step-by-step guides!
        """,
        "tags": ["integrations", "types", "available", "what", "connect"],
        "difficulty": "easy"
    },
    {
        "id": "office365-guide",
        "category": "Integrations",
        "question": "How do I connect Office 365?",
        "answer": """
Quick Guide (Full guide coming soon):

1. Go to https://portal.azure.com
2. Azure Active Directory → App registrations
3. New registration: "DV Portfolio Platform"
4. Redirect URI: http://localhost:8000/integrations/microsoft/callback
5. API Permissions: Add Mail, Calendar, Files, Contacts
6. Certificates & secrets → New client secret
7. Copy: Tenant ID, Application ID, Client Secret
8. Go to Settings → Portfolio Companies
9. Click "Connect" on Office 365
10. Paste: Tenant ID, Client ID, Secret
11. Save Integration

Full guide: INTEGRATION_GUIDE_OFFICE365.md (coming soon)
        """,
        "tags": ["office365", "microsoft", "outlook", "teams", "integration"],
        "difficulty": "medium"
    },
    {
        "id": "custom-integration",
        "category": "Integrations",
        "question": "How do I add a custom integration?",
        "answer": """
For connecting any API not listed:

1. Go to Settings → Portfolio Companies
2. Find your company
3. Click "Connect" on "Custom Integration"

Fill in:
- **Integration Name**: Give it a name (e.g., "Internal CRM")
- **API Endpoint URL**: Base URL (e.g., https://api.example.com/v1)
- **API Token**: Your authentication token
- **Additional Headers**: Any custom headers as JSON

Examples:
- HubSpot
- Salesforce
- QuickBooks
- Xero
- Stripe
- Custom internal tools
- Legacy systems

The platform stores credentials encrypted.
You'll need to implement the actual API calls in code.
        """,
        "tags": ["custom", "integration", "api", "connect", "other"],
        "difficulty": "hard"
    },
    {
        "id": "coeo-example",
        "category": "Examples",
        "question": "Show me an example of a working integration",
        "answer": """
**Coeo's Pipedrive Integration** (Currently Live!)

Setup Time: 5 minutes
Status: ✅ Connected

What's Working:
- 193 deals pulled from Coeo's Pipedrive
- 2.77M SEK total pipeline value
- Deals organized by stage
- Real customer names and organizations
- Live data refreshing on page load

How to See It:
1. Go to: http://localhost:8000/wheels/building
2. Select "Coeo" from dropdown
3. Click "Dealflow" tab
4. Scroll through 193 real deals!

Examples of deals:
- Skolkuratorsdagen 5/10 2026 (350,000 SEK)
- Grönytesektionen Sverige affär (20,000 SEK)
- Landsbygdsriksdagen 29-31 maj 2026 (35,000 SEK)
- And 190 more...

This proves the system works!
        """,
        "tags": ["example", "coeo", "working", "demo", "proof"],
        "difficulty": "easy"
    }
]


@router.get("", response_class=HTMLResponse)
async def help_page():
    """Help & FAQ page with searchable documentation."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        people = supabase.table('people').select('*').execute().data
        current_user = next((p for p in people if 'marcus' in p.get('name', '').lower() or 'markus' in p.get('name', '').lower()), None)
        if not current_user:
            current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
    
    except Exception as e:
        current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
    
    # Build FAQ items HTML
    faq_items_html = ""
    for faq in FAQ_DATA:
        difficulty_badge = {
            'easy': '<span style="padding: 3px 8px; background: #f0fdf4; color: #16a34a; border-radius: 4px; font-size: 10px; font-weight: 600;">EASY</span>',
            'medium': '<span style="padding: 3px 8px; background: #fffbeb; color: #d97706; border-radius: 4px; font-size: 10px; font-weight: 600;">MODERATE</span>',
            'hard': '<span style="padding: 3px 8px; background: #fef2f2; color: #dc2626; border-radius: 4px; font-size: 10px; font-weight: 600;">COMPLEX</span>',
        }.get(faq.get('difficulty', 'easy'), '')
        
        faq_items_html += f"""
        <div class="faq-item" data-category="{faq['category']}" data-tags="{' '.join(faq['tags'])}">
            <div class="faq-header" onclick="toggleFaq('{faq['id']}')">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                        <span class="faq-category">{faq['category']}</span>
                        {difficulty_badge}
                    </div>
                    <h3 class="faq-question">{faq['question']}</h3>
                </div>
                <svg class="faq-icon" id="icon-{faq['id']}" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
            </div>
            <div class="faq-answer" id="answer-{faq['id']}" style="display: none;">
                <pre style="white-space: pre-wrap; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif; font-size: 14px; line-height: 1.6; color: var(--gray-700); margin: 0;">{faq['answer'].strip()}</pre>
            </div>
        </div>
        """
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Help & FAQ - DV Platform</title>
    {get_dv_styles()}
    <style>
        .search-container {{
            max-width: 800px;
            margin: 0 auto 32px;
        }}
        
        .search-box {{
            position: relative;
        }}
        
        .search-input {{
            width: 100%;
            padding: 16px 50px 16px 20px;
            font-size: 16px;
            border: 2px solid var(--gray-300);
            border-radius: 12px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
            transition: all 0.2s;
        }}
        
        .search-input:focus {{
            outline: none;
            border-color: var(--gray-900);
            box-shadow: 0 0 0 4px rgba(0,0,0,0.05);
        }}
        
        .search-icon {{
            position: absolute;
            right: 18px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--gray-400);
        }}
        
        .search-results {{
            margin-top: 12px;
            font-size: 13px;
            color: var(--gray-600);
        }}
        
        .category-filters {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-bottom: 24px;
            justify-content: center;
        }}
        
        .category-btn {{
            padding: 8px 16px;
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
            color: var(--gray-700);
            cursor: pointer;
            transition: all 0.15s;
        }}
        
        .category-btn:hover {{
            background: var(--gray-100);
            border-color: var(--gray-300);
        }}
        
        .category-btn.active {{
            background: var(--gray-900);
            color: white;
            border-color: var(--gray-900);
        }}
        
        .faq-list {{
            max-width: 900px;
            margin: 0 auto;
        }}
        
        .faq-item {{
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 12px;
            margin-bottom: 16px;
            overflow: hidden;
            transition: all 0.2s;
        }}
        
        .faq-item:hover {{
            border-color: var(--gray-300);
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        
        .faq-header {{
            padding: 20px;
            cursor: pointer;
            display: flex;
            align-items: flex-start;
            gap: 16px;
        }}
        
        .faq-category {{
            font-size: 11px;
            font-weight: 600;
            color: var(--purple-600);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .faq-question {{
            font-size: 16px;
            font-weight: 600;
            color: var(--gray-900);
            margin: 0;
        }}
        
        .faq-icon {{
            flex-shrink: 0;
            transition: transform 0.2s;
        }}
        
        .faq-icon.rotated {{
            transform: rotate(180deg);
        }}
        
        .faq-answer {{
            padding: 0 20px 20px 20px;
            border-top: 1px solid var(--gray-200);
            background: var(--gray-50);
        }}
        
        .faq-item.hidden {{
            display: none;
        }}
        
        .quick-links {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
        }}
        
        .quick-link {{
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 8px;
            padding: 16px;
            text-align: center;
            transition: all 0.15s;
            text-decoration: none;
            display: block;
        }}
        
        .quick-link:hover {{
            border-color: var(--purple-600);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}
        
        .quick-link-title {{
            font-size: 14px;
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 4px;
        }}
        
        .quick-link-desc {{
            font-size: 12px;
            color: var(--gray-600);
        }}
        
        body.dark-mode .search-input,
        body.dark-mode .faq-item,
        body.dark-mode .category-btn,
        body.dark-mode .quick-link {{
            background: #2a2a2a;
            border-color: #404040;
            color: #e5e5e5;
        }}
        
        body.dark-mode .faq-answer {{
            background: #1a1a1a;
        }}
        
        body.dark-mode .faq-question,
        body.dark-mode .quick-link-title {{
            color: #e5e5e5;
        }}
        
        body.dark-mode .category-btn.active {{
            background: #e5e5e5;
            color: #1a1a1a;
        }}
    </style>
</head>
<body>
    {get_admin_sidebar('help', current_user.get('name', 'Admin User'), current_user.get('email', ''), current_user.get('linkedin_url', ''))}
    
    <div class="main-content">
        <div class="page-header">
            <div class="page-header-left">
                <h1 class="page-title">Help & Documentation</h1>
                <p class="page-description">Searchable guides and frequently asked questions</p>
            </div>
        </div>
        
        <div class="container">
            <!-- Search Bar -->
            <div class="search-container">
                <div class="search-box">
                    <input 
                        type="text" 
                        id="search-input" 
                        class="search-input" 
                        placeholder="Search for help... (e.g., 'how to connect pipedrive')"
                        oninput="searchFAQ(this.value)"
                        autofocus
                    >
                    <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="11" cy="11" r="8"></circle>
                        <path d="m21 21-4.35-4.35"></path>
                    </svg>
                </div>
                <div id="search-results" class="search-results"></div>
            </div>
            
            <!-- Quick Links -->
            <div class="quick-links">
                <a href="#" onclick="scrollToFaq('connect-pipedrive'); return false;" class="quick-link">
                    <div class="quick-link-title">Connect Pipedrive</div>
                    <div class="quick-link-desc">5 min setup</div>
                </a>
                <a href="#" onclick="scrollToFaq('connect-fortnox'); return false;" class="quick-link">
                    <div class="quick-link-title">Connect Fortnox</div>
                    <div class="quick-link-desc">2-3 days</div>
                </a>
                <a href="#" onclick="scrollToFaq('add-api-key'); return false;" class="quick-link">
                    <div class="quick-link-title">Add API Key</div>
                    <div class="quick-link-desc">Quick start</div>
                </a>
                <a href="#" onclick="scrollToFaq('view-deals'); return false;" class="quick-link">
                    <div class="quick-link-title">View Deals</div>
                    <div class="quick-link-desc">Find dealflow</div>
                </a>
            </div>
            
            <!-- Category Filters -->
            <div class="category-filters">
                <button class="category-btn active" onclick="filterByCategory('all')">All</button>
                <button class="category-btn" onclick="filterByCategory('Using the Platform')">Using the Platform</button>
                <button class="category-btn" onclick="filterByCategory('Integrations')">Integrations</button>
                <button class="category-btn" onclick="filterByCategory('Portfolio Companies')">Portfolio Companies</button>
                <button class="category-btn" onclick="filterByCategory('Troubleshooting')">Troubleshooting</button>
                <button class="category-btn" onclick="filterByCategory('Security')">Security</button>
            </div>
            
            <!-- FAQ List -->
            <div class="faq-list" id="faq-list">
                {faq_items_html}
            </div>
            
            <!-- No Results Message -->
            <div id="no-results" style="display: none; text-align: center; padding: 40px; color: var(--gray-500);">
                <p style="font-size: 16px; margin-bottom: 8px;">No results found</p>
                <p style="font-size: 13px;">Try different keywords or browse by category</p>
            </div>
        </div>
    </div>
    
    <script>
        const faqData = {json.dumps(FAQ_DATA)};
        let currentCategory = 'all';
        
        function toggleFaq(faqId) {{
            const answer = document.getElementById(`answer-${{faqId}}`);
            const icon = document.getElementById(`icon-${{faqId}}`);
            
            if (answer.style.display === 'none') {{
                answer.style.display = 'block';
                icon.classList.add('rotated');
            }} else {{
                answer.style.display = 'none';
                icon.classList.remove('rotated');
            }}
        }}
        
        function scrollToFaq(faqId) {{
            const element = document.querySelector(`[data-tags*="${{faqId}}"]`);
            if (element) {{
                element.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                element.style.background = '#faf5ff';
                setTimeout(() => {{
                    element.style.background = 'white';
                }}, 2000);
                
                // Open it
                const answer = document.getElementById(`answer-${{faqId}}`);
                const icon = document.getElementById(`icon-${{faqId}}`);
                if (answer) {{
                    answer.style.display = 'block';
                    icon.classList.add('rotated');
                }}
            }}
        }}
        
        function searchFAQ(query) {{
            const searchLower = query.toLowerCase().trim();
            const faqItems = document.querySelectorAll('.faq-item');
            const noResults = document.getElementById('no-results');
            let visibleCount = 0;
            
            if (!searchLower) {{
                // Show all in current category
                faqItems.forEach(item => {{
                    if (currentCategory === 'all' || item.dataset.category === currentCategory) {{
                        item.classList.remove('hidden');
                        visibleCount++;
                    }}
                }});
                noResults.style.display = 'none';
                document.getElementById('search-results').textContent = '';
                return;
            }}
            
            faqItems.forEach(item => {{
                const question = item.querySelector('.faq-question').textContent.toLowerCase();
                const tags = item.dataset.tags.toLowerCase();
                const category = item.dataset.category.toLowerCase();
                
                const matches = question.includes(searchLower) || 
                               tags.includes(searchLower) || 
                               category.includes(searchLower);
                
                if (matches) {{
                    item.classList.remove('hidden');
                    visibleCount++;
                }} else {{
                    item.classList.add('hidden');
                }}
            }});
            
            // Update results count
            const resultsText = document.getElementById('search-results');
            if (visibleCount > 0) {{
                resultsText.textContent = `Found ${{visibleCount}} result${{visibleCount !== 1 ? 's' : ''}}`;
                noResults.style.display = 'none';
            }} else {{
                resultsText.textContent = '';
                noResults.style.display = 'block';
            }}
        }}
        
        function filterByCategory(category) {{
            currentCategory = category;
            
            // Update button states
            document.querySelectorAll('.category-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');
            
            // Filter FAQs
            const faqItems = document.querySelectorAll('.faq-item');
            const noResults = document.getElementById('no-results');
            let visibleCount = 0;
            
            faqItems.forEach(item => {{
                if (category === 'all' || item.dataset.category === category) {{
                    item.classList.remove('hidden');
                    visibleCount++;
                }} else {{
                    item.classList.add('hidden');
                }}
            }});
            
            noResults.style.display = visibleCount === 0 ? 'block' : 'none';
            
            // Clear search
            document.getElementById('search-input').value = '';
            document.getElementById('search-results').textContent = '';
        }}
        
        // Keyboard shortcut: / to focus search
        document.addEventListener('keydown', (e) => {{
            if (e.key === '/' && !e.target.matches('input, textarea')) {{
                e.preventDefault();
                document.getElementById('search-input').focus();
            }}
        }});
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html)


@router.get("/search")
async def search_help(q: str):
    """API endpoint for searching FAQ."""
    
    query_lower = q.lower()
    results = []
    
    for faq in FAQ_DATA:
        # Search in question, tags, and category
        if (query_lower in faq['question'].lower() or
            any(query_lower in tag for tag in faq['tags']) or
            query_lower in faq['category'].lower()):
            results.append({
                'id': faq['id'],
                'question': faq['question'],
                'category': faq['category'],
                'difficulty': faq['difficulty']
            })
    
    return JSONResponse(content={"results": results, "count": len(results)})

