"""Simple web UI for bulk file upload."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/upload-ui", response_class=HTMLResponse)
async def upload_ui(request: Request):
    """
    Simple HTML interface for bulk file upload.
    PRODUCTION: Redirects to login if not authenticated.
    """
    
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meeting Intelligence - Bulk Upload</title>
    <script>
        // Check if user is authenticated - redirect to login if not
        window.addEventListener('DOMContentLoaded', function() {
            const token = localStorage.getItem('access_token');
            if (!token) {
                window.location.href = '/login?redirect=/upload-ui';
            }
        });
    </script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 800px;
            width: 100%;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2em;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        
        .auth-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        
        .input-group {
            margin-bottom: 15px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }
        
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        input[type="text"]:focus, input[type="password"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .upload-area {
            border: 3px dashed #ddd;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            background: #fafafa;
        }
        
        .upload-area:hover {
            border-color: #667eea;
            background: #f0f0ff;
        }
        
        .upload-area.dragover {
            border-color: #667eea;
            background: #e8e8ff;
        }
        
        .upload-icon {
            font-size: 60px;
            color: #667eea;
            margin-bottom: 20px;
        }
        
        #fileInput {
            display: none;
        }
        
        .file-list {
            margin-top: 20px;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .file-item {
            background: #f8f9fa;
            padding: 12px;
            margin-bottom: 8px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s;
        }
        
        .file-item.uploading {
            background: #fff3cd;
        }
        
        .file-item.success {
            background: #d4edda;
        }
        
        .file-item.error {
            background: #f8d7da;
        }
        
        .file-name {
            flex: 1;
            font-weight: 500;
        }
        
        .file-status {
            margin-left: 15px;
            font-size: 12px;
            padding: 4px 10px;
            border-radius: 12px;
            background: white;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-top: 20px;
            width: 100%;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 20px;
            display: none;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            width: 0%;
            transition: width 0.3s;
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📤 Meeting Intelligence</h1>
        <p class="subtitle">Bulk Upload - Process up to 100 files at once</p>
        
        <div style="text-align: center; margin: 15px 0;">
            <a href="/dashboard-ui" style="display: inline-block; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; transition: background 0.3s;">
                📊 View Dashboard
            </a>
        </div>
        
        <div id="alertBox" class="alert"></div>
        
        <div style="background: #e0f0ff; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #667eea;">
            <p style="margin: 0; color: #2c5282;">
                <strong>🔒 Secure Upload</strong> - Your files are private and only visible to your organization.
            </p>
        </div>
        
        <div class="upload-area" id="uploadArea">
            <div class="upload-icon">📁</div>
            <h3>Drop Word files here or click to browse</h3>
            <p style="color: #999; margin-top: 10px;">Supports .docx files (up to 50MB each)</p>
            <input type="file" id="fileInput" multiple accept=".docx,.doc">
        </div>
        
        <div class="progress-bar" id="progressBar">
            <div class="progress-fill" id="progressFill"></div>
        </div>
        
        <div class="file-list" id="fileList"></div>
        
        <button class="btn" id="uploadBtn" disabled>Upload Files</button>
        
        <div class="stats" id="stats" style="display: none;">
            <div class="stat">
                <div class="stat-value" id="totalFiles">0</div>
                <div class="stat-label">Total Files</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="successCount">0</div>
                <div class="stat-label">Uploaded</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="errorCount">0</div>
                <div class="stat-label">Failed</div>
            </div>
        </div>
    </div>
    
    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const fileList = document.getElementById('fileList');
        const uploadBtn = document.getElementById('uploadBtn');
        const progressBar = document.getElementById('progressBar');
        const progressFill = document.getElementById('progressFill');
        const stats = document.getElementById('stats');
        const alertBox = document.getElementById('alertBox');
        
        let selectedFiles = [];
        let uploadResults = { success: 0, error: 0 };
        
        uploadArea.addEventListener('click', () => fileInput.click());
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            handleFiles(e.dataTransfer.files);
        });
        
        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });
        
        function showAlert(message, type) {
            alertBox.textContent = message;
            alertBox.className = `alert alert-${type}`;
            alertBox.style.display = 'block';
            setTimeout(() => {
                alertBox.style.display = 'none';
            }, 5000);
        }
        
        function handleFiles(files) {
            selectedFiles = Array.from(files).filter(f => 
                f.name.endsWith('.docx') || f.name.endsWith('.doc')
            );
            
            if (selectedFiles.length === 0) {
                showAlert('Please select Word documents (.docx or .doc)', 'error');
                return;
            }
            
            displayFiles();
            uploadBtn.disabled = false; // Dev mode: no auth required
            document.getElementById('totalFiles').textContent = selectedFiles.length;
            stats.style.display = 'flex';
        }
        
        function displayFiles() {
            fileList.innerHTML = '';
            selectedFiles.forEach((file, index) => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                fileItem.id = `file-${index}`;
                fileItem.innerHTML = `
                    <span class="file-name">${file.name}</span>
                    <span class="file-status" id="status-${index}">Pending</span>
                `;
                fileList.appendChild(fileItem);
            });
        }
        
        async function uploadFile(file, index) {
            const fileItem = document.getElementById(`file-${index}`);
            const statusSpan = document.getElementById(`status-${index}`);
            
            fileItem.classList.add('uploading');
            statusSpan.textContent = 'Uploading...';
            
            const formData = new FormData();
            formData.append('file', file);
            
            // Get auth token from localStorage
            const token = localStorage.getItem('access_token');
            const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
            
            try {
                const response = await fetch('http://localhost:8000/artifacts/upload-simple', {
                    method: 'POST',
                    headers: headers,
                    body: formData
                });
                
                if (response.ok) {
                    fileItem.classList.remove('uploading');
                    fileItem.classList.add('success');
                    statusSpan.textContent = '✓ Success';
                    uploadResults.success++;
                } else {
                    throw new Error(await response.text());
                }
            } catch (error) {
                fileItem.classList.remove('uploading');
                fileItem.classList.add('error');
                statusSpan.textContent = '✗ Failed';
                uploadResults.error++;
                console.error('Upload failed:', error);
            }
            
            document.getElementById('successCount').textContent = uploadResults.success;
            document.getElementById('errorCount').textContent = uploadResults.error;
            
            const progress = ((uploadResults.success + uploadResults.error) / selectedFiles.length) * 100;
            progressFill.style.width = progress + '%';
        }
        
        uploadBtn.addEventListener('click', async () => {
            uploadBtn.disabled = true;
            progressBar.style.display = 'block';
            uploadResults = { success: 0, error: 0 };
            
            showAlert(`Uploading ${selectedFiles.length} files...`, 'success');
            
            // Upload files in parallel (5 at a time)
            const chunkSize = 5;
            for (let i = 0; i < selectedFiles.length; i += chunkSize) {
                const chunk = selectedFiles.slice(i, i + chunkSize);
                await Promise.all(
                    chunk.map((file, idx) => uploadFile(file, i + idx))
                );
            }
            
            showAlert(
                `Upload complete! ${uploadResults.success} succeeded, ${uploadResults.error} failed.`,
                uploadResults.error === 0 ? 'success' : 'error'
            );
            
            uploadBtn.disabled = false;
            uploadBtn.textContent = 'Upload More Files';
        });
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html_content)

