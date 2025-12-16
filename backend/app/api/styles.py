"""
Disruptive Ventures Brand Styles
Colors, fonts, and styling from https://www.disruptiveventures.se
"""

DV_STYLES = """
<style>
    /* Disruptive Ventures Brand Colors - Updated */
    :root {
        /* Primary Nordic VC colors - clean, professional, trustworthy */
        --dv-primary: #0A2540;        /* Deep navy blue - headers */
        --dv-secondary: #425466;      /* Slate gray - secondary text */
        --dv-accent: #635BFF;         /* Vibrant purple-blue - CTAs/links */
        --dv-highlight: #00D4FF;      /* Cyan - highlights/progress */
        --dv-background: #FFFFFF;     /* White background */
        --dv-gray-50: #F7FAFC;        /* Light gray backgrounds */
        --dv-gray-100: #EDF2F7;       /* Subtle borders */
        --dv-success: #00C48C;        /* Green - success states */
        --dv-warning: #FFA726;        /* Orange - warnings */
        --dv-light-bg: #f8f9fa;       /* Light gray background */
        --dv-border: #e0e0e0;         /* Border color */
        
        /* Semantic colors */
        --dv-success: #28a745;
        --dv-warning: #ff9800;
        --dv-danger: #dc3545;
        --dv-info: #17a2b8;
    }
    
    /* Typography - Professional VC firm style */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
        background: var(--dv-light-bg);
        color: var(--dv-primary);
        line-height: 1.6;
        font-size: 16px;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-weight: 600;
        color: var(--dv-primary);
        letter-spacing: -0.5px;
    }
    
    h1 {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 10px;
    }
    
    h2 {
        font-size: 28px;
        margin-bottom: 20px;
    }
    
    h3 {
        font-size: 20px;
        margin-bottom: 15px;
    }
    
    /* Header - DV Style */
    .header {
        background: var(--dv-primary);
        color: white;
        padding: 40px 30px;
        border-bottom: 4px solid var(--dv-highlight);
    }
    
    .header h1 {
        color: white;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 10px;
    }
    
    .header p {
        color: rgba(255,255,255,0.9);
        font-size: 16px;
    }
    
    .header-meta {
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
        margin-top: 15px;
        font-size: 14px;
        opacity: 0.9;
    }
    
    /* Navigation */
    .nav {
        background: white;
        padding: 15px 30px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        display: flex;
        gap: 15px;
        align-items: center;
    }
    
    .nav a, .nav button {
        padding: 10px 20px;
        text-decoration: none;
        color: var(--dv-primary);
        font-weight: 600;
        border-radius: 6px;
        transition: all 0.3s;
        font-size: 14px;
        border: none;
        background: transparent;
        cursor: pointer;
    }
    
    .nav a:hover, .nav button:hover {
        background: var(--dv-light-bg);
        color: var(--dv-accent);
    }
    
    .nav .btn-primary {
        background: var(--dv-highlight);
        color: white;
        margin-left: auto;
    }
    
    .nav .btn-primary:hover {
        background: #e55a2a;
        color: white;
    }
    
    .nav .btn-secondary {
        background: var(--dv-accent);
        color: white;
    }
    
    .nav .btn-secondary:hover {
        background: #0052a3;
        color: white;
    }
    
    /* Container */
    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 40px 30px;
    }
    
    /* Cards - Professional style */
    .card {
        background: white;
        border-radius: 8px;
        padding: 30px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 4px solid var(--dv-accent);
        transition: all 0.3s;
    }
    
    .card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .section {
        margin-bottom: 50px;
    }
    
    .section-title {
        font-size: 24px;
        font-weight: 700;
        color: var(--dv-primary);
        margin-bottom: 25px;
        padding-bottom: 10px;
        border-bottom: 2px solid var(--dv-border);
    }
    
    /* Info Grid */
    .info-grid {
        display: grid;
        grid-template-columns: 200px 1fr;
        gap: 20px;
        margin-bottom: 15px;
    }
    
    .info-label {
        font-weight: 600;
        color: var(--dv-secondary);
    }
    
    .info-value {
        color: var(--dv-primary);
    }
    
    /* Decisions - Success color */
    .decision {
        padding: 25px;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-left: 4px solid var(--dv-accent);
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
    .decision-text {
        font-size: 18px;
        font-weight: 600;
        color: var(--dv-primary);
        margin-bottom: 10px;
    }
    
    .decision-meta {
        font-size: 14px;
        color: var(--dv-secondary);
        margin-top: 10px;
    }
    
    /* Action Items - Warning color */
    .action-item {
        padding: 25px;
        background: linear-gradient(135deg, #fff8f0 0%, #ffe8d6 100%);
        border-left: 4px solid var(--dv-highlight);
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
    .action-text {
        font-size: 18px;
        font-weight: 600;
        color: var(--dv-primary);
        margin-bottom: 10px;
    }
    
    .action-meta {
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
        font-size: 14px;
        color: var(--dv-secondary);
        margin-top: 10px;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-high {
        background: var(--dv-danger);
        color: white;
    }
    
    .badge-medium {
        background: var(--dv-warning);
        color: white;
    }
    
    .badge-low {
        background: var(--dv-info);
        color: white;
    }
    
    .badge-open {
        background: var(--dv-light-bg);
        color: var(--dv-secondary);
        border: 1px solid var(--dv-border);
    }
    
    .badge-in_progress {
        background: var(--dv-info);
        color: white;
    }
    
    .badge-done {
        background: var(--dv-success);
        color: white;
    }
    
    /* Attendee list */
    .attendee {
        padding: 15px 20px;
        background: white;
        border-radius: 6px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 15px;
        border: 1px solid var(--dv-border);
        transition: all 0.2s;
    }
    
    .attendee:hover {
        border-color: var(--dv-accent);
        box-shadow: 0 2px 8px rgba(0,102,204,0.1);
    }
    
    .attendee-name {
        font-weight: 600;
        color: var(--dv-primary);
        font-size: 16px;
    }
    
    .attendee-role {
        padding: 4px 12px;
        background: var(--dv-light-bg);
        color: var(--dv-secondary);
        border-radius: 4px;
        font-size: 13px;
        margin-left: auto;
    }
    
    /* Stats cards */
    .stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 20px;
        margin-bottom: 40px;
    }
    
    .stat-card {
        background: white;
        padding: 30px;
        border-radius: 8px;
        text-align: center;
        border-top: 4px solid var(--dv-accent);
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    .stat-number {
        font-size: 48px;
        font-weight: 700;
        color: var(--dv-accent);
        margin-bottom: 10px;
    }
    
    .stat-label {
        color: var(--dv-secondary);
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    /* Buttons */
    .btn {
        display: inline-block;
        padding: 12px 24px;
        border-radius: 6px;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.3s;
        border: none;
        cursor: pointer;
        font-size: 14px;
    }
    
    .btn-primary {
        background: var(--dv-highlight);
        color: white;
    }
    
    .btn-primary:hover {
        background: #e55a2a;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255,107,53,0.3);
    }
    
    .btn-secondary {
        background: var(--dv-accent);
        color: white;
    }
    
    .btn-secondary:hover {
        background: #0052a3;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,102,204,0.3);
    }
    
    .btn-outline {
        background: white;
        color: var(--dv-accent);
        border: 2px solid var(--dv-accent);
    }
    
    .btn-outline:hover {
        background: var(--dv-accent);
        color: white;
    }
    
    /* Document generation cards */
    .doc-card {
        background: white;
        border-radius: 8px;
        padding: 25px;
        border-left: 4px solid var(--dv-accent);
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: all 0.3s;
    }
    
    .doc-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .doc-card h3 {
        margin: 0 0 10px 0;
        color: var(--dv-primary);
        font-size: 18px;
    }
    
    .doc-card p {
        font-size: 14px;
        color: var(--dv-secondary);
        margin-bottom: 15px;
    }
    
    /* Key points list */
    .key-points {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .key-points li {
        padding: 18px 20px;
        background: white;
        border-left: 4px solid var(--dv-accent);
        border-radius: 6px;
        margin-bottom: 12px;
        padding-left: 50px;
        position: relative;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        transition: all 0.3s;
        font-size: 15px;
        line-height: 1.7;
        color: var(--dv-primary);
    }
    
    .key-points li:hover {
        box-shadow: 0 4px 12px rgba(0,102,204,0.15);
        transform: translateX(5px);
    }
    
    .key-points li:before {
        content: "→";
        position: absolute;
        left: 20px;
        color: var(--dv-accent);
        font-weight: bold;
        font-size: 20px;
    }
    
    /* Topics/Tags */
    .topic-badge {
        display: inline-block;
        padding: 8px 16px;
        background: white;
        color: var(--dv-accent);
        border: 1px solid var(--dv-accent);
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        margin: 5px;
        transition: all 0.3s;
    }
    
    .topic-badge:hover {
        background: var(--dv-accent);
        color: white;
    }
    
    /* Source info banner */
    .source-info {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 30px;
        border-left: 4px solid var(--dv-accent);
    }
    
    .source-info strong {
        color: var(--dv-primary);
        font-weight: 700;
    }
    
    /* Empty states */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: var(--dv-secondary);
    }
    
    .empty-state-icon {
        font-size: 64px;
        margin-bottom: 20px;
        opacity: 0.5;
    }
    
    .empty-state-title {
        font-size: 24px;
        color: var(--dv-secondary);
        margin-bottom: 10px;
        font-weight: 600;
    }
    
    /* Logo area */
    .logo {
        font-size: 24px;
        font-weight: 700;
        color: white;
        text-decoration: none;
    }
    
    .logo-accent {
        color: var(--dv-highlight);
    }
    
    /* Professional spacing */
    .template {
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        padding: 40px;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .container {
            padding: 20px 15px;
        }
        
        .header {
            padding: 30px 20px;
        }
        
        .info-grid {
            grid-template-columns: 1fr;
            gap: 10px;
        }
        
        .stats {
            grid-template-columns: 1fr 1fr;
        }
    }
</style>
"""

def get_dv_styles():
    """Get Disruptive Ventures brand styles."""
    return DV_STYLES



