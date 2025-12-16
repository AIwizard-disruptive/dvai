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
    """People & Network wheel - HR & Culture documents."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get all policy documents
        policies = supabase.table('policy_documents').select('*').order('created_at', desc=True).execute().data
        
        # Get people for user profile - Markus Löwegren
        people = supabase.table('people').select('*').execute().data
        current_user = next((p for p in people if 'marcus' in p.get('name', '').lower() or 'markus' in p.get('name', '').lower()), None)
        if not current_user:
            current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        
        # Organize by category
        categories = {
            'HR & Culture': [],
            'Recognition Program': [],
            'Culture Program': [],
            'Onboarding': [],
            'Policy Documents': []
        }
        
        for policy in policies:
            policy_type = policy.get('policy_type', 'other')
            if policy_type == 'culture':
                categories['Culture Program'].append(policy)
            elif policy_type == 'hr':
                categories['HR & Culture'].append(policy)
            elif policy_type == 'onboarding':
                categories['Onboarding'].append(policy)
            elif policy_type == 'policy':
                categories['Policy Documents'].append(policy)
            else:
                categories['HR & Culture'].append(policy)
        
    except Exception as e:
        categories = {}
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
    </style>
</head>
<body>
    {get_admin_sidebar('people', current_user.get('name', 'Admin User'), current_user.get('email', ''), current_user.get('linkedin_url', ''))}
    
    <div class="main-content">
        <div class="page-header">
            <div class="page-header-left">
                <h1 class="page-title">People & Network</h1>
                <p class="page-description">HR, Culture & Team Documentation</p>
            </div>
        </div>
        
        <div class="container">
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


@router.get("/people/docs", response_class=HTMLResponse)
async def people_docs():
    """People & Network - Policy Documents page with Google Drive links."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get all policy documents
        policies = supabase.table('policy_documents').select('*').order('created_at', desc=True).execute().data
        
        # Get current user
        people = supabase.table('people').select('*').execute().data
        current_user = next((p for p in people if 'marcus' in p.get('name', '').lower() or 'markus' in p.get('name', '').lower()), None)
        if not current_user:
            current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        
        # Organize by category
        categories = {
            'HR & Culture': [],
            'Culture Program': [],
            'Onboarding': [],
            'Policy Documents': [],
            'Other': []
        }
        
        for policy in policies:
            policy_type = policy.get('policy_type', 'other')
            if policy_type == 'culture':
                categories['Culture Program'].append(policy)
            elif policy_type == 'hr':
                categories['HR & Culture'].append(policy)
            elif policy_type == 'onboarding':
                categories['Onboarding'].append(policy)
            elif policy_type == 'policy':
                categories['Policy Documents'].append(policy)
            else:
                categories['Other'].append(policy)
        
    except Exception as e:
        categories = {}
        current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        print(f"Error: {e}")
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Policy Documents - People & Network</title>
    {get_dv_styles()}
    <style>
        .docs-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 12px;
        }}
        
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
        
        .expand-icon {{
            width: 20px;
            height: 20px;
            color: var(--gray-600);
        }}
        
        .category-content {{
            display: block;
        }}
        
        .category-content.collapsed {{
            display: none;
        }}
    </style>
</head>
<body>
    {get_admin_sidebar('people-docs', current_user.get('name', 'Admin User'), current_user.get('email', ''), current_user.get('linkedin_url', ''))}
    
    <div class="main-content">
        <div class="page-header">
            <div class="page-header-left">
                <h1 class="page-title">Policy Documents</h1>
                <p class="page-description">All company policies and documents in Google Drive</p>
            </div>
        </div>
        
        <div class="container">
            {generate_policy_categories_html(categories)}
        </div>
    </div>
    
    <script>
        function toggleCategory(categoryId) {{
            const content = document.getElementById(categoryId);
            const icon = event.currentTarget.querySelector('.expand-icon');
            
            content.classList.toggle('collapsed');
            
            if (content.classList.contains('collapsed')) {{
                icon.innerHTML = '<svg class="category-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="width: 20px; height: 20px;"><polyline points="6 9 12 15 18 9"/></svg>';
            }} else {{
                icon.innerHTML = '<svg class="category-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="width: 20px; height: 20px;"><polyline points="18 15 12 9 6 15"/></svg>';
            }}
        }}
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html)


def generate_policy_categories_html(categories):
    """Generate HTML for policy categories with Google Drive links."""
    html = []
    
    for category_name, documents in categories.items():
        if not documents:
            continue
            
        category_id = category_name.lower().replace(' ', '-').replace('&', 'and')
        
        html.append(f'''
        <div class="category-section">
            <div class="category-header" onclick="toggleCategory('{category_id}')">
                <span class="expand-icon">
                    <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="width: 20px; height: 20px;">
                        <polyline points="18 15 12 9 6 15"/>
                    </svg>
                </span>
                <div class="category-title">{category_name}</div>
                <span class="category-count">{len(documents)} documents</span>
            </div>
            
            <div id="{category_id}" class="category-content">
                <div class="docs-grid">
                    {generate_policy_doc_cards(documents)}
                </div>
            </div>
        </div>
        ''')
    
    return '\n'.join(html) if html else '<div class="empty-state"><div class="empty-state-title">No documents yet</div><p style="font-size: 13px; color: var(--gray-500); margin-top: 8px;">Add policy documents in Knowledge Bank to see them here.</p></div>'


def generate_policy_doc_cards(documents):
    """Generate document cards with Google Drive links."""
    cards = []
    
    for doc in documents:
        # Required reading badge
        required_badge = '<span style="background: var(--gray-200); color: var(--gray-700); padding: 2px 6px; border-radius: 3px; font-size: 10px; margin-left: 6px;">REQUIRED</span>' if doc.get('is_required_reading') else ''
        
        cards.append(f'''
        <a href="{doc.get('google_drive_url', '#')}" target="_blank" class="doc-card">
            <div class="doc-icon">
                <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                </svg>
            </div>
            <div class="doc-title">{doc.get('title', 'Untitled')}{required_badge}</div>
            <div class="doc-meta">
                {doc.get('description', 'No description')[:100]}{"..." if len(doc.get('description', '')) > 100 else ''}
            </div>
            <div class="doc-meta" style="margin-top: 8px;">
                <span>Added: {str(doc.get('created_at', ''))[:10]}</span>
            </div>
        </a>
        ''')
    
    return '\n'.join(cards)


def generate_categories_html(categories):
    """Generate HTML for document categories."""
    html = []
    
    for category_name, documents in categories.items():
        if not documents:
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
                <span class="category-count">{len(documents)} documents</span>
            </div>
            
            <div id="{category_id}" class="category-content">
                {generate_document_cards(documents)}
            </div>
        </div>
        ''')
    
    return '\n'.join(html) if html else '<div class="empty-state"><div class="empty-state-title">No documents yet</div></div>'


def generate_document_cards(documents):
    """Generate document cards for a category."""
    cards = []
    
    for doc in documents:
        cards.append(f'''
        <a href="{doc.get('google_drive_url', '#')}" target="_blank" class="doc-card">
            <div class="doc-icon">
                <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                </svg>
            </div>
            <div class="doc-title">{doc.get('title', 'Untitled')}</div>
            <div class="doc-meta">
                {doc.get('description', 'No description')[:80]}
            </div>
            <div class="doc-meta" style="margin-top: 8px;">
                <span style="background: var(--gray-100); padding: 2px 6px; border-radius: 3px; font-size: 11px;">
                    {doc.get('policy_type', 'document')}
                </span>
            </div>
        </a>
        ''')
    
    return '\n'.join(cards)


