"""
Sidebar Component for Backend Admin Interface
Consistent left sidebar navigation across all admin pages
"""

def get_admin_sidebar(active_page="", user_name="Admin User", user_email="", user_image_url=""):
    """
    Generate consistent admin sidebar HTML.
    
    Args:
        active_page: Current page identifier (e.g., 'dashboard', 'knowledge', 'meetings')
        user_name: Logged-in user's name (default: "Admin User")
        user_email: User's email
        user_image_url: LinkedIn or profile image URL
    
    Returns:
        HTML string for sidebar
    """
    
    def is_active(page):
        return "active" if page == active_page else ""
    
    # Generate user initials for fallback
    initials = ''.join([n[0].upper() for n in user_name.split()[:2]]) if user_name else 'AD'
    avatar_html = f'<img src="{user_image_url}" alt="{user_name}" onerror="this.style.display=\'none\'; this.parentElement.textContent=\'{initials}\';">' if user_image_url else initials
    
    return f"""
    <div class="sidebar" id="sidebar">
        <!-- Sidebar Header -->
        <div class="sidebar-header">
            <div class="sidebar-logo">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                    <path d="M2 17l10 5 10-5"/>
                    <path d="M2 12l10 5 10-5"/>
                </svg>
                Disruptive Ventures
            </div>
            <div class="sidebar-subtitle">Admin Command Center</div>
        </div>
        
        <!-- Admin Warning - NO COLORED ICONS -->
        <div class="sidebar-warning">
            <div class="sidebar-warning-title">Admin Only</div>
            <div>Partners & administrators only. Team uses Google & Linear.</div>
        </div>
        
        <!-- Navigation -->
        <div class="sidebar-nav">
            <!-- People & Activity -->
            <div style="margin-bottom: 16px;">
                <a href="/wheels/people" class="sidebar-nav-item {is_active('people')}">
                    <svg class="sidebar-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                        <circle cx="9" cy="7" r="4"/>
                        <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                        <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                    </svg>
                    People & Network
                </a>
                
                <a href="/dashboard-ui" class="sidebar-nav-item {is_active('dashboard')}" style="padding-left: 36px;">
                    <svg class="sidebar-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="width: 14px; height: 14px;">
                        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                    </svg>
                    Activity Dashboard
                </a>
                
                <a href="/knowledge/" class="sidebar-nav-item {is_active('knowledge')}" style="padding-left: 36px;">
                    <svg class="sidebar-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="width: 14px; height: 14px;">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                        <circle cx="9" cy="7" r="4"/>
                    </svg>
                    People
                </a>
                
                <a href="/wheels/people/docs" class="sidebar-nav-item {is_active('people-docs')}" style="padding-left: 36px;">
                    <svg class="sidebar-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="width: 14px; height: 14px;">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <polyline points="14 2 14 8 20 8"/>
                    </svg>
                    Docs
                </a>
            </div>
            
            <!-- Deal Flow with Submenus -->
            <div style="margin-bottom: 16px;">
                <a href="/wheels/dealflow" class="sidebar-nav-item {is_active('dealflow')}">
                    <svg class="sidebar-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                        <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                        <line x1="12" y1="22.08" x2="12" y2="12"/>
                    </svg>
                    Deal Flow
                </a>
                
                <a href="/wheels/dealflow/leads" class="sidebar-nav-item {is_active('leads')}" style="padding-left: 36px;">
                    <svg class="sidebar-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="width: 14px; height: 14px;">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="12" y1="8" x2="12" y2="12"/>
                        <line x1="12" y1="16" x2="12.01" y2="16"/>
                    </svg>
                    Leads
                </a>
                
                <a href="/wheels/dealflow/deals" class="sidebar-nav-item {is_active('deals')}" style="padding-left: 36px;">
                    <svg class="sidebar-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="width: 14px; height: 14px;">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                        <line x1="9" y1="9" x2="15" y2="15"/>
                        <line x1="15" y1="9" x2="9" y2="15"/>
                    </svg>
                    Deals
                </a>
                
                <a href="/wheels/dealflow/docs" class="sidebar-nav-item {is_active('dealflow-docs')}" style="padding-left: 36px;">
                    <svg class="sidebar-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="width: 14px; height: 14px;">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <polyline points="14 2 14 8 20 8"/>
                    </svg>
                    Docs
                </a>
            </div>
            
            <a href="/wheels/building" class="sidebar-nav-item {is_active('building')}">
                <svg class="sidebar-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                    <polyline points="9 22 9 12 15 12 15 22"/>
                </svg>
                Building Companies
            </a>
            
            <a href="/wheels/admin" class="sidebar-nav-item {is_active('admin')}">
                <svg class="sidebar-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                    <line x1="3" y1="9" x2="21" y2="9"/>
                    <line x1="9" y1="21" x2="9" y2="9"/>
                </svg>
                Portfolio Dashboard
            </a>
            
            <!-- SEPARATOR -->
            <div style="height: 1px; background: var(--gray-200); margin: 16px 12px;"></div>
            
            <!-- Quick Access -->
            <div style="font-size: 11px; color: var(--gray-500); padding: 0 12px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">Quick Access</div>
            
            <a href="/upload-ui" class="sidebar-nav-item {is_active('upload')}">
                <svg class="sidebar-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="17 8 12 3 7 8"/>
                    <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                Upload Files
            </a>
            
            <a href="/user-integrations/settings" class="sidebar-nav-item {is_active('settings')}">
                <svg class="sidebar-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="3"/>
                    <path d="M12 1v6m0 6v6M4.2 4.2l4.2 4.2m5.6 5.6l4.2 4.2M1 12h6m6 0h6M4.2 19.8l4.2-4.2m5.6-5.6l4.2-4.2"/>
                </svg>
                Settings
            </a>
        </div>
        
        <!-- Footer -->
        <div class="sidebar-footer">
            <!-- Dark Mode Toggle -->
            <button class="dark-mode-toggle" onclick="toggleDarkMode()">
                <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                </svg>
                <span id="dark-mode-label">Dark Mode</span>
            </button>
            
            <!-- User Profile -->
            <div style="padding: 12px; border: 1px solid var(--gray-200); border-radius: 8px; background: var(--gray-50); margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div class="user-avatar">{avatar_html}</div>
                    <div style="flex: 1; min-width: 0;">
                        <div style="font-size: 13px; font-weight: 600; color: var(--gray-900); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                            {user_name}
                        </div>
                        {f'<div style="font-size: 11px; color: var(--gray-500); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{user_email}</div>' if user_email else ''}
                    </div>
                </div>
            </div>
            
            <div style="margin-bottom: 8px; font-weight: 500; color: var(--gray-700); font-size: 11px;">System Status</div>
            <div style="margin-bottom: 4px; font-size: 11px;">Most team members use:</div>
            <div style="margin-bottom: 2px; font-size: 11px;">• Google Workspace</div>
            <div style="font-size: 11px;">• Linear</div>
        </div>
    </div>
    
    <!-- Sidebar Toggle Button (slides with sidebar) -->
    <button class="sidebar-toggle" onclick="toggleSidebar()" aria-label="Toggle sidebar">
        <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <polyline points="15 18 9 12 15 6"/>
        </svg>
    </button>
    
    <script>
        // Toggle sidebar (pushes content like Claude)
        function toggleSidebar() {{
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('collapsed');
            localStorage.setItem('sidebar-collapsed', sidebar.classList.contains('collapsed'));
        }}
        
        // Auto dark mode based on sunset/sunrise
        function shouldBeDarkMode() {{
            const hour = new Date().getHours();
            // Dark mode: 6 PM (18:00) to 6 AM (06:00)
            return hour >= 18 || hour < 6;
        }}
        
        // Toggle dark mode (with auto-detection)
        function toggleDarkMode() {{
            const manualOverride = localStorage.getItem('dark-mode-manual');
            
            if (manualOverride !== null) {{
                // User has manually toggled - remove override and go back to auto
                localStorage.removeItem('dark-mode-manual');
                applyDarkMode(shouldBeDarkMode());
            }} else {{
                // User is toggling for first time - set manual override
                const currentlyDark = document.body.classList.contains('dark-mode');
                const newState = !currentlyDark;
                localStorage.setItem('dark-mode-manual', newState);
                applyDarkMode(newState);
            }}
        }}
        
        function applyDarkMode(isDark) {{
            if (isDark) {{
                document.body.classList.add('dark-mode');
            }} else {{
                document.body.classList.remove('dark-mode');
            }}
            const label = document.getElementById('dark-mode-label');
            if (label) label.textContent = isDark ? 'Light Mode' : 'Dark Mode';
        }}
        
        // Initialize on page load
        window.addEventListener('load', () => {{
            // Restore sidebar state
            const sidebarCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
            if (sidebarCollapsed) {{
                document.getElementById('sidebar')?.classList.add('collapsed');
            }}
            
            // Auto dark mode based on time (or manual override)
            const manualOverride = localStorage.getItem('dark-mode-manual');
            if (manualOverride !== null) {{
                // User has manually set preference
                applyDarkMode(manualOverride === 'true');
            }} else {{
                // Auto-detect based on time
                applyDarkMode(shouldBeDarkMode());
            }}
        }});
        
        // Check time every minute and auto-switch (only if no manual override)
        setInterval(() => {{
            const manualOverride = localStorage.getItem('dark-mode-manual');
            if (manualOverride === null) {{
                // No manual override - auto-switch based on time
                applyDarkMode(shouldBeDarkMode());
            }}
        }}, 60000);  // Check every minute
    </script>
    """


