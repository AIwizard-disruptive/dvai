"""Building Companies Wheel - Portfolio Company Support."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from supabase import create_client
from app.config import settings
from app.api.styles import get_dv_styles
from app.api.sidebar_component import get_admin_sidebar
import httpx

router = APIRouter(prefix="/wheels", tags=["Wheels - Building"])


@router.get("/building", response_class=HTMLResponse)
async def building_wheel():
    """Building Companies wheel - Kanban board for company activities."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get current user
        people = supabase.table('people').select('*').execute().data
        current_user = next((p for p in people if 'marcus' in p.get('name', '').lower() or 'markus' in p.get('name', '').lower()), None)
        if not current_user:
            current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        
        # Get tasks from Linear
        linear_tasks = await fetch_linear_tasks()
        
        # Fallback to action_items if Linear fails
        if not linear_tasks:
            db_tasks = supabase.table('action_items').select('*').order('created_at', desc=True).limit(50).execute().data
            linear_tasks = db_tasks
        
        # Organize by status (including canceled and duplicate)
        columns = {
            'backlog': [t for t in linear_tasks if t.get('status') in ['backlog', 'Backlog']],
            'todo': [t for t in linear_tasks if t.get('status') in ['todo', 'Todo', 'To Do']],
            'in_progress': [t for t in linear_tasks if t.get('status') in ['in_progress', 'In Progress', 'Started']],
            'done': [t for t in linear_tasks if t.get('status') in ['done', 'Done', 'Completed']],
            'canceled': [t for t in linear_tasks if t.get('status') in ['canceled', 'Canceled']],
            'duplicate': [t for t in linear_tasks if t.get('status') in ['duplicate', 'Duplicate']]
        }
        
    except Exception as e:
        current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        columns = {'backlog': [], 'todo': [], 'in_progress': [], 'done': []}
        print(f"Error: {e}")
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Building Companies - Admin</title>
    {get_dv_styles()}
    <style>
        .company-selector {{
            margin-bottom: 24px;
            padding: 12px;
            background: var(--gray-100);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        
        .company-name {{
            font-size: 16px;
            font-weight: 600;
            color: var(--gray-900);
        }}
        
        .filters {{
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
            align-items: center;
        }}
        
        .filter-btn {{
            padding: 6px 12px;
            background: var(--gray-100);
            border: 1px solid var(--gray-200);
            border-radius: 6px;
            font-size: 12px;
            color: var(--gray-700);
            cursor: pointer;
            transition: all 0.15s;
        }}
        
        .filter-btn:hover {{
            background: var(--gray-200);
        }}
        
        .filter-btn.active {{
            background: var(--gray-900);
            color: white;
            border-color: var(--gray-900);
        }}
        
        .kanban-board {{
            display: flex;
            gap: 12px;
            min-height: calc(100vh - 280px);
            overflow-x: auto;
            padding-bottom: 16px;
        }}
        
        .kanban-board.active {{
            display: flex;
        }}
        
        .kanban-column {{
            flex: 1;
            min-width: 280px;
            background: var(--gray-50);
            border-radius: 8px;
            padding: 12px;
            display: flex;
            flex-direction: column;
        }}
        
        .column-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--gray-200);
        }}
        
        .column-title {{
            font-size: 13px;
            font-weight: 600;
            color: var(--gray-700);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .column-count {{
            font-size: 12px;
            color: var(--gray-500);
            background: var(--gray-200);
            padding: 2px 6px;
            border-radius: 4px;
        }}
        
        .kanban-tasks {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .task-card {{
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 6px;
            padding: 12px;
            cursor: grab;
            transition: all 0.15s;
        }}
        
        .task-card:hover {{
            border-color: var(--gray-300);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .task-card:active {{
            cursor: grabbing;
            opacity: 0.8;
        }}
        
        .task-card.dragging {{
            opacity: 0.5;
        }}
        
        .task-title {{
            font-size: 13px;
            font-weight: 500;
            color: var(--gray-900);
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        
        .task-meta {{
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap;
            margin-top: 8px;
            font-size: 11px;
            color: var(--gray-500);
        }}
        
        .task-assignee {{
            display: flex;
            align-items: center;
            gap: 4px;
            padding: 2px 6px;
            background: var(--gray-100);
            border-radius: 3px;
            font-size: 11px;
            color: var(--gray-700);
        }}
        
        .task-deadline {{
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 11px;
            color: var(--gray-600);
        }}
        
        .sync-status {{
            font-size: 11px;
            color: var(--gray-500);
            padding: 4px 8px;
            background: var(--gray-100);
            border-radius: 4px;
        }}
        
        /* Timeline View (Asana-style) */
        .timeline-view {{
            display: none;
            padding: 24px 0;
        }}
        
        .timeline-view.active {{
            display: block;
        }}
        
        .timeline-header {{
            display: grid;
            grid-template-columns: 200px 1fr;
            gap: 16px;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--gray-200);
        }}
        
        .timeline-months {{
            display: flex;
            gap: 8px;
            overflow-x: auto;
        }}
        
        .timeline-month {{
            flex: 1;
            min-width: 120px;
            text-align: center;
            font-size: 12px;
            font-weight: 500;
            color: var(--gray-700);
            padding: 8px;
        }}
        
        .timeline-tasks {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .timeline-task {{
            display: grid;
            grid-template-columns: 200px 1fr;
            gap: 16px;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid var(--gray-100);
        }}
        
        .timeline-task-info {{
            font-size: 13px;
            color: var(--gray-900);
        }}
        
        .timeline-task-name {{
            font-weight: 500;
            margin-bottom: 4px;
        }}
        
        .timeline-task-meta {{
            font-size: 11px;
            color: var(--gray-500);
        }}
        
        .timeline-bar-container {{
            position: relative;
            height: 32px;
            background: var(--gray-50);
            border-radius: 4px;
        }}
        
        .timeline-bar {{
            position: absolute;
            height: 100%;
            background: var(--gray-900);
            border-radius: 4px;
            display: flex;
            align-items: center;
            padding: 0 8px;
            font-size: 11px;
            color: white;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s;
        }}
        
        .timeline-bar:hover {{
            background: var(--gray-700);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .view-switcher {{
            display: flex;
            gap: 4px;
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 6px;
            padding: 4px;
        }}
        
        .view-switcher-btn {{
            padding: 6px 12px;
            background: transparent;
            border: none;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            color: var(--gray-600);
            cursor: pointer;
            transition: all 0.15s;
        }}
        
        .view-switcher-btn:hover {{
            background: var(--gray-100);
            color: var(--gray-900);
        }}
        
        .view-switcher-btn.active {{
            background: var(--gray-100);
            color: var(--gray-900);
        }}
        
        /* Right Panel (Linear-style task detail) */
        .task-panel {{
            position: fixed;
            top: 0;
            right: -500px;
            width: 500px;
            height: 100vh;
            background: white;
            border-left: 1px solid var(--gray-200);
            box-shadow: -2px 0 8px rgba(0,0,0,0.1);
            z-index: 2000;
            transition: right 0.3s ease;
            overflow-y: auto;
        }}
        
        .task-panel.open {{
            right: 0;
        }}
        
        .task-panel-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100vh;
            background: rgba(0,0,0,0.3);
            z-index: 1999;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }}
        
        .task-panel-overlay.open {{
            opacity: 1;
            pointer-events: all;
        }}
        
        .task-panel-header {{
            padding: 20px;
            border-bottom: 1px solid var(--gray-200);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .task-panel-close {{
            padding: 8px;
            background: transparent;
            border: none;
            cursor: pointer;
            color: var(--gray-600);
            font-size: 20px;
        }}
        
        .task-panel-close:hover {{
            background: var(--gray-100);
            border-radius: 4px;
        }}
        
        .task-panel-body {{
            padding: 20px;
        }}
        
        .task-field {{
            margin-bottom: 24px;
        }}
        
        .task-field-label {{
            font-size: 12px;
            font-weight: 600;
            color: var(--gray-700);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .task-field input,
        .task-field textarea,
        .task-field select {{
            width: 100%;
            padding: 10px;
            border: 1px solid var(--gray-200);
            border-radius: 6px;
            font-size: 14px;
            color: var(--gray-900);
            background: white;
            font-family: inherit;
        }}
        
        .task-field input:focus,
        .task-field textarea:focus,
        .task-field select:focus {{
            outline: none;
            border-color: var(--gray-400);
        }}
        
        .task-field textarea {{
            min-height: 100px;
            resize: vertical;
        }}
        
        .task-actions {{
            display: flex;
            gap: 8px;
            padding: 20px;
            border-top: 1px solid var(--gray-200);
            position: sticky;
            bottom: 0;
            background: white;
        }}
        
        /* Dark mode panel */
        body.dark-mode .task-panel {{
            background: #2a2a2a;
            border-left-color: #404040;
        }}
        
        body.dark-mode .task-panel-header {{
            border-bottom-color: #404040;
        }}
        
        body.dark-mode .task-panel-close {{
            color: #999999;
        }}
        
        body.dark-mode .task-panel-close:hover {{
            background: #333333;
        }}
        
        body.dark-mode .task-field-label {{
            color: #cccccc;
        }}
        
        body.dark-mode .task-field input,
        body.dark-mode .task-field textarea,
        body.dark-mode .task-field select {{
            background: #333333;
            border-color: #404040;
            color: #e5e5e5;
        }}
        
        body.dark-mode .task-actions {{
            background: #2a2a2a;
            border-top-color: #404040;
        }}
        
        .task-priority {{
            padding: 2px 6px;
            background: var(--gray-100);
            border-radius: 3px;
            font-size: 10px;
            font-weight: 500;
            color: var(--gray-700);
        }}
        
        /* Dark mode kanban */
        body.dark-mode .company-selector {{
            background: #2a2a2a;
        }}
        
        body.dark-mode .company-name {{
            color: #e5e5e5;
        }}
        
        body.dark-mode .kanban-column {{
            background: #2a2a2a;
        }}
        
        body.dark-mode .column-header {{
            border-bottom-color: #404040;
        }}
        
        body.dark-mode .column-title {{
            color: #cccccc;
        }}
        
        body.dark-mode .column-count {{
            background: #404040;
            color: #999999;
        }}
        
        body.dark-mode .task-card {{
            background: #333333;
            border-color: #4a4a4a;
        }}
        
        body.dark-mode .task-card:hover {{
            border-color: #555555;
            box-shadow: 0 2px 4px rgba(255,255,255,0.05);
        }}
        
        body.dark-mode .task-title {{
            color: #e5e5e5;
        }}
        
        body.dark-mode .task-meta {{
            color: #999999;
        }}
        
        body.dark-mode .task-assignee,
        body.dark-mode .task-priority {{
            background: #404040;
            color: #cccccc;
        }}
        
        @media (max-width: 1200px) {{
            .kanban-board {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        
        @media (max-width: 768px) {{
            .kanban-board {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    {get_admin_sidebar('building', current_user.get('name', 'Admin User'), current_user.get('email', ''), current_user.get('linkedin_url', ''))}
    
    <div class="main-content">
        <div class="page-header">
            <div class="page-header-left">
                <h1 class="page-title">Building Companies</h1>
                <p class="page-description">Activity tracking and compliance management</p>
            </div>
        </div>
        
        <div class="container">
            <!-- Company Selector & Filters -->
            <div class="company-selector">
                <div>
                    <div class="company-name">Disruptive Ventures</div>
                    <div style="font-size: 12px; color: var(--gray-600);">
                        Our own company - 
                        <span id="sync-status" class="sync-status">Syncing...</span>
                    </div>
                </div>
                <button onclick="syncLinear()" class="btn-primary" style="padding: 6px 12px; font-size: 12px;">
                    Sync Now
                </button>
            </div>
            
            <!-- View Switcher & Filters -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <div class="view-switcher">
                    <button class="view-switcher-btn active" onclick="switchView('kanban')">Board</button>
                    <button class="view-switcher-btn" onclick="switchView('timeline')">Timeline</button>
                </div>
                
                <div class="filters">
                    <button class="filter-btn active" onclick="filterBy('all')">All</button>
                    <button class="filter-btn" onclick="filterBy('mine')">My Tasks</button>
                    <button class="filter-btn" onclick="filterBy('high')">High Priority</button>
                    <button class="filter-btn" onclick="filterBy('overdue')">Overdue</button>
                </div>
            </div>
            
            <!-- Kanban Board View -->
            <div class="kanban-board active" id="kanban-view">
                <!-- Backlog -->
                <div class="kanban-column" data-status="backlog" ondrop="drop(event)" ondragover="allowDrop(event)">
                    <div class="column-header">
                        <div class="column-title">Backlog</div>
                        <div class="column-count">{len(columns['backlog'])}</div>
                    </div>
                    <div class="kanban-tasks" id="backlog">
                        {generate_task_cards(columns['backlog'])}
                    </div>
                </div>
                
                <!-- To Do -->
                <div class="kanban-column" data-status="todo" ondrop="drop(event)" ondragover="allowDrop(event)">
                    <div class="column-header">
                        <div class="column-title">To Do</div>
                        <div class="column-count">{len(columns['todo'])}</div>
                    </div>
                    <div class="kanban-tasks" id="todo">
                        {generate_task_cards(columns['todo'])}
                    </div>
                </div>
                
                <!-- In Progress -->
                <div class="kanban-column" data-status="in_progress" ondrop="drop(event)" ondragover="allowDrop(event)">
                    <div class="column-header">
                        <div class="column-title">In Progress</div>
                        <div class="column-count">{len(columns['in_progress'])}</div>
                    </div>
                    <div class="kanban-tasks" id="in_progress">
                        {generate_task_cards(columns['in_progress'])}
                    </div>
                </div>
                
                <!-- Done -->
                <div class="kanban-column" data-status="done" ondrop="drop(event)" ondragover="allowDrop(event)">
                    <div class="column-header">
                        <div class="column-title">Done</div>
                        <div class="column-count">{len(columns['done'])}</div>
                    </div>
                    <div class="kanban-tasks" id="done">
                        {generate_task_cards(columns['done'])}
                    </div>
                </div>
                
                <!-- Canceled -->
                <div class="kanban-column" data-status="canceled" ondrop="drop(event)" ondragover="allowDrop(event)" style="opacity: 0.7;">
                    <div class="column-header">
                        <div class="column-title">Canceled</div>
                        <div class="column-count">{len(columns.get('canceled', []))}</div>
                    </div>
                    <div class="kanban-tasks" id="canceled">
                        {generate_task_cards(columns.get('canceled', []))}
                    </div>
                </div>
            </div>
            
        </div>
    </div>
    
    <script>
        let draggedElement = null;
        
        async function syncLinear() {{
            const btn = event.target;
            btn.disabled = true;
            btn.textContent = 'Syncing...';
            
            try {{
                const response = await fetch('/wheels/building/sync-linear', {{
                    method: 'POST'
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    // Reload page to show new tasks
                    window.location.reload();
                }} else {{
                    alert('Sync failed. Check console for details.');
                    btn.disabled = false;
                    btn.textContent = 'Sync from Linear';
                }}
            }} catch (error) {{
                console.error('Sync error:', error);
                alert('Sync failed: ' + error.message);
                btn.disabled = false;
                btn.textContent = 'Sync Now';
            }}
        }}
        
        // Auto-sync every minute
        async function autoSync() {{
            try {{
                const response = await fetch('/wheels/building/sync-linear', {{
                    method: 'POST'
                }});
                
                if (response.ok) {{
                    const data = await response.json();
                    document.getElementById('sync-status').textContent = `Last synced: ${{new Date().toLocaleTimeString()}}`;
                    
                    // Silently reload if new tasks
                    if (data.tasks_synced > 0) {{
                        // Could update DOM instead of reload for smoother UX
                    }}
                }}
            }} catch (error) {{
                console.error('Auto-sync error:', error);
            }}
        }}
        
        // Initial sync on load
        window.addEventListener('load', () => {{
            autoSync();
            // Set interval to sync every minute
            setInterval(autoSync, 60000);
        }});
        
        // Filter tasks
        function filterBy(filter) {{
            // Update active button
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            const tasks = document.querySelectorAll('.task-card');
            
            tasks.forEach(task => {{
                const assignee = task.querySelector('.task-assignee')?.textContent || '';
                const priority = task.querySelector('.task-priority')?.textContent || '';
                const deadline = task.querySelector('.task-deadline')?.textContent || '';
                
                let show = true;
                
                if (filter === 'mine') {{
                    show = assignee.includes('Markus') || assignee.includes('Marcus');
                }} else if (filter === 'high') {{
                    show = priority.includes('high') || priority.includes('urgent');
                }} else if (filter === 'overdue') {{
                    const dateMatch = deadline.match(/\\d{{4}}-\\d{{2}}-\\d{{2}}/);
                    if (dateMatch) {{
                        const dueDate = new Date(dateMatch[0]);
                        const today = new Date();
                        show = dueDate < today;
                    }} else {{
                        show = false;
                    }}
                }}
                
                task.style.display = show ? 'block' : 'none';
            }});
            
            updateColumnCounts();
        }}
        
        // Switch between Kanban and Timeline views
        function switchView(view) {{
            // Update buttons
            document.querySelectorAll('.view-switcher-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Show/hide views
            if (view === 'kanban') {{
                document.getElementById('kanban-view').classList.add('active');
                document.getElementById('kanban-view').style.display = 'flex';
                document.getElementById('timeline-view').classList.remove('active');
            }} else {{
                document.getElementById('kanban-view').classList.remove('active');
                document.getElementById('kanban-view').style.display = 'none';
                document.getElementById('timeline-view').classList.add('active');
            }}
            
            // Save preference
            localStorage.setItem('building-view', view);
        }}
        
        // Open task detail panel
        function openTaskPanel(taskCard) {{
            // Prevent drag from opening panel
            if (taskCard.classList.contains('dragging')) return;
            
            const panel = document.getElementById('task-panel');
            const overlay = document.getElementById('task-panel-overlay');
            
            // Populate panel with task data
            document.getElementById('task-id-display').textContent = taskCard.dataset.linearId || 'Task Details';
            document.getElementById('edit-title').value = taskCard.dataset.title || '';
            document.getElementById('edit-description').value = taskCard.dataset.description || '';
            document.getElementById('edit-status').value = taskCard.dataset.status || 'todo';
            document.getElementById('edit-priority').value = taskCard.dataset.priority || 'medium';
            document.getElementById('edit-assignee').value = taskCard.dataset.assignee || '';
            document.getElementById('edit-due-date').value = taskCard.dataset.dueDate || '';
            
            // Show Linear link if exists
            const linearUrl = taskCard.dataset.linearUrl;
            if (linearUrl) {{
                document.getElementById('linear-link-field').style.display = 'block';
                document.getElementById('linear-link').href = linearUrl;
            }} else {{
                document.getElementById('linear-link-field').style.display = 'none';
            }}
            
            // Store task ID for saving
            panel.dataset.taskId = taskCard.dataset.taskId;
            panel.dataset.taskCard = taskCard.id || '';
            
            // Open panel
            panel.classList.add('open');
            overlay.classList.add('open');
            document.body.style.overflow = 'hidden';
        }}
        
        // Close task detail panel
        function closeTaskPanel() {{
            const panel = document.getElementById('task-panel');
            const overlay = document.getElementById('task-panel-overlay');
            
            panel.classList.remove('open');
            overlay.classList.remove('open');
            document.body.style.overflow = 'auto';
        }}
        
        // Save task changes
        async function saveTask() {{
            const panel = document.getElementById('task-panel');
            const taskId = panel.dataset.taskId;
            
            const updates = {{
                title: document.getElementById('edit-title').value,
                description: document.getElementById('edit-description').value,
                status: document.getElementById('edit-status').value,
                priority: document.getElementById('edit-priority').value,
                owner_name: document.getElementById('edit-assignee').value,
                due_date: document.getElementById('edit-due-date').value
            }};
            
            try {{
                // TODO: Call API to save changes
                console.log('Saving task:', taskId, updates);
                
                // For now, just close and reload
                closeTaskPanel();
                window.location.reload();
            }} catch (error) {{
                console.error('Save error:', error);
                alert('Failed to save: ' + error.message);
            }}
        }}
        
        // Prevent panel from opening when dragging
        document.addEventListener('DOMContentLoaded', () => {{
            document.querySelectorAll('.task-card').forEach(card => {{
                card.addEventListener('dragstart', (e) => {{
                    e.target.style.pointerEvents = 'none';
                    setTimeout(() => {{ e.target.style.pointerEvents = 'auto'; }}, 100);
                }});
            }});
        }});
        
        // Restore view preference
        window.addEventListener('load', () => {{
            const savedView = localStorage.getItem('building-view');
            if (savedView === 'timeline') {{
                document.getElementById('timeline-view').classList.add('active');
                document.getElementById('kanban-view').style.display = 'none';
                document.querySelectorAll('.view-switcher-btn')[1].classList.add('active');
                document.querySelectorAll('.view-switcher-btn')[0].classList.remove('active');
            }}
        }}
        
        function allowDrop(ev) {{
            ev.preventDefault();
        }}
        
        function drag(ev) {{
            draggedElement = ev.target;
            ev.target.classList.add('dragging');
        }}
        
        function drop(ev) {{
            ev.preventDefault();
            
            if (draggedElement) {{
                const column = ev.currentTarget;
                const tasksContainer = column.querySelector('.kanban-tasks');
                
                // Append to new column
                tasksContainer.appendChild(draggedElement);
                draggedElement.classList.remove('dragging');
                
                // Get new status
                const newStatus = column.dataset.status;
                const taskId = draggedElement.dataset.taskId;
                
                // Update count badges
                updateColumnCounts();
                
                // TODO: Sync to backend
                console.log(`Task ${{taskId}} moved to ${{newStatus}}`);
                
                draggedElement = null;
            }}
        }}
        
        function updateColumnCounts() {{
            ['backlog', 'todo', 'in_progress', 'done', 'canceled'].forEach(status => {{
                const column = document.querySelector(`[data-status="${{status}}"]`);
                if (column) {{
                    const count = column.querySelectorAll('.task-card').length;
                    const badge = column.querySelector('.column-count');
                    if (badge) badge.textContent = count;
                }}
            }});
        }}
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html)


def generate_task_cards(tasks):
    """Generate draggable task cards for Kanban board."""
    if not tasks:
        return '<div style="text-align: center; padding: 24px; color: var(--gray-500); font-size: 12px;">No tasks</div>'
    
    cards = []
    for task in tasks:
        # Get assignee initials
        assignee = task.get('owner_name', 'Unassigned')
        initials = ''.join([n[0].upper() for n in assignee.split()[:2]]) if assignee != 'Unassigned' else '?'
        
        # Format deadline
        deadline = task.get('due_date', '')
        deadline_display = str(deadline)[:10] if deadline else 'No deadline'
        
        # Priority
        priority = task.get('priority', 'medium')
        
        # Description preview
        description = task.get('description', '')
        description_html = f'<div style="font-size: 12px; color: var(--gray-600); margin-top: 6px; line-height: 1.4;">{description[:80]}{"..." if len(description) > 80 else ""}</div>' if description else ''
        
        # Linear link
        linear_url = task.get('linear_issue_url', '')
        linear_id = task.get('linear_issue_id', '')
        
        # Escape quotes for JavaScript
        title_js = task.get('title', 'Untitled').replace("'", "\\'").replace('"', '\\"')
        description_js = description.replace("'", "\\'").replace('"', '\\"') if description else ''
        
        card = f'''
        <div class="task-card" 
             draggable="true" 
             ondragstart="drag(event)" 
             onclick="openTaskPanel(this)" 
             data-task-id="{task.get('id', '')}"
             data-title="{title_js}"
             data-description="{description_js}"
             data-status="{task.get('status', 'todo')}"
             data-priority="{priority}"
             data-assignee="{assignee}"
             data-due-date="{deadline if deadline and deadline != 'No deadline' else ''}"
             data-linear-url="{linear_url}"
             data-linear-id="{linear_id}">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 4px;">
                <div class="task-title" style="flex: 1;">{task.get('title', 'Untitled')}</div>
                {f'<span style="font-size: 11px; color: var(--gray-500); margin-left: 8px;">{linear_id}</span>' if linear_id else ''}
            </div>
            {description_html}
            <div class="task-meta">
                <div class="task-assignee">
                    <span style="width: 18px; height: 18px; border-radius: 50%; background: var(--gray-200); display: inline-flex; align-items: center; justify-content: center; font-size: 9px; font-weight: 600; color: var(--gray-700);">{initials}</span>
                    <span>{assignee}</span>
                </div>
                {f'<div class="task-deadline">{deadline_display}</div>' if deadline else ''}
                <div class="task-priority">{priority}</div>
            </div>
        </div>
        '''
        cards.append(card)
    
    return '\n'.join(cards)


async def fetch_linear_tasks():
    """Fetch tasks from Linear API for Disruptive Ventures."""
    try:
        if not settings.linear_api_key:
            print("Linear API key not configured")
            return []
        
        # GraphQL query to get issues
        query = """
        query {
          issues(
            first: 100
            filter: {
              team: { name: { contains: "Disruptive" } }
            }
          ) {
            nodes {
              id
              identifier
              title
              description
              priority
              state {
                name
              }
              assignee {
                name
              }
              dueDate
              url
            }
          }
        }
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://api.linear.app/graphql',
                json={'query': query},
                headers={
                    'Authorization': settings.linear_api_key,
                    'Content-Type': 'application/json'
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                issues = data.get('data', {}).get('issues', {}).get('nodes', [])
                
                # Convert Linear issues to our format
                tasks = []
                for issue in issues:
                    tasks.append({
                        'id': issue.get('id'),
                        'title': issue.get('title'),
                        'description': issue.get('description', ''),
                        'owner_name': issue.get('assignee', {}).get('name') if issue.get('assignee') else 'Unassigned',
                        'due_date': issue.get('dueDate'),
                        'priority': map_linear_priority(issue.get('priority', 0)),
                        'status': map_linear_status(issue.get('state', {}).get('name', 'Todo')),
                        'linear_issue_url': issue.get('url'),
                        'linear_issue_id': issue.get('identifier')
                    })
                
                return tasks
            else:
                print(f"Linear API error: {response.status_code}")
                return []
                
    except Exception as e:
        print(f"Error fetching Linear tasks: {e}")
        return []


def map_linear_priority(priority_num):
    """Map Linear priority (0-4) to our format."""
    priority_map = {
        0: 'none',
        1: 'low',
        2: 'medium',
        3: 'high',
        4: 'urgent'
    }
    return priority_map.get(priority_num, 'medium')


def map_linear_status(status_name):
    """Map Linear status names to our kanban columns."""
    status_name_lower = status_name.lower()
    
    if any(x in status_name_lower for x in ['backlog', 'icebox', 'triage']):
        return 'backlog'
    elif any(x in status_name_lower for x in ['todo', 'planned', 'ready']):
        return 'todo'
    elif any(x in status_name_lower for x in ['progress', 'started', 'doing']):
        return 'in_progress'
    elif any(x in status_name_lower for x in ['done', 'completed', 'canceled', 'closed']):
        return 'done'
    else:
        return 'todo'


@router.post("/building/sync-linear")
async def sync_linear_tasks():
    """Manual sync button - fetch latest tasks from Linear."""
    tasks = await fetch_linear_tasks()
    
    return {
        "success": True,
        "tasks_synced": len(tasks),
        "message": f"Synced {len(tasks)} tasks from Linear"
    }


def generate_timeline_view(columns):
    """Generate Asana-style timeline view."""
    from datetime import datetime, timedelta
    
    # Get all tasks with dates
    all_tasks = []
    for status_tasks in columns.values():
        all_tasks.extend(status_tasks)
    
    # Filter tasks with due dates
    tasks_with_dates = [t for t in all_tasks if t.get('due_date')]
    
    if not tasks_with_dates:
        return '<div class="empty-state"><div class="empty-state-title">No tasks with deadlines</div><p style="font-size: 13px; color: var(--gray-500); margin-top: 8px;">Add due dates to tasks to see them in timeline view.</p></div>'
    
    # Sort by due date
    tasks_with_dates.sort(key=lambda t: t.get('due_date', ''))
    
    # Generate timeline header (next 3 months)
    today = datetime.now()
    months = []
    for i in range(3):
        month_date = today + timedelta(days=30*i)
        months.append(month_date.strftime('%B %Y'))
    
    # Generate timeline HTML
    html = f'''
    <div class="timeline-header">
        <div style="font-size: 12px; font-weight: 600; color: var(--gray-700);">TASK</div>
        <div class="timeline-months">
            {' '.join([f'<div class="timeline-month">{month}</div>' for month in months])}
        </div>
    </div>
    
    <div class="timeline-tasks">
    '''
    
    for task in tasks_with_dates:
        assignee = task.get('owner_name', 'Unassigned')
        initials = ''.join([n[0].upper() for n in assignee.split()[:2]]) if assignee != 'Unassigned' else '?'
        due_date = task.get('due_date', '')
        
        # Calculate position and width
        try:
            task_date = datetime.fromisoformat(str(due_date)[:10])
            days_from_now = (task_date - today).days
            
            # Position as percentage (90 days = 100%)
            position = max(0, min(100, (days_from_now / 90) * 100))
            width = 10  # Default width in percentage
            
        except:
            position = 0
            width = 10
        
        html += f'''
        <div class="timeline-task">
            <div class="timeline-task-info">
                <div class="timeline-task-name">{task.get('title', 'Untitled')[:40]}</div>
                <div class="timeline-task-meta">
                    <span style="width: 18px; height: 18px; border-radius: 50%; background: var(--gray-200); display: inline-flex; align-items: center; justify-content: center; font-size: 9px; font-weight: 600; color: var(--gray-700); margin-right: 4px;">{initials}</span>
                    {assignee}
                </div>
            </div>
            <div class="timeline-bar-container">
                <div class="timeline-bar" style="left: {position}%; width: {width}%;" title="{task.get('title', '')}">
                    {str(due_date)[:10]}
                </div>
            </div>
        </div>
        '''
    
    html += '</div>'
    
    return html


