"""People & Network Wheel - HR, Culture, Documents."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from supabase import create_client
from app.config import settings
from app.api.styles import get_dv_styles
from app.api.sidebar_component import get_admin_sidebar

router = APIRouter(prefix="/wheels", tags=["Wheels - People"])


@router.get("/people", response_class=HTMLResponse)
async def people_wheel():
    """People & Network wheel - Display all employees and contacts."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get all people
        all_people = supabase.table('people').select('*').order('name').execute().data
        
        # Get current user - Marcus Löwegren
        current_user = next((p for p in all_people if 'marcus' in p.get('name', '').lower() or 'markus' in p.get('name', '').lower()), None)
        if not current_user:
            current_user = {'name': 'Marcus Löwegren', 'email': 'marcus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        
        # Categorize people - Employees first
        categories = {
            'Disruptive Ventures Team': [],
            'Partners & Advisors': [],
            'Portfolio Founders': [],
            'Investors': [],
            'Other Contacts': []
        }
        
        for person in all_people:
            person_type = person.get('person_type', 'contact')
            name = person.get('name', 'Unknown')
            email = person.get('email', '').lower()
            job_title = person.get('job_title', '').lower()
            
            # Skip if no name
            if not name or name == 'Unknown':
                continue
            
            # Categorize based on type or email domain - Prioritize DV employees
            if person_type == 'internal' or 'disruptiveventures' in email or '@dv.' in email:
                categories['Disruptive Ventures Team'].append(person)
            elif person_type == 'advisor' or 'advisor' in job_title or 'partner' in job_title:
                categories['Partners & Advisors'].append(person)
            elif person_type == 'founder' or 'founder' in job_title or 'ceo' in job_title or 'cto' in job_title:
                categories['Portfolio Founders'].append(person)
            elif person_type == 'investor' or 'investor' in job_title or 'vc' in job_title:
                categories['Investors'].append(person)
            else:
                categories['Other Contacts'].append(person)
        
    except Exception as e:
        all_people = []
        categories = {'Disruptive Ventures Team': [], 'Partners & Advisors': [], 'Portfolio Founders': [], 'Investors': [], 'Other Contacts': []}
        current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        print(f"Error: {e}")
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>People & Network - Admin</title>
    {get_dv_styles()}
    <style>
        .category-section {{
            margin-bottom: 32px;
        }}
        
        .category-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
            padding: 12px 0;
            border-bottom: 1px solid var(--gray-200);
            cursor: pointer;
            user-select: none;
        }}
        
        .category-header:hover {{
            color: var(--gray-900);
        }}
        
        .category-icon {{
            width: 20px;
            height: 20px;
            color: var(--gray-600);
        }}
        
        .category-title {{
            font-size: 16px;
            font-weight: 600;
            color: var(--gray-900);
            flex: 1;
        }}
        
        .category-count {{
            font-size: 12px;
            color: var(--gray-500);
            background: var(--gray-100);
            padding: 2px 8px;
            border-radius: 4px;
        }}
        
        .category-content {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 12px;
        }}
        
        .category-content.collapsed {{
            display: none;
        }}
        
        .doc-card {{
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 8px;
            padding: 16px;
            transition: all 0.15s;
            text-decoration: none;
            display: block;
            color: inherit;
        }}
        
        .doc-card:hover {{
            border-color: var(--gray-300);
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .doc-icon {{
            width: 32px;
            height: 32px;
            background: var(--gray-100);
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 12px;
        }}
        
        .doc-icon svg {{
            width: 18px;
            height: 18px;
            stroke: var(--gray-600);
        }}
        
        .doc-title {{
            font-size: 14px;
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 4px;
        }}
        
        .doc-meta {{
            font-size: 12px;
            color: var(--gray-500);
            margin-top: 8px;
        }}
        
        /* Person Cards Styles */
        .person-card {{
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 8px;
            padding: 16px;
            transition: all 0.15s;
        }}
        
        .person-card:hover {{
            border-color: var(--gray-300);
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        
        .person-avatar {{
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 12px;
            font-size: 18px;
            font-weight: 600;
            color: white;
        }}
        
        .person-name {{
            font-size: 15px;
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 4px;
        }}
        
        .person-title {{
            font-size: 13px;
            color: var(--gray-600);
            margin-bottom: 8px;
        }}
        
        .person-email {{
            font-size: 12px;
            color: var(--gray-500);
            margin-bottom: 8px;
            word-break: break-word;
        }}
        
        .person-actions {{
            display: flex;
            gap: 8px;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid var(--gray-100);
        }}
        
        .person-action-btn {{
            flex: 1;
            padding: 6px 12px;
            font-size: 12px;
            text-align: center;
            border: 1px solid var(--gray-200);
            border-radius: 6px;
            background: white;
            color: var(--gray-700);
            text-decoration: none;
            transition: all 0.15s;
        }}
        
        .person-action-btn:hover {{
            background: var(--gray-50);
            border-color: var(--gray-300);
        }}
    </style>
</head>
<body>
    {get_admin_sidebar('people', current_user.get('name', 'Admin User'), current_user.get('email', ''), current_user.get('linkedin_url', ''))}
    
    <div class="main-content">
        <div class="page-header">
            <div class="page-header-left">
                <h1 class="page-title">People & Network</h1>
                <p class="page-description">Team members and network contacts</p>
            </div>
        </div>
        
        <div class="container">
            <!-- Stats -->
            <div class="dashboard-stats">
                <div class="stat-card">
                    <div class="stat-number">{len(categories['Disruptive Ventures Team'])}</div>
                    <div class="stat-label">DV Team</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(categories['Portfolio Founders'])}</div>
                    <div class="stat-label">Founders</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(categories['Partners & Advisors'])}</div>
                    <div class="stat-label">Partners & Advisors</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(all_people)}</div>
                    <div class="stat-label">Total Contacts</div>
                </div>
            </div>
            
            {generate_categories_html(categories)}
        </div>
    </div>
    
    <script>
        function toggleCategory(categoryId) {{
            const content = document.getElementById(categoryId);
            const icon = event.currentTarget.querySelector('.expand-icon');
            
            content.classList.toggle('collapsed');
            
            if (content.classList.contains('collapsed')) {{
                icon.innerHTML = '<svg class="category-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"/></svg>';
            }} else {{
                icon.innerHTML = '<svg class="category-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="18 15 12 9 6 15"/></svg>';
            }}
        }}
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html)


