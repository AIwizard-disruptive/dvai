"""Dashboard API endpoint - Monochrome minimal design with left sidebar."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from datetime import datetime

from app.config import settings
from app.api.styles import get_dv_styles
from app.api.sidebar_component import get_admin_sidebar

router = APIRouter()


@router.get("/dashboard-ui", response_class=HTMLResponse)
async def dashboard_ui():
    """
    Dashboard UI - Monochrome minimal design with left sidebar.
    NO colored icons, NO gradients, NO colored badges.
    """
    
    try:
        from supabase import create_client
        
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get meetings (include display_title for clean names)
        meetings = supabase.table('meetings').select('*').order('created_at', desc=True).limit(20).execute().data
        
        # Get decisions
        decisions = supabase.table('decisions').select('*').order('created_at', desc=True).limit(20).execute().data
        
        # Get action items
        action_items = supabase.table('action_items').select('*').order('created_at', desc=True).limit(20).execute().data
        
        # Get unique people count
        people = supabase.table('people').select('*').execute().data
        unique_names = set(p.get('name', '').strip().lower() for p in people if p.get('name'))
        unique_count = len(unique_names)
        
        # Get current user - Markus Löwegren
        current_user = next((p for p in people if 'marcus' in p.get('name', '').lower() or 'markus' in p.get('name', '').lower()), None)
        if not current_user:
            current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        
        stats = (len(meetings), len(decisions), len(action_items), unique_count)
        
    except Exception as e:
        meetings = []
        decisions = []
        action_items = []
        stats = (0, 0, 0, 0)
        current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        print(f"Dashboard error: {e}")
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Disruptive Ventures</title>
    <meta http-equiv="refresh" content="30">
    {get_dv_styles()}
    <style>
        .dashboard-tabs {{
            display: flex;
            gap: 8px;
            margin-bottom: 24px;
            border-bottom: 1px solid var(--gray-200);
            padding-bottom: 0;
        }}
        
        .dashboard-tab {{
            padding: 10px 16px;
            border: none;
            background: transparent;
            color: var(--gray-600);
            font-weight: 500;
            cursor: pointer;
            border-radius: 6px 6px 0 0;
            transition: all 0.15s;
            font-size: 13px;
            border-bottom: 2px solid transparent;
        }}
        
        .dashboard-tab:hover {{
            color: var(--gray-900);
            background: var(--gray-50);
        }}
        
        .dashboard-tab.active {{
            color: var(--gray-900);
            border-bottom-color: var(--gray-900);
            background: transparent;
        }}
        
        .dashboard-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }}
        
        .section {{
            display: none;
        }}
        
        .section.active {{
            display: block;
        }}
        
        .item-card {{
            background: white;
            padding: 16px;
            border-radius: 8px;
            border: 1px solid var(--gray-200);
            margin-bottom: 12px;
            transition: all 0.15s;
        }}
        
        .item-card:hover {{
            border-color: var(--gray-300);
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .item-title {{
            font-size: 14px;
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 8px;
        }}
        
        .item-meta {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            font-size: 12px;
            color: var(--gray-500);
        }}
    </style>
</head>
<body>
    {get_admin_sidebar('dashboard', current_user.get('name', 'Admin User'), current_user.get('email', ''), current_user.get('linkedin_url', ''))}
    
    <div class="main-content">
        <div class="page-header">
            <h1 class="page-title">Dashboard</h1>
            <p class="page-description">System monitoring and data overview</p>
        </div>
        
        <div class="container">
            <!-- Stats -->
            <div class="dashboard-stats">
                <div class="stat-card">
                    <div class="stat-number">{stats[0]}</div>
                    <div class="stat-label">Meetings</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats[1]}</div>
                    <div class="stat-label">Decisions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats[2]}</div>
                    <div class="stat-label">Action Items</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats[3]}</div>
                    <div class="stat-label">Attendees</div>
                </div>
            </div>
            
            <!-- Tabs -->
            <div class="dashboard-tabs">
                <button class="dashboard-tab active" onclick="showTab('meetings')">Meetings</button>
                <button class="dashboard-tab" onclick="showTab('decisions')">Decisions</button>
                <button class="dashboard-tab" onclick="showTab('actions')">Action Items</button>
            </div>
            
            <!-- Meetings Section -->
            <div id="meetings" class="section active">
                <div class="section-header">
                    <h2>Meetings ({len(meetings)})</h2>
                    <div class="view-toggle">
                        <button class="view-toggle-btn" onclick="toggleView('meetings', 'card')" title="Card View">
                            <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                                <rect x="3" y="3" width="7" height="7"/>
                                <rect x="14" y="3" width="7" height="7"/>
                                <rect x="14" y="14" width="7" height="7"/>
                                <rect x="3" y="14" width="7" height="7"/>
                            </svg>
                        </button>
                        <button class="view-toggle-btn active" onclick="toggleView('meetings', 'list')" title="List View">
                            <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                                <line x1="8" y1="6" x2="21" y2="6"/>
                                <line x1="8" y1="12" x2="21" y2="12"/>
                                <line x1="8" y1="18" x2="21" y2="18"/>
                                <line x1="3" y1="6" x2="3.01" y2="6"/>
                                <line x1="3" y1="12" x2="3.01" y2="12"/>
                                <line x1="3" y1="18" x2="3.01" y2="18"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div id="meetings-container" class="list-view">
                    {generate_meeting_cards(meetings)}
                </div>
            </div>
            
            <!-- Decisions Section -->
            <div id="decisions" class="section">
                <div class="section-header">
                    <h2>Decisions ({len(decisions)})</h2>
                    <div class="view-toggle">
                        <button class="view-toggle-btn" onclick="toggleView('decisions', 'card')" title="Card View">
                            <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                                <rect x="3" y="3" width="7" height="7"/>
                                <rect x="14" y="3" width="7" height="7"/>
                                <rect x="14" y="14" width="7" height="7"/>
                                <rect x="3" y="14" width="7" height="7"/>
                            </svg>
                        </button>
                        <button class="view-toggle-btn active" onclick="toggleView('decisions', 'list')" title="List View">
                            <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                                <line x1="8" y1="6" x2="21" y2="6"/>
                                <line x1="8" y1="12" x2="21" y2="12"/>
                                <line x1="8" y1="18" x2="21" y2="18"/>
                                <line x1="3" y1="6" x2="3.01" y2="6"/>
                                <line x1="3" y1="12" x2="3.01" y2="12"/>
                                <line x1="3" y1="18" x2="3.01" y2="18"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div id="decisions-container" class="list-view">
                    {generate_decision_cards(decisions)}
                </div>
            </div>
            
            <!-- Actions Section -->
            <div id="actions" class="section">
                <div class="section-header">
                    <h2>Action Items ({len(action_items)})</h2>
                    <div class="view-toggle">
                        <button class="view-toggle-btn" onclick="toggleView('actions', 'card')" title="Card View">
                            <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                                <rect x="3" y="3" width="7" height="7"/>
                                <rect x="14" y="3" width="7" height="7"/>
                                <rect x="14" y="14" width="7" height="7"/>
                                <rect x="3" y="14" width="7" height="7"/>
                            </svg>
                        </button>
                        <button class="view-toggle-btn active" onclick="toggleView('actions', 'list')" title="List View">
                            <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                                <line x1="8" y1="6" x2="21" y2="6"/>
                                <line x1="8" y1="12" x2="21" y2="12"/>
                                <line x1="8" y1="18" x2="21" y2="18"/>
                                <line x1="3" y1="6" x2="3.01" y2="6"/>
                                <line x1="3" y1="12" x2="3.01" y2="12"/>
                                <line x1="3" y1="18" x2="3.01" y2="18"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div id="actions-container" class="list-view">
                    {generate_action_cards(action_items)}
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function showTab(tabName) {{
            // Hide all sections
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.dashboard-tab').forEach(t => t.classList.remove('active'));
            
            // Show selected
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}
        
        function toggleView(section, view) {{
            const container = document.getElementById(section + '-container');
            const buttons = event.currentTarget.parentElement.querySelectorAll('.view-toggle-btn');
            
            // Update active button
            buttons.forEach(b => b.classList.remove('active'));
            event.currentTarget.classList.add('active');
            
            // Toggle view
            if (view === 'list') {{
                container.className = 'list-view';
            }} else {{
                container.className = 'card-view';
            }}
            
            // Save preference
            localStorage.setItem(section + '-view', view);
        }}
        
        // Restore view preferences on load
        window.addEventListener('load', () => {{
            ['meetings', 'decisions', 'actions'].forEach(section => {{
                const savedView = localStorage.getItem(section + '-view');
                if (savedView === 'card') {{
                    const container = document.getElementById(section + '-container');
                    if (container) container.className = 'card-view';
                }}
            }});
        }});
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html)


def generate_meeting_cards(meetings):
    """Generate monochrome meeting cards."""
    if not meetings:
        return '<div class="empty-state"><div class="empty-state-title">No meetings yet</div></div>'
    
    cards = []
    for m in meetings:
        card = f"""
        <div class="item-card">
            <div class="item-title">{m.get('display_title') or m.get('title', 'Untitled Meeting')}</div>
            <div class="item-meta">
                <span>{str(m.get('meeting_date', 'No date'))[:10]}</span>
                <span>•</span>
                <span>{m.get('duration_minutes', 'N/A')} min</span>
                <span>•</span>
                <span>{m.get('company', 'Unknown')}</span>
            </div>
        </div>
        """
        cards.append(card)
    
    return '\n'.join(cards)


def generate_decision_cards(decisions):
    """Generate monochrome decision cards."""
    if not decisions:
        return '<div class="empty-state"><div class="empty-state-title">No decisions yet</div></div>'
    
    cards = []
    for d in decisions:
        card = f"""
        <div class="item-card">
            <div class="item-title">{d.get('decision', 'No decision text')[:100]}...</div>
            {f'<p style="font-size: 13px; color: var(--gray-600); margin-top: 8px;">{d.get("rationale", "")[:150]}</p>' if d.get('rationale') else ''}
            <div class="item-meta" style="margin-top: 8px;">
                <span>{str(d.get('created_at', 'Unknown'))[:10]}</span>
            </div>
        </div>
        """
        cards.append(card)
    
    return '\n'.join(cards)


def generate_action_cards(actions):
    """Generate monochrome action cards with deadline, description, and Linear link."""
    if not actions:
        return '<div class="empty-state"><div class="empty-state-title">No action items yet</div></div>'
    
    cards = []
    for a in actions:
        # Get Linear URL if exists
        linear_url = a.get('linear_issue_url', '')
        linear_id = a.get('linear_issue_id', '')
        
        # Format due date
        due_date = a.get('due_date', '')
        due_display = str(due_date)[:10] if due_date else 'No deadline'
        
        # Description
        description = a.get('description', '')
        description_html = f'<p style="font-size: 13px; color: var(--gray-600); margin: 8px 0; line-height: 1.5;">{description[:150]}{"..." if len(description) > 150 else ""}</p>' if description else ''
        
        card = f"""
        <div class="item-card">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                <div class="item-title">{a.get('title', 'Untitled')}</div>
                <div style="display: flex; gap: 4px;">
                    <span class="badge">{a.get('priority', 'low')}</span>
                    <span class="badge">{a.get('status', 'todo')}</span>
                </div>
            </div>
            
            {description_html}
            
            <div class="item-meta">
                <span>{a.get('owner_name', 'Unassigned')}</span>
                <span>•</span>
                <span>📅 {due_display}</span>
                {f'<span>•</span><a href="{linear_url}" target="_blank" style="color: var(--gray-900); text-decoration: none; font-weight: 500;">Linear {linear_id}</a>' if linear_url else ''}
            </div>
        </div>
        """
        cards.append(card)
    
    return '\n'.join(cards)
