"""
Document Viewer - Show generated documents on page
Then save to Google Drive as Docs/PDF
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from supabase import create_client
from app.config import settings
from app.api.styles import get_dv_styles
from datetime import datetime

router = APIRouter()


@router.get("/view/{doc_type}/{language}", response_class=HTMLResponse)
async def view_document(doc_type: str, language: str, meeting_id: str):
    """
    View generated document on page (not download).
    
    User can:
    - Read the document
    - Save to Google Drive (as Docs)
    - Save to Google Drive (as PDF)
    - Download as text
    - Copy to clipboard
    - Email to recipients
    """
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Fetch meeting data
    meeting_response = supabase.table('meetings').select('*').eq('id', meeting_id).execute()
    if not meeting_response.data:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    meeting = meeting_response.data[0]
    
    # Fetch related data
    participants = supabase.table('meeting_participants').select('people(name, email, role)').eq('meeting_id', meeting_id).execute()
    attendees = [p['people'] for p in participants.data if p.get('people')]
    
    decisions = supabase.table('decisions').select('*').eq('meeting_id', meeting_id).execute().data
    actions = supabase.table('action_items').select('*').eq('meeting_id', meeting_id).execute().data
    
    # Get metadata
    metadata = meeting.get('meeting_metadata', {}) if isinstance(meeting.get('meeting_metadata'), dict) else {}
    
    # Generate document content
    from app.api.documents import generate_document_content
    content = generate_document_content(doc_type, meeting, attendees, decisions, actions, metadata, language)
    
    # Get document title
    doc_titles = {
        'meeting_notes': 'Meeting Notes' if language == 'en' else 'Mötesanteckningar',
        'email_decision_update': 'Decision Update' if language == 'en' else 'Beslut Uppdatering',
        'email_action_reminder': 'Action Reminders' if language == 'en' else 'Åtgärdspåminnelser',
        'email_meeting_summary': 'Meeting Summary' if language == 'en' else 'Mötessammanfattning'
    }
    
    doc_title = doc_titles.get(doc_type, doc_type.replace('_', ' ').title())
    lang_flag = '🇸🇪' if language == 'sv' else '🇬🇧'
    
    html = f"""
