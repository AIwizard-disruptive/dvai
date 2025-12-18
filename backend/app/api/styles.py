"""
Disruptive Ventures Brand Styles - Claude-Inspired Minimalistic Design
Clean, minimal interface matching the new frontend design system
"""

DV_STYLES = """
<style>
    /* Claude-Inspired Minimalistic Color System */
    :root {
        /* Grayscale Foundation */
        --gray-900: #1a1a1a;          /* Text primary */
        --gray-700: #374151;          /* Text secondary */
        --gray-600: #666666;          /* Text tertiary */
        --gray-500: #808080;          /* Text muted */
        --gray-300: #d1d5db;          /* Borders light */
        --gray-200: #e5e5e5;          /* Borders */
        --gray-100: #f5f5f5;          /* Backgrounds light */
        --gray-50: #fafafa;           /* Backgrounds subtle */
        
        /* Wheel Accent Colors (from frontend) */
        --blue-600: #2563eb;          /* People */
        --blue-50: #eff6ff;           /* People bg */
        --green-600: #16a34a;         /* Dealflow */
        --green-50: #f0fdf4;          /* Dealflow bg */
        --purple-600: #9333ea;        /* Portfolio */
        --purple-50: #faf5ff;         /* Portfolio bg */
        --amber-600: #d97706;         /* Admin/Warning */
        --amber-50: #fffbeb;          /* Admin bg */
        
        /* Semantic Colors */
        --success: #16a34a;
        --warning: #d97706;
        --danger: #dc2626;
        --info: #2563eb;
    }
    
    /* Global Reset & Base Styles */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
        background: #ffffff;
        color: var(--gray-900);
        line-height: 1.6;
        font-size: 14px;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* Typography - Clean & Minimal */
    h1, h2, h3, h4, h5, h6 {
        font-weight: 600;
        color: var(--gray-900);
        letter-spacing: -0.01em;
        line-height: 1.2;
    }
    
    h1 {
        font-size: 30px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    h2 {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 16px;
    }
    
    h3 {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 12px;
    }
    
    p {
        color: var(--gray-600);
        font-size: 14px;
        line-height: 1.6;
    }
    
    a {
        color: var(--gray-900);
        text-decoration: none;
    }
    
    /* Dark Mode Colors - Complete Styling */
    body.dark-mode {
        background: #1a1a1a;
        color: #e5e5e5;
    }
    
    body.dark-mode .sidebar {
        background: #2a2a2a;
        border-right-color: #404040;
    }
    
    body.dark-mode .sidebar-header {
        border-bottom-color: #333333;
    }
    
    body.dark-mode .sidebar-subtitle {
        color: #e5e5e5;
    }
    
    body.dark-mode .sidebar-nav-item {
        color: #999999;
    }
    
    body.dark-mode .sidebar-nav-item:hover {
        background: #333333;
        color: #e5e5e5;
    }
    
    body.dark-mode .sidebar-nav-item.active {
        background: #333333;
        color: #e5e5e5;
    }
    
    body.dark-mode .sidebar-icon {
        color: #999999;
    }
    
    body.dark-mode .admin-alert-content {
        background: rgba(45, 36, 22, 0.95);
        border-color: rgba(217, 119, 6, 0.5);
    }

    body.dark-mode .admin-alert-close {
        color: #fbbf24;
    }
    
    body.dark-mode .admin-alert-close:hover {
        background: rgba(255, 255, 255, 0.05);
    }
    
    body.dark-mode .sidebar-footer {
        border-top-color: #333333;
        color: #999999;
    }
    
    body.dark-mode .sidebar-footer > div {
        background: #333333 !important;
        border-color: #404040 !important;
    }
    
    body.dark-mode .user-avatar {
        background: #404040;
        color: #999999;
    }
    
    body.dark-mode .user-name {
        color: #e5e5e5;
    }
    
    body.dark-mode .user-role {
        color: #808080;
    }
    
    body.dark-mode .sidebar-footer > div div {
        color: #999999 !important;
    }
    
    body.dark-mode .sidebar-footer > div div:first-child {
        color: #e5e5e5 !important;
    }
    
    body.dark-mode .main-content {
        background: #1a1a1a;
    }
    
    body.dark-mode .page-header {
        border-bottom-color: #333333;
        background: #1a1a1a;
    }
    
    body.dark-mode .page-title,
    body.dark-mode .item-title,
    body.dark-mode .doc-title,
    body.dark-mode .meeting-title,
    body.dark-mode .profile-name,
    body.dark-mode .category-title,
    body.dark-mode h1, body.dark-mode h2, body.dark-mode h3 {
        color: #e5e5e5;
    }
    
    body.dark-mode .page-description,
    body.dark-mode .item-meta,
    body.dark-mode .doc-meta,
    body.dark-mode .stat-label,
    body.dark-mode .section-heading,
    body.dark-mode p {
        color: #999999;
    }
    
    body.dark-mode .item-card,
    body.dark-mode .stat-card,
    body.dark-mode .integration-card,
    body.dark-mode .test-card,
    body.dark-mode .doc-card,
    body.dark-mode .person-card,
    body.dark-mode .policy-card,
    body.dark-mode .meeting-card,
    body.dark-mode .card {
        background: #2a2a2a;
        border-color: #404040;
        color: #e5e5e5;
    }
    
    body.dark-mode .item-card:hover,
    body.dark-mode .stat-card:hover,
    body.dark-mode .doc-card:hover,
    body.dark-mode .person-card:hover {
        border-color: #4a4a4a;
        box-shadow: 0 1px 3px rgba(255,255,255,0.05);
    }
    
    body.dark-mode .badge,
    body.dark-mode .policy-tag,
    body.dark-mode .category-count {
        background: #404040;
        color: #cccccc;
    }
    
    body.dark-mode .btn-primary {
        background: #e5e5e5;
        color: #1a1a1a;
    }
    
    body.dark-mode .btn-primary:hover {
        background: #cccccc;
    }
    
    body.dark-mode .btn-secondary {
        background: #2a2a2a;
        color: #e5e5e5;
        border-color: #404040;
    }
    
    body.dark-mode .btn-secondary:hover {
        background: #333333;
        border-color: #4a4a4a;
    }
    
    body.dark-mode .tab,
    body.dark-mode .dashboard-tab,
    body.dark-mode .nav-tab {
        color: #999999;
        border-bottom-color: transparent;
    }
    
    body.dark-mode .tab:hover,
    body.dark-mode .dashboard-tab:hover {
        background: #333333;
        color: #e5e5e5;
    }
    
    body.dark-mode .tab.active,
    body.dark-mode .dashboard-tab.active {
        background: transparent;
        color: #e5e5e5;
        border-bottom-color: #e5e5e5;
    }
    
    body.dark-mode .view-toggle {
        background: #2a2a2a;
        border-color: #404040;
    }
    
    body.dark-mode .view-toggle-btn {
        color: #999999;
    }
    
    body.dark-mode .view-toggle-btn:hover {
        background: #333333;
        color: #e5e5e5;
    }
    
    body.dark-mode .view-toggle-btn.active {
        background: #333333;
        color: #e5e5e5;
    }
    
    body.dark-mode .category-header {
        border-bottom-color: #333333;
        color: #e5e5e5;
    }
    
    body.dark-mode .doc-icon,
    body.dark-mode .integration-icon,
    body.dark-mode .person-avatar {
        background: #404040;
    }
    
    body.dark-mode .doc-icon svg,
    body.dark-mode .integration-icon svg {
        stroke: #999999;
    }
    
    body.dark-mode .empty-state {
        color: #808080;
    }
    
    body.dark-mode .empty-state-title {
        color: #999999;
    }
    
    body.dark-mode a {
        color: #e5e5e5;
    }
    
    body.dark-mode a:hover {
        color: #ffffff;
    }
    
    body.dark-mode input,
    body.dark-mode textarea,
    body.dark-mode select {
        background: #2a2a2a;
        border-color: #404040;
        color: #e5e5e5;
    }
    
    body.dark-mode .upload-area {
        background: #2a2a2a;
        border-color: #404040;
    }
    
    body.dark-mode .upload-area:hover {
        border-color: #4a4a4a;
        background: #333333;
    }
    
    /* Dark mode kanban filters */
    body.dark-mode .filter-btn {
        background: #2a2a2a;
        border-color: #404040;
        color: #999999;
    }
    
    body.dark-mode .filter-btn:hover {
        background: #333333;
        color: #e5e5e5;
    }
    
    body.dark-mode .filter-btn.active {
        background: #e5e5e5;
        color: #1a1a1a;
        border-color: #e5e5e5;
    }
    
    body.dark-mode .sync-status {
        background: #333333;
        color: #999999;
    }
    
    /* Dark mode timeline */
    body.dark-mode .view-switcher {
        background: #2a2a2a;
        border-color: #404040;
    }
    
    body.dark-mode .view-switcher-btn {
        color: #999999;
    }
    
    body.dark-mode .view-switcher-btn:hover {
        background: #333333;
        color: #e5e5e5;
    }
    
    body.dark-mode .view-switcher-btn.active {
        background: #333333;
        color: #e5e5e5;
    }
    
    body.dark-mode .timeline-header {
        border-bottom-color: #404040;
    }
    
    body.dark-mode .timeline-month {
        color: #cccccc;
    }
    
    body.dark-mode .timeline-task {
        border-bottom-color: #333333;
    }
    
    body.dark-mode .timeline-task-info {
        color: #e5e5e5;
    }
    
    body.dark-mode .timeline-task-name {
        color: #e5e5e5;
    }
    
    body.dark-mode .timeline-task-meta {
        color: #999999;
    }
    
    body.dark-mode .timeline-bar-container {
        background: #2a2a2a;
    }
    
    body.dark-mode .timeline-bar {
        background: #e5e5e5;
        color: #1a1a1a;
    }
    
    body.dark-mode .timeline-bar:hover {
        background: #cccccc;
    }
    
    /* Info boxes */
    .info-box {
        background: white;
        border: 1px solid var(--gray-200);
        border-radius: 8px;
        padding: 16px;
    }
    
    /* Dark mode for info boxes */
    body.dark-mode .info-box {
        background: #2a2a2a !important;
        border-color: #404040 !important;
    }
    
    body.dark-mode .info-box p {
        color: #999999 !important;
    }
    
    body.dark-mode .info-box strong {
        color: #e5e5e5 !important;
    }
    
    body.dark-mode .info-box h3 {
        color: #e5e5e5 !important;
    }
    
    /* Sidebar Layout - Claude Style with Toggle */
    .sidebar {
        position: fixed;
        top: 0;
        left: 0;
        width: 280px;
        height: 100vh;
        background: #ffffff;
        border-right: 1px solid var(--gray-200);
        display: flex;
        flex-direction: column;
        z-index: 1000;
        transition: transform 0.3s ease;
    }
    
    .sidebar.collapsed {
        transform: translateX(-280px);
    }
    
    .sidebar-header {
        padding: 20px;
        border-bottom: 1px solid var(--gray-100);
    }
    
    .sidebar-header img {
        max-width: 100%;
        height: auto;
    }
    
    .sidebar-subtitle {
        font-size: 11px;
        color: var(--gray-500);
        font-weight: 400;
    }
    
    .sidebar-nav {
        flex: 1;
        padding: 16px;
        overflow-y: auto;
    }
    
    .sidebar-nav-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 12px;
        border-radius: 6px;
        color: var(--gray-700);
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.15s;
        text-decoration: none;
        margin-bottom: 4px;
    }
    
    .sidebar-nav-item:hover {
        background: var(--gray-100);
        color: var(--gray-900);
    }
    
    .sidebar-nav-item.active {
        background: var(--gray-100);
        color: var(--gray-900);
    }
    
    .sidebar-icon {
        width: 18px;
        height: 18px;
        color: var(--gray-600);
        flex-shrink: 0;
    }
    
    .sidebar-nav-item:hover .sidebar-icon {
        color: var(--gray-700);
    }
    
    .sidebar-footer {
        padding: 16px;
        border-top: 1px solid var(--gray-100);
        font-size: 11px;
        color: var(--gray-500);
    }
    
    /* Dark Mode Toggle */
    .dark-mode-toggle {
        padding: 8px 12px;
        background: var(--gray-100);
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 11px;
        font-weight: 500;
        color: var(--gray-700);
        margin: 8px 16px;
        transition: all 0.15s;
        display: flex;
        align-items: center;
        gap: 8px;
        width: calc(100% - 32px);
        justify-content: center;
    }
    
    .dark-mode-toggle:hover {
        background: var(--gray-200);
    }
    
    .dark-mode-toggle svg {
        width: 14px;
        height: 14px;
        stroke: currentColor;
    }
    
    body.dark-mode .dark-mode-toggle {
        background: #404040;
        color: #e5e5e5;
        border: 1px solid #4a4a4a;
    }
    
    body.dark-mode .dark-mode-toggle:hover {
        background: #4a4a4a;
        border-color: #555555;
    }
    
    /* Admin Alert - Floating notification */
    .admin-alert {
        position: fixed;
        top: 16px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 10000;
        max-width: 440px;
        width: calc(100% - 32px);
    }
    
    .admin-alert-content {
        background: #fffbeb;
        border: 1px solid #fbbf24;
        border-radius: 8px;
        padding: 16px;
        display: flex;
        align-items: start;
        gap: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .admin-alert-close {
        background: transparent;
        border: none;
        cursor: pointer;
        padding: 4px;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #92400e;
        transition: background 0.15s;
    }
    
    .admin-alert-close:hover {
        background: rgba(0, 0, 0, 0.05);
    }
    
    /* Animations */
    @keyframes slideInFromTop {
        from {
            transform: translate(-50%, -100%);
            opacity: 0;
        }
        to {
            transform: translate(-50%, 0);
            opacity: 1;
        }
    }
    
    @keyframes fadeOut {
        from {
            opacity: 1;
        }
        to {
            opacity: 0;
        }
    }
    
    /* Sidebar Toggle Button - Clean icon only, positioned at sidebar edge */
    .sidebar-toggle {
        position: fixed;
        top: 24px;
        left: 288px;
        z-index: 1001;
        padding: 0;
        background: transparent;
        border: none;
        cursor: pointer;
        transition: left 0.3s ease, opacity 0.15s;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0.6;
    }
    
    .sidebar-toggle:hover {
        opacity: 1;
    }
    
    .sidebar-toggle svg {
        width: 20px;
        height: 20px;
        stroke: var(--gray-600);
        transition: transform 0.3s ease;
    }
    
    /* When sidebar is collapsed, button moves left and rotates */
    .sidebar.collapsed ~ .sidebar-toggle {
        left: 16px;
    }
    
    /* Rotate icon when collapsed */
    .sidebar.collapsed ~ .sidebar-toggle svg {
        transform: rotate(180deg);
    }
    
    body.dark-mode .sidebar-toggle svg {
        stroke: var(--gray-400);
    }
    
    body.dark-mode .sidebar-toggle:hover {
        opacity: 1;
    }
    
    body.dark-mode .sidebar-toggle:hover svg {
        stroke: var(--gray-300);
    }
    
    /* Main Content Area */
    .main-content {
        margin-left: 280px;
        min-height: 100vh;
        background: #ffffff;
        transition: margin-left 0.3s ease;
    }
    
    .sidebar.collapsed ~ .main-content {
        margin-left: 0;
    }
    
    .page-header {
        padding: 32px;
        border-bottom: 1px solid var(--gray-200);
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
    }
    
    .page-header-left {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    .page-title {
        font-size: 24px;
        font-weight: 600;
        color: var(--gray-900);
        margin-bottom: 8px;
    }
    
    .page-description {
        font-size: 14px;
        color: var(--gray-600);
    }
    
    /* User Profile - Top Right */
    .user-profile {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 12px;
        border-radius: 8px;
        border: 1px solid var(--gray-200);
        background: white;
        cursor: pointer;
        transition: all 0.15s;
    }
    
    .user-profile:hover {
        background: var(--gray-50);
        border-color: var(--gray-300);
    }
    
    .user-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: var(--gray-200);
        color: var(--gray-600);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: 600;
        overflow: hidden;
    }
    
    .user-avatar img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    .user-info {
        text-align: right;
    }
    
    .user-name {
        font-size: 13px;
        font-weight: 500;
        color: var(--gray-900);
    }
    
    .user-role {
        font-size: 11px;
        color: var(--gray-500);
    }
    
    /* View Toggle - List/Card Switch */
    .view-toggle {
        display: flex;
        gap: 4px;
        background: white;
        border: 1px solid var(--gray-200);
        border-radius: 6px;
        padding: 4px;
    }
    
    .view-toggle-btn {
        padding: 6px 8px;
        border: none;
        background: transparent;
        color: var(--gray-600);
        cursor: pointer;
        border-radius: 4px;
        transition: all 0.15s;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .view-toggle-btn:hover {
        background: var(--gray-100);
        color: var(--gray-900);
    }
    
    .view-toggle-btn.active {
        background: var(--gray-100);
        color: var(--gray-900);
    }
    
    .view-toggle-btn svg {
        width: 16px;
        height: 16px;
        stroke: currentColor;
    }
    
    /* Section Header with Toggle */
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }
    
    .section-header h2 {
        font-size: 14px;
        font-weight: 600;
        color: var(--gray-900);
        margin: 0;
    }
    
    /* List View Styles */
    .list-view {
        display: block;
    }
    
    .list-view .item-card,
    .list-view .person-card,
    .list-view .meeting-card {
        display: block;
    }
    
    /* Card/Grid View Styles */
    .card-view {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 16px;
    }
    
    .card-view.three-col {
        grid-template-columns: repeat(3, 1fr);
    }
    
    @media (max-width: 1024px) {
        .card-view.three-col {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (max-width: 640px) {
        .card-view, .card-view.three-col {
            grid-template-columns: 1fr;
        }
    }
    
    /* Container */
    .container {
        max-width: 1280px;
        margin: 0 auto;
        padding: 32px;
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .sidebar {
            transform: translateX(-100%);
            transition: transform 0.3s;
        }
        
        .sidebar.open {
            transform: translateX(0);
        }
        
        .main-content {
            margin-left: 0;
        }
    }
    
    /* Cards - Minimal Style */
    .card {
        background: white;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        border: 1px solid var(--gray-200);
        transition: all 0.15s;
    }
    
    .card:hover {
        border-color: var(--gray-300);
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .section {
        margin-bottom: 32px;
    }
    
    .section-title {
        font-size: 14px;
        font-weight: 500;
        color: var(--gray-700);
        margin-bottom: 16px;
        text-transform: none;
    }
    
    /* Info Grid */
    .info-grid {
        display: grid;
        grid-template-columns: 140px 1fr;
        gap: 12px;
        margin-bottom: 12px;
    }
    
    .info-label {
        font-weight: 500;
        color: var(--gray-600);
        font-size: 13px;
    }
    
    .info-value {
        color: var(--gray-900);
        font-size: 13px;
    }
    
    /* Decisions - Minimal */
    .decision {
        padding: 16px;
        background: var(--blue-50);
        border: 1px solid #dbeafe;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    
    .decision-text {
        font-size: 14px;
        font-weight: 500;
        color: var(--gray-900);
        margin-bottom: 8px;
    }
    
    .decision-meta {
        font-size: 12px;
        color: var(--gray-600);
        margin-top: 8px;
    }
    
    /* Action Items - Minimal */
    .action-item {
        padding: 16px;
        background: white;
        border: 1px solid var(--gray-200);
        border-radius: 8px;
        margin-bottom: 12px;
    }
    
    .action-text {
        font-size: 14px;
        font-weight: 500;
        color: var(--gray-900);
        margin-bottom: 8px;
    }
    
    .action-meta {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        font-size: 12px;
        color: var(--gray-600);
        margin-top: 8px;
    }
    
    /* Badges - Minimal */
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 500;
        text-transform: none;
        letter-spacing: 0;
    }
    
    .badge-high {
        background: #fee2e2;
        color: #991b1b;
    }
    
    .badge-medium {
        background: #fed7aa;
        color: #92400e;
    }
    
    .badge-low {
        background: #dbeafe;
        color: #1e40af;
    }
    
    .badge-open {
        background: var(--gray-100);
        color: var(--gray-700);
        border: none;
    }
    
    .badge-in_progress {
        background: #dbeafe;
        color: #1e40af;
    }
    
    .badge-done {
        background: #dcfce7;
        color: #166534;
    }
    
    /* Attendee list - Minimal */
    .attendee {
        padding: 12px 16px;
        background: white;
        border-radius: 6px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 12px;
        border: 1px solid var(--gray-200);
        transition: all 0.15s;
    }
    
    .attendee:hover {
        border-color: var(--gray-300);
    }
    
    .attendee-name {
        font-weight: 500;
        color: var(--gray-900);
        font-size: 13px;
    }
    
    .attendee-role {
        padding: 2px 8px;
        background: var(--gray-100);
        color: var(--gray-700);
        border-radius: 4px;
        font-size: 11px;
        margin-left: auto;
    }
    
    /* Stats cards - Minimal */
    .stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 32px;
    }
    
    .stat-card {
        background: white;
        padding: 16px;
        border-radius: 8px;
        text-align: left;
        border: 1px solid var(--gray-200);
    }
    
    .stat-number {
        font-size: 24px;
        font-weight: 600;
        color: var(--gray-900);
        margin-bottom: 4px;
    }
    
    .stat-label {
        color: var(--gray-600);
        font-size: 12px;
        text-transform: none;
        letter-spacing: 0;
        font-weight: 400;
    }
    
    /* Buttons - Minimal & Clean */
    .btn {
        display: inline-block;
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: 500;
        text-decoration: none;
        transition: all 0.15s;
        border: none;
        cursor: pointer;
        font-size: 13px;
    }
    
    .btn-primary {
        background: var(--gray-900);
        color: white;
    }
    
    .btn-primary:hover {
        background: var(--gray-700);
    }
    
    .btn-secondary {
        background: white;
        color: var(--gray-900);
        border: 1px solid var(--gray-200);
    }
    
    .btn-secondary:hover {
        background: var(--gray-50);
        border-color: var(--gray-300);
    }
    
    .btn-outline {
        background: transparent;
        color: var(--gray-700);
        border: 1px solid var(--gray-300);
    }
    
    .btn-outline:hover {
        background: var(--gray-50);
        border-color: var(--gray-400);
    }
    
    /* Document cards - Minimal */
    .doc-card {
        background: white;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid var(--gray-200);
        transition: all 0.15s;
    }
    
    .doc-card:hover {
        border-color: var(--gray-300);
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .doc-card h3 {
        margin: 0 0 8px 0;
        color: var(--gray-900);
        font-size: 14px;
        font-weight: 600;
    }
    
    .doc-card p {
        font-size: 13px;
        color: var(--gray-600);
        margin-bottom: 12px;
    }
    
    /* Key points list - Minimal */
    .key-points {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .key-points li {
        padding: 12px 16px;
        background: white;
        border: 1px solid var(--gray-200);
        border-radius: 6px;
        margin-bottom: 8px;
        padding-left: 36px;
        position: relative;
        transition: all 0.15s;
        font-size: 13px;
        line-height: 1.6;
        color: var(--gray-900);
    }
    
    .key-points li:hover {
        border-color: var(--gray-300);
    }
    
    .key-points li:before {
        content: "•";
        position: absolute;
        left: 16px;
        color: var(--gray-600);
        font-weight: bold;
        font-size: 16px;
    }
    
    /* Topics/Tags - Minimal */
    .topic-badge {
        display: inline-block;
        padding: 4px 10px;
        background: var(--gray-100);
        color: var(--gray-700);
        border: none;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 500;
        margin: 4px 4px 4px 0;
        transition: all 0.15s;
    }
    
    .topic-badge:hover {
        background: var(--gray-200);
    }
    
    /* Source info banner - Minimal */
    .source-info {
        background: var(--gray-50);
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 24px;
        border: 1px solid var(--gray-200);
    }
    
    .source-info strong {
        color: var(--gray-900);
        font-weight: 600;
    }
    
    /* Empty states - Minimal */
    .empty-state {
        text-align: center;
        padding: 48px 20px;
        color: var(--gray-600);
    }
    
    .empty-state-icon {
        font-size: 48px;
        margin-bottom: 16px;
        opacity: 0.3;
    }
    
    .empty-state-title {
        font-size: 16px;
        color: var(--gray-700);
        margin-bottom: 8px;
        font-weight: 500;
    }
    
    /* Logo area - Minimal */
    .logo {
        font-size: 16px;
        font-weight: 600;
        color: var(--gray-900);
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .logo-accent {
        color: var(--gray-900);
        font-weight: 600;
    }
    
    .logo-icon {
        width: 24px;
        height: 24px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border-radius: 6px;
        display: inline-block;
    }
    
    /* Template spacing - Minimal */
    .template {
        background: white;
        border-radius: 8px;
        border: 1px solid var(--gray-200);
        padding: 24px;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .container {
            padding: 16px;
        }
        
        .header {
            padding: 16px;
        }
        
        .nav {
            padding: 12px 16px;
        }
        
        .info-grid {
            grid-template-columns: 1fr;
            gap: 8px;
        }
        
        .stats {
            grid-template-columns: 1fr;
        }
        
        h1 {
            font-size: 24px;
        }
    }
</style>
"""

def get_dv_styles():
    """Get Disruptive Ventures brand styles."""
    return DV_STYLES