# Old policy docs route removed - no longer needed


def generate_categories_html(categories):
    """Generate HTML for people categories."""
    html = []
    
    for category_name, people_list in categories.items():
        if not people_list:
            continue
            
        category_id = category_name.lower().replace(' ', '-').replace('&', 'and')
        
        html.append(f'''
        <div class="category-section">
            <div class="category-header" onclick="toggleCategory('{category_id}')">
                <span class="expand-icon">
                    <svg class="category-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <polyline points="18 15 12 9 6 15"/>
                    </svg>
                </span>
                <div class="category-title">{category_name}</div>
                <span class="category-count">{len(people_list)} people</span>
            </div>
            
            <div id="{category_id}" class="category-content">
                {generate_person_cards(people_list)}
            </div>
        </div>
        ''')
    
    return '\n'.join(html) if html else '<div class="empty-state"><div class="empty-state-title">No people yet</div></div>'


def generate_person_cards(people_list):
    """Generate person cards for a category."""
    cards = []
    
    for person in people_list:
        name = person.get('name', 'Unknown')
        email = person.get('email', '')
        job_title = person.get('job_title', '')
        linkedin_url = person.get('linkedin_url', '')
        
        # Generate initials for avatar
        initials = ''.join(word[0].upper() for word in name.split()[:2]) if name != 'Unknown' else '??'
        
        # Build action buttons
        actions_html = ''
        if email:
            actions_html += f'<a href="mailto:{email}" class="person-action-btn">Email</a>'
        if linkedin_url:
            actions_html += f'<a href="{linkedin_url}" target="_blank" class="person-action-btn">LinkedIn</a>'
        
        cards.append(f'''
        <div class="person-card">
            <div class="person-avatar">{initials}</div>
            <div class="person-name">{name}</div>
            {f'<div class="person-title">{job_title}</div>' if job_title else ''}
            {f'<div class="person-email">{email}</div>' if email else ''}
            {f'<div class="person-actions">{actions_html}</div>' if actions_html else ''}
        </div>
        ''')
    
    return '\n'.join(cards)



