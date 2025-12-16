"""Upload UI - Monochrome design with left sidebar."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.api.styles import get_dv_styles
from app.api.sidebar_component import get_admin_sidebar

router = APIRouter()


@router.get("/upload-ui", response_class=HTMLResponse)
async def upload_ui(request: Request):
    """Upload interface with left sidebar and monochrome design."""
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload Files - Admin</title>
    {get_dv_styles()}
    <style>
        .upload-area {{
            border: 2px dashed var(--gray-300);
            border-radius: 8px;
            padding: 48px 24px;
            text-align: center;
            background: var(--gray-50);
            transition: all 0.15s;
            cursor: pointer;
            margin-bottom: 24px;
        }}
        
        .upload-area:hover {{
            border-color: var(--gray-400);
            background: white;
        }}
        
        .upload-area.drag-over {{
            border-color: var(--gray-900);
            background: white;
        }}
        
        .file-list {{
            margin-top: 24px;
        }}
        
        .file-item {{
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .progress-bar {{
            height: 4px;
            background: var(--gray-200);
            border-radius: 2px;
            overflow: hidden;
            margin-top: 8px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: var(--gray-900);
            transition: width 0.3s;
        }}
    </style>
</head>
<body>
    {get_admin_sidebar('upload', 'Markus Löwegren', 'markus.lowegren@disruptiveventures.se', '')}
    
    <div class="main-content">
        <div class="page-header">
            <h1 class="page-title">Upload Files</h1>
            <p class="page-description">Upload meeting recordings or documents for processing</p>
        </div>
        
        <div class="container">
            <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
                <input type="file" id="fileInput" multiple style="display: none;" accept=".mp3,.wav,.m4a,.docx,.doc,.txt">
                <div style="font-size: 48px; color: var(--gray-400); margin-bottom: 16px;">↑</div>
                <h3 style="font-size: 16px; font-weight: 600; color: var(--gray-900); margin-bottom: 8px;">
                    Click to upload or drag and drop
                </h3>
                <p style="font-size: 13px; color: var(--gray-600);">
                    Audio files (MP3, WAV, M4A) or documents (DOCX, DOC, TXT)
                </p>
            </div>
            
            <div id="fileList" class="file-list"></div>
            
            <div style="display: flex; gap: 12px; margin-top: 24px;">
                <button id="uploadBtn" class="btn-primary" style="display: none;">
                    Upload Files
                </button>
                <button id="clearBtn" class="btn-secondary" style="display: none;">
                    Clear All
                </button>
            </div>
            
            <div id="results" style="margin-top: 24px;"></div>
        </div>
    </div>
    
    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const fileList = document.getElementById('fileList');
        const uploadBtn = document.getElementById('uploadBtn');
        const clearBtn = document.getElementById('clearBtn');
        const results = document.getElementById('results');
        let selectedFiles = [];
        
        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {{
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        }});
        
        uploadArea.addEventListener('dragleave', () => {{
            uploadArea.classList.remove('drag-over');
        }});
        
        uploadArea.addEventListener('drop', (e) => {{
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            const files = Array.from(e.dataTransfer.files);
            addFiles(files);
        }});
        
        fileInput.addEventListener('change', (e) => {{
            const files = Array.from(e.target.files);
            addFiles(files);
        }});
        
        function addFiles(files) {{
            selectedFiles = [...selectedFiles, ...files];
            updateFileList();
            uploadBtn.style.display = 'inline-block';
            clearBtn.style.display = 'inline-block';
        }}
        
        function updateFileList() {{
            fileList.innerHTML = selectedFiles.map((file, index) => `
                <div class="file-item">
                    <div>
                        <div style="font-size: 13px; font-weight: 500; color: var(--gray-900);">${{file.name}}</div>
                        <div style="font-size: 11px; color: var(--gray-500);">${{(file.size / 1024 / 1024).toFixed(2)}} MB</div>
                    </div>
                    <button onclick="removeFile(${{index}})" style="background: none; border: none; color: var(--gray-600); cursor: pointer; padding: 4px 8px;">✕</button>
                </div>
            `).join('');
        }}
        
        function removeFile(index) {{
            selectedFiles.splice(index, 1);
            updateFileList();
            if (selectedFiles.length === 0) {{
                uploadBtn.style.display = 'none';
                clearBtn.style.display = 'none';
            }}
        }}
        
        clearBtn.addEventListener('click', () => {{
            selectedFiles = [];
            fileList.innerHTML = '';
            uploadBtn.style.display = 'none';
            clearBtn.style.display = 'none';
            results.innerHTML = '';
        }});
        
        uploadBtn.addEventListener('click', async () => {{
            results.innerHTML = '<div style="padding: 16px; border: 1px solid var(--gray-200); border-radius: 8px; background: var(--gray-50); color: var(--gray-900);">Uploading files...</div>';
            
            for (const file of selectedFiles) {{
                const formData = new FormData();
                formData.append('file', file);
                
                try {{
                    const response = await fetch('/upload', {{
                        method: 'POST',
                        body: formData
                    }});
                    
                    if (response.ok) {{
                        console.log(`Uploaded: ${{file.name}}`);
                    }}
                }} catch (error) {{
                    console.error('Upload error:', error);
                }}
            }}
            
            results.innerHTML = '<div style="padding: 16px; border: 1px solid var(--gray-200); border-radius: 8px; background: white; color: var(--gray-900);">✓ Upload complete</div>';
            selectedFiles = [];
            updateFileList();
            uploadBtn.style.display = 'none';
            clearBtn.style.display = 'none';
        }});
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html_content)
