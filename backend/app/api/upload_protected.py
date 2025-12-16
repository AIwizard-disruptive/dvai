"""Protected upload UI with authentication."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/upload", response_class=HTMLResponse)
async def protected_upload_ui(request: Request):
    """Protected upload interface with login."""
    
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meeting Intelligence - Upload</title>
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
        
        /* Login Section */
        #loginSection {
            max-width: 400px;
            margin: 0 auto;
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }
        
        input[type="email"], input[type="password"], input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        input:focus {
            outline: none;
            border-color: #667eea;
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
            width: 100%;
            margin-top: 10px;
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
        
        .btn-google {
            background: white;
            color: #333;
            border: 2px solid #e0e0e0;
            margin-top: 15px;
        }
        
        .btn-google:hover {
            background: #f5f5f5;
        }
        
        .divider {
            text-align: center;
            margin: 20px 0;
            color: #999;
            position: relative;
        }
        
        .divider::before,
        .divider::after {
            content: '';
            position: absolute;
            top: 50%;
            width: 45%;
            height: 1px;
            background: #e0e0e0;
        }
        
        .divider::before {
            left: 0;
        }
        
        .divider::after {
            right: 0;
        }
        
        .toggle-auth {
            text-align: center;
            margin-top: 20px;
            color: #666;
        }
        
        .toggle-auth a {
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }
        
        .toggle-auth a:hover {
            text-decoration: underline;
        }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
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
        
        /* Upload Section - Hidden until logged in */
        #uploadSection {
            display: none;
        }
        
        .user-info {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
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
        
        .stats {
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
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
    </style>
</head>
<body>
    <div class="container">
        <h1>📤 Meeting Intelligence</h1>
        <p class="subtitle">Secure Bulk Upload</p>
        
        <div id="alertBox" class="alert" style="display: none;"></div>
        
        <!-- Login Section -->
        <div id="loginSection">
            <div class="input-group">
                <label for="email">📧 Email</label>
                <input type="email" id="email" placeholder="your@email.com" required>
            </div>
            <div class="input-group">
                <label for="password">🔒 Password</label>
                <input type="password" id="password" placeholder="Enter your password" required>
            </div>
            
            <div id="signupFields" style="display: none;">
                <div class="input-group">
                    <label for="confirmPassword">🔒 Confirm Password</label>
                    <input type="password" id="confirmPassword" placeholder="Confirm your password">
                </div>
                <div class="input-group">
                    <label for="fullName">👤 Full Name (Optional)</label>
                    <input type="text" id="fullName" placeholder="Your name">
                </div>
            </div>
            
            <button class="btn" id="authBtn" onclick="handleAuth()">Log In</button>
            
            <div class="divider">OR</div>
            
            <button class="btn btn-google" onclick="loginWithGoogle()">
                <span style="font-size: 20px;">🔐</span> Continue with Google
            </button>
            
            <div class="toggle-auth">
                <span id="toggleText">Don't have an account?</span>
                <a href="#" id="toggleLink" onclick="toggleAuthMode(); return false;">Sign Up</a>
            </div>
        </div>
        
        <!-- Upload Section (shown after login) -->
        <div id="uploadSection">
            <div class="user-info">
                <div>
                    <strong id="userName"></strong>
                    <div id="userEmail" style="color: #666; font-size: 14px;"></div>
                </div>
                <button class="btn" style="width: auto; padding: 10px 20px;" onclick="logout()">Logout</button>
            </div>
            
            <div class="upload-area" id="uploadArea">
                <div class="upload-icon">📁</div>
                <h3>Drop files here or click to browse</h3>
                <p style="color: #999; margin-top: 10px;">Supports .docx files</p>
                <input type="file" id="fileInput" multiple accept=".docx,.doc">
            </div>
            
            <div class="file-list" id="fileList"></div>
            
            <button class="btn" id="uploadBtn" disabled onclick="uploadFiles()">Upload Files</button>
            
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
    </div>
    
    <script>
        let isSignupMode = false;
        let currentUser = null;
        let accessToken = null;
        let selectedFiles = [];
        let uploadResults = { success: 0, error: 0 };
        
        // Check if already logged in
        checkAuth();
        
        function checkAuth() {
            const token = localStorage.getItem('access_token');
            if (token) {
                accessToken = token;
                fetchCurrentUser();
            }
        }
        
        async function fetchCurrentUser() {
            try {
                const response = await fetch('http://localhost:8000/auth/me', {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                });
                
                if (response.ok) {
                    currentUser = await response.json();
                    showUploadSection();
                } else {
                    // Token invalid, clear it
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                }
            } catch (error) {
                console.error('Auth check failed:', error);
            }
        }
        
        function toggleAuthMode() {
            isSignupMode = !isSignupMode;
            const signupFields = document.getElementById('signupFields');
            const authBtn = document.getElementById('authBtn');
            const toggleText = document.getElementById('toggleText');
            const toggleLink = document.getElementById('toggleLink');
            
            if (isSignupMode) {
                signupFields.style.display = 'block';
                authBtn.textContent = 'Sign Up';
                toggleText.textContent = 'Already have an account?';
                toggleLink.textContent = 'Log In';
            } else {
                signupFields.style.display = 'none';
                authBtn.textContent = 'Log In';
                toggleText.textContent = "Don't have an account?";
                toggleLink.textContent = 'Sign Up';
            }
        }
        
        async function handleAuth() {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (!email || !password) {
                showAlert('Please enter email and password', 'error');
                return;
            }
            
            if (isSignupMode) {
                const confirmPassword = document.getElementById('confirmPassword').value;
                if (password !== confirmPassword) {
                    showAlert('Passwords do not match', 'error');
                    return;
                }
                await signup(email, password);
            } else {
                await login(email, password);
            }
        }
        
        async function signup(email, password) {
            try {
                const fullName = document.getElementById('fullName').value;
                const response = await fetch('http://localhost:8000/auth/signup', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ email, password, full_name: fullName })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showAlert(data.message, 'success');
                    accessToken = data.access_token;
                    localStorage.setItem('access_token', data.access_token);
                    localStorage.setItem('refresh_token', data.refresh_token);
                    currentUser = data.user;
                    showUploadSection();
                } else {
                    showAlert(data.detail || 'Signup failed', 'error');
                }
            } catch (error) {
                showAlert('Network error: ' + error.message, 'error');
            }
        }
        
        async function login(email, password) {
            try {
                const response = await fetch('http://localhost:8000/auth/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ email, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showAlert(data.message, 'success');
                    accessToken = data.access_token;
                    localStorage.setItem('access_token', data.access_token);
                    localStorage.setItem('refresh_token', data.refresh_token);
                    currentUser = data.user;
                    showUploadSection();
                } else {
                    showAlert(data.detail || 'Login failed', 'error');
                }
            } catch (error) {
                showAlert('Network error: ' + error.message, 'error');
            }
        }
        
        function loginWithGoogle() {
            window.location.href = 'http://localhost:8000/auth/google';
        }
        
        async function logout() {
            try {
                await fetch('http://localhost:8000/auth/logout', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                });
            } catch (error) {
                console.error('Logout error:', error);
            }
            
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            accessToken = null;
            currentUser = null;
            showLoginSection();
        }
        
        function showLoginSection() {
            document.getElementById('loginSection').style.display = 'block';
            document.getElementById('uploadSection').style.display = 'none';
        }
        
        function showUploadSection() {
            document.getElementById('loginSection').style.display = 'none';
            document.getElementById('uploadSection').style.display = 'block';
            document.getElementById('userName').textContent = currentUser.full_name || currentUser.email;
            document.getElementById('userEmail').textContent = currentUser.email;
        }
        
        function showAlert(message, type) {
            const alertBox = document.getElementById('alertBox');
            alertBox.textContent = message;
            alertBox.className = `alert alert-${type}`;
            alertBox.style.display = 'block';
            setTimeout(() => {
                alertBox.style.display = 'none';
            }, 5000);
        }
        
        // File upload logic
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const fileList = document.getElementById('fileList');
        const uploadBtn = document.getElementById('uploadBtn');
        
        uploadArea.addEventListener('click', () => fileInput.click());
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = '#667eea';
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.style.borderColor = '#ddd';
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = '#ddd';
            handleFiles(e.dataTransfer.files);
        });
        
        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });
        
        function handleFiles(files) {
            selectedFiles = Array.from(files).filter(f => 
                f.name.endsWith('.docx') || f.name.endsWith('.doc')
            );
            
            if (selectedFiles.length === 0) {
                showAlert('Please select Word documents (.docx or .doc)', 'error');
                return;
            }
            
            displayFiles();
            uploadBtn.disabled = false;
            document.getElementById('totalFiles').textContent = selectedFiles.length;
            document.getElementById('stats').style.display = 'flex';
        }
        
        function displayFiles() {
            fileList.innerHTML = '';
            selectedFiles.forEach((file, index) => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                fileItem.id = `file-${index}`;
                fileItem.innerHTML = `
                    <span>${file.name}</span>
                    <span id="status-${index}">Pending</span>
                `;
                fileList.appendChild(fileItem);
            });
        }
        
        async function uploadFiles() {
            uploadBtn.disabled = true;
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
        }
        
        async function uploadFile(file, index) {
            const fileItem = document.getElementById(`file-${index}`);
            const statusSpan = document.getElementById(`status-${index}`);
            
            fileItem.classList.add('uploading');
            statusSpan.textContent = 'Uploading...';
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('http://localhost:8000/artifacts/upload', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    },
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
        }
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html_content)