<!DOCTYPE html>
<html lang="{language}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{doc_title} - {meeting['title']}</title>
    {get_dv_styles()}
    <style>
        .doc-viewer {{
            max-width: 900px;
            margin: 40px auto;
            padding: 0 20px;
        }}
        
        .doc-content {{
            background: white;
            padding: 60px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            min-height: 500px;
            white-space: pre-wrap;
            font-family: Georgia, 'Times New Roman', serif;
            font-size: 16px;
            line-height: 1.8;
            color: #1a1a1a;
        }}
        
        .doc-actions {{
            position: sticky;
            bottom: 0;
            background: white;
            border-top: 2px solid #e0e0e0;
            padding: 20px;
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
            box-shadow: 0 -4px 20px rgba(0,0,0,0.1);
        }}
        
        .action-btn {{
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            border: none;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .action-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .btn-google-docs {{
            background: #4285f4;
            color: white;
        }}
        
        .btn-google-pdf {{
            background: #ea4335;
            color: white;
        }}
        
        .btn-download {{
            background: #0066cc;
            color: white;
        }}
        
        .btn-copy {{
            background: #ff6b35;
            color: white;
        }}
        
        .btn-email {{
            background: #28a745;
            color: white;
        }}
        
        .loading-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        }}
        
        .loading-content {{
            background: white;
            padding: 40px;
            border-radius: 12px;
            text-align: center;
            max-width: 400px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo" style="margin-bottom: 15px;">
            <span class="logo-accent">Disruptive</span> Ventures
        </div>
        <h1>{lang_flag} {doc_title}</h1>
        <p>{meeting['title']}</p>
    </div>
    
    <div class="nav">
        <a href="/meeting/{meeting_id}">← Back to Meeting</a>
        <a href="/dashboard-ui">Dashboard</a>
        <span style="margin-left: auto; color: #4a4a4a; font-size: 13px;">
            {'Svenska' if language == 'sv' else 'English'} | 
            <a href="/viewer/view/{doc_type}/{'en' if language == 'sv' else 'sv'}?meeting_id={meeting_id}" style="color: #0066cc; text-decoration: none;">
                Switch to {'English' if language == 'sv' else 'Swedish'}
            </a>
        </span>
    </div>
    
    <div class="doc-viewer">
        <div class="doc-content" id="docContent">
{content}
        </div>
    </div>
    
    <div class="doc-actions">
        <button onclick="saveToGoogleDocs()" class="action-btn btn-google-docs">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
            </svg>
            Save to Google Docs
        </button>
        
        <button onclick="saveToGooglePDF()" class="action-btn btn-google-pdf">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M13,9H18.5L13,3.5V9M6,2H14L20,8V20A2,2 0 0,1 18,22H6C4.89,22 4,21.1 4,20V4C4,2.89 4.89,2 6,2M15,18V16H6V18H15M18,14V12H6V14H18Z"/>
            </svg>
            Save as PDF
        </button>
        
        <button onclick="downloadDoc()" class="action-btn btn-download">
            📥 Download .txt
        </button>
        
        <button onclick="copyToClipboard()" class="action-btn btn-copy">
            📋 Copy All
        </button>
        
        <button onclick="emailDoc()" class="action-btn btn-email">
            📧 Email to Attendees
        </button>
    </div>
    
    <div id="loadingOverlay" class="loading-overlay">
        <div class="loading-content">
            <div style="width: 60px; height: 60px; border: 4px solid #f3f3f3; border-top: 4px solid #0066cc; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px;"></div>
            <h3 id="loadingTitle" style="color: #1a1a1a; margin-bottom: 10px;">Saving to Google Drive...</h3>
            <p id="loadingSubtitle" style="color: #4a4a4a; font-size: 14px;">Please wait</p>
        </div>
    </div>
    
    <style>
        @keyframes spin {{
            0%% {{ transform: rotate(0deg); }}
            100%% {{ transform: rotate(360deg); }}
        }}
    </style>
    
    <script>
        const docContent = document.getElementById('docContent').textContent;
        const docTitle = '{doc_title}';
        const meetingId = '{meeting_id}';
        
        async function saveToGoogleDocs() {{
            showLoading('Saving to Google Docs...', 'Converting to Google Docs format');
            
            try {{
                // TODO: Integrate with Google Drive API
                // Would call: POST /integrations/google/create-doc
                // Body: {{ title, content, folder_id }}
                
                setTimeout(() => {{
                    hideLoading();
                    alert('✅ Saved to Google Docs!\\n\\n⚠️ Google Drive integration coming soon.\\n\\nFor now: Click \"Copy All\" and paste into Google Docs manually.');
                }}, 2000);
                
                // Future implementation:
                /*
                const response = await fetch('/integrations/google/create-doc', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        title: docTitle,
                        content: docContent,
                        folder: 'Meeting Intelligence'
                    }})
                }});
                
                if (response.ok) {{
                    const data = await response.json();
                    window.open(data.doc_url, '_blank');
                }}
                */
                
            }} catch (error) {{
                hideLoading();
                alert('❌ Error: ' + error.message);
            }}
        }}
        
        async function saveToGooglePDF() {{
            showLoading('Creating PDF...', 'Formatting document for PDF');
            
            try {{
                // Print to PDF using browser
                setTimeout(() => {{
                    hideLoading();
                    window.print();  // Opens print dialog → Save as PDF
                }}, 1000);
                
                // Future: Direct PDF generation and upload to Google Drive
                
            }} catch (error) {{
                hideLoading();
                alert('❌ Error: ' + error.message);
            }}
        }}
        
        function downloadDoc() {{
            const blob = new Blob([docContent], {{ type: 'text/plain; charset=utf-8' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            const filename = docTitle.replace(/[^a-zA-Z0-9]/g, '_') + '_{language.upper()}.txt';
            a.download = filename;
            a.click();
            URL.revokeObjectURL(url);
        }}
        
        function copyToClipboard() {{
            navigator.clipboard.writeText(docContent).then(() => {{
                alert('✅ Kopierad till urklipp!');
            }}).catch(err => {{
                alert('❌ Kunde inte kopiera: ' + err);
            }});
        }}
        
        async function emailDoc() {{
            showLoading('Preparing email...', 'Generating email with document');
            
            // TODO: Integrate with Gmail API
            setTimeout(() => {{
                hideLoading();
                alert('📧 Email integration coming soon!\\n\\nFor now: Copy the content and email manually.');
            }}, 1500);
        }}
        
        function showLoading(title, subtitle) {{
            document.getElementById('loadingTitle').textContent = title;
            document.getElementById('loadingSubtitle').textContent = subtitle;
            document.getElementById('loadingOverlay').style.display = 'flex';
        }}
        
        function hideLoading() {{
            document.getElementById('loadingOverlay').style.display = 'none';
        }}
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html)

