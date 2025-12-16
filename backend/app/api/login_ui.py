"""Simple login UI."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_ui():
    """Simple login interface with Google OAuth."""
    
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Meeting Intelligence</title>
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
            padding: 60px 40px;
            max-width: 450px;
            width: 100%;
            text-align: center;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 40px;
            font-size: 1.1em;
        }
        
        .google-btn {
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px 30px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            width: 100%;
            text-decoration: none;
            color: #333;
            margin-bottom: 20px;
        }
        
        .google-btn:hover {
            background: #f8f9fa;
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.2);
        }
        
        .google-icon {
            width: 24px;
            height: 24px;
        }
        
        .dev-mode-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 15px 30px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            width: 100%;
            text-decoration: none;
            display: inline-block;
        }
        
        .dev-mode-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        
        .divider {
            margin: 30px 0;
            text-align: center;
            position: relative;
        }
        
        .divider::before {
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            width: 100%;
            height: 1px;
            background: #e0e0e0;
        }
        
        .divider span {
            background: white;
            padding: 0 15px;
            position: relative;
            color: #999;
            font-size: 14px;
        }
        
        .info-box {
            background: #f0f0ff;
            border-left: 4px solid #667eea;
            padding: 15px;
            border-radius: 8px;
            margin-top: 30px;
            text-align: left;
        }
        
        .info-box h3 {
            color: #667eea;
            font-size: 14px;
            margin-bottom: 8px;
        }
        
        .info-box p {
            color: #666;
            font-size: 13px;
            line-height: 1.6;
        }
        
        .info-box ul {
            margin: 10px 0 0 20px;
            color: #666;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📤 Meeting Intelligence</h1>
        <p class="subtitle">Sign in to process your meetings</p>
        
        <a href="/auth/google" class="google-btn">
            <svg class="google-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
                <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                <path fill="none" d="M0 0h48v48H0z"/>
            </svg>
            Sign in with Google
        </a>
        
        
        <div class="info-box">
            <h3>✨ What happens when you sign in:</h3>
            <ul>
                <li>Your organization is created automatically</li>
                <li>You're set as the owner</li>
                <li>Files are saved to database</li>
                <li>AI processing extracts action items & decisions</li>
                <li>All your data is private & secure</li>
            </ul>
        </div>
    </div>
    
    <script>
        // Check if we're returning from OAuth with an error
        const urlParams = new URLSearchParams(window.location.search);
        const error = urlParams.get('error');
        
        if (error) {
            alert('Login failed: ' + error);
        }
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html_content)


@router.get("/auth/success", response_class=HTMLResponse)
async def auth_success():
    """Success page after OAuth login."""
    
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login Successful</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
            padding: 60px 40px;
            max-width: 500px;
            width: 100%;
            text-align: center;
        }
        
        .success-icon {
            font-size: 80px;
            margin-bottom: 20px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 15px;
        }
        
        p {
            color: #666;
            margin-bottom: 30px;
            line-height: 1.6;
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
            text-decoration: none;
            display: inline-block;
            transition: transform 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        
        .token-info {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 30px 0;
            font-size: 12px;
            color: #666;
            text-align: left;
        }
        
        .token-info code {
            background: #e9ecef;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
            word-break: break-all;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✅</div>
        <h1>Login Successful!</h1>
        <p>
            Your organization has been created and you're all set!<br>
            You can now upload files and they'll be processed automatically.
        </p>
        
        <div id="tokenInfo" class="token-info" style="display:none;">
            <strong>Your Access Token:</strong><br>
            <code id="accessToken"></code>
        </div>
        
        <a href="/upload-ui" class="btn" id="uploadBtn">Upload Files</a>
    </div>
    
    <script>
        // Extract tokens from URL (can be in query params or hash)
        const urlParams = new URLSearchParams(window.location.search);
        const hashParams = new URLSearchParams(window.location.hash.substring(1));
        
        const accessToken = urlParams.get('access_token') || hashParams.get('access_token');
        const refreshToken = urlParams.get('refresh_token') || hashParams.get('refresh_token');
        
        if (accessToken) {
            // Store tokens in localStorage
            localStorage.setItem('access_token', accessToken);
            if (refreshToken) localStorage.setItem('refresh_token', refreshToken);
            
            // Show token info (optional, for dev)
            document.getElementById('accessToken').textContent = accessToken.substring(0, 50) + '...';
            document.getElementById('tokenInfo').style.display = 'block';
            
            // Call backend to ensure org exists
            fetch('http://localhost:8000/auth/ensure-org', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log('Org setup:', data);
                // Auto-redirect after org is created
                setTimeout(() => {
                    window.location.href = '/upload';
                }, 2000);
            })
            .catch(error => {
                console.error('Error setting up org:', error);
                // Redirect anyway
                setTimeout(() => {
                    window.location.href = '/upload';
                }, 3000);
            });
        } else {
            // No tokens found - might still be processing OAuth
            setTimeout(() => {
                if (!localStorage.getItem('access_token')) {
                    window.location.href = '/login?error=no_tokens';
                }
            }, 5000);
        }
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html_content)

