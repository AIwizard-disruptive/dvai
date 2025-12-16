"""Voice recording UI with Whisperflow integration."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/record", response_class=HTMLResponse)
async def recording_ui():
    """Voice recording interface with real-time transcription."""
    
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Record Meeting - Meeting Intelligence</title>
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
            max-width: 600px;
            width: 100%;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2em;
            text-align: center;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .record-btn {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            border: none;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-size: 24px;
            cursor: pointer;
            transition: all 0.3s;
            margin: 30px auto;
            display: block;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .record-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.5);
        }
        
        .record-btn.recording {
            background: #ef4444;
            animation: pulse 1.5s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
                box-shadow: 0 10px 30px rgba(239, 68, 68, 0.3);
            }
            50% {
                transform: scale(1.05);
                box-shadow: 0 15px 40px rgba(239, 68, 68, 0.6);
            }
        }
        
        .status {
            text-align: center;
            font-size: 18px;
            color: #666;
            margin: 20px 0;
            min-height: 30px;
        }
        
        .status.recording {
            color: #ef4444;
            font-weight: 600;
        }
        
        .timer {
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin: 20px 0;
            font-variant-numeric: tabular-nums;
        }
        
        .transcript-box {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 30px 0;
            min-height: 200px;
            max-height: 400px;
            overflow-y: auto;
            display: none;
        }
        
        .transcript-box.active {
            display: block;
        }
        
        .transcript-box h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 16px;
        }
        
        .transcript-text {
            color: #333;
            line-height: 1.6;
            white-space: pre-wrap;
        }
        
        .actions {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-top: 20px;
        }
        
        .btn {
            padding: 12px 30px;
            border-radius: 8px;
            border: none;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #e0e0e0;
            color: #333;
        }
        
        .btn-secondary:hover {
            background: #d0d0d0;
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .info-box {
            background: #f0f0ff;
            border-left: 4px solid #667eea;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }
        
        .info-box p {
            color: #666;
            font-size: 14px;
            line-height: 1.6;
        }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        
        .alert.error {
            background: #fee;
            color: #c33;
            border: 1px solid #fcc;
            display: block;
        }
        
        .alert.success {
            background: #efe;
            color: #3c3;
            border: 1px solid #cfc;
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎙️ Record Meeting</h1>
        <p class="subtitle">Record and transcribe in real-time</p>
        
        <div id="alert" class="alert"></div>
        
        <div class="status" id="status">Click to start recording</div>
        <div class="timer" id="timer">00:00</div>
        
        <button class="record-btn" id="recordBtn">
            <span id="btnIcon">🎙️</span>
        </button>
        
        <div class="transcript-box" id="transcriptBox">
            <h3>📝 Live Transcript</h3>
            <div class="transcript-text" id="transcriptText">
                Transcript will appear here as you speak...
            </div>
        </div>
        
        <div class="actions">
            <button class="btn btn-secondary" id="cancelBtn" disabled>Cancel</button>
            <button class="btn btn-primary" id="saveBtn" disabled>Save & Process</button>
        </div>
        
        <div class="info-box">
            <p>
                <strong>💡 How it works:</strong><br>
                1. Click the microphone to start recording<br>
                2. Speak naturally - real-time transcription via Whisperflow<br>
                3. Click again to stop<br>
                4. Save to automatically extract action items & decisions
            </p>
        </div>
    </div>
    
    <script>
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;
        let startTime;
        let timerInterval;
        let audioContext;
        let whisperflowWs;
        
        const recordBtn = document.getElementById('recordBtn');
        const btnIcon = document.getElementById('btnIcon');
        const status = document.getElementById('status');
        const timer = document.getElementById('timer');
        const transcriptBox = document.getElementById('transcriptBox');
        const transcriptText = document.getElementById('transcriptText');
        const cancelBtn = document.getElementById('cancelBtn');
        const saveBtn = document.getElementById('saveBtn');
        const alert = document.getElementById('alert');
        
        // Format time as MM:SS
        function formatTime(seconds) {
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        }
        
        // Update timer
        function updateTimer() {
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            timer.textContent = formatTime(elapsed);
        }
        
        // Show alert
        function showAlert(message, type = 'error') {
            alert.textContent = message;
            alert.className = `alert ${type}`;
            setTimeout(() => {
                alert.className = 'alert';
            }, 5000);
        }
        
        // Connect to Whisperflow WebSocket
        function connectWhisperflow() {
            // TODO: Replace with actual Whisperflow WebSocket endpoint
            // For now, simulate with local processing
            console.log('Connecting to Whisperflow...');
            
            // Simulated real-time transcription
            // In production, this would connect to Whisperflow's WebSocket API
            return {
                send: (data) => console.log('Sending audio chunk to Whisperflow'),
                close: () => console.log('Closed Whisperflow connection')
            };
        }
        
        // Start recording
        async function startRecording() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        sampleRate: 16000
                    } 
                });
                
                mediaRecorder = new MediaRecorder(stream, {
                    mimeType: 'audio/webm'
                });
                
                audioChunks = [];
                
                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        audioChunks.push(event.data);
                        
                        // Send to Whisperflow for real-time transcription
                        if (whisperflowWs) {
                            whisperflowWs.send(event.data);
                        }
                    }
                };
                
                mediaRecorder.onstop = () => {
                    stream.getTracks().forEach(track => track.stop());
                };
                
                mediaRecorder.start(1000); // Capture chunks every second
                
                // Connect to Whisperflow
                whisperflowWs = connectWhisperflow();
                
                isRecording = true;
                startTime = Date.now();
                timerInterval = setInterval(updateTimer, 1000);
                
                recordBtn.classList.add('recording');
                btnIcon.textContent = '⏸️';
                status.textContent = 'Recording... Click to stop';
                status.classList.add('recording');
                transcriptBox.classList.add('active');
                cancelBtn.disabled = false;
                
                // Simulate real-time transcription
                simulateTranscription();
                
            } catch (error) {
                console.error('Error starting recording:', error);
                showAlert('Could not access microphone. Please grant permission.', 'error');
            }
        }
        
        // Stop recording
        function stopRecording() {
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
                
                if (whisperflowWs) {
                    whisperflowWs.close();
                }
                
                clearInterval(timerInterval);
                
                isRecording = false;
                recordBtn.classList.remove('recording');
                btnIcon.textContent = '✅';
                status.textContent = 'Recording stopped';
                status.classList.remove('recording');
                saveBtn.disabled = false;
            }
        }
        
        // Simulate real-time transcription (replace with actual Whisperflow integration)
        function simulateTranscription() {
            const sampleTranscript = [
                "Let's start with the Q1 review...",
                "I think we should prioritize the mobile app redesign.",
                "Sarah, can you take the lead on that?",
                "We need to allocate budget by next week.",
                "John will handle the technical specification.",
                "Target launch date is end of Q2."
            ];
            
            let index = 0;
            const transcriptionInterval = setInterval(() => {
                if (!isRecording || index >= sampleTranscript.length) {
                    clearInterval(transcriptionInterval);
                    return;
                }
                
                const current = transcriptText.textContent;
                if (current === 'Transcript will appear here as you speak...') {
                    transcriptText.textContent = sampleTranscript[index];
                } else {
                    transcriptText.textContent = current + ' ' + sampleTranscript[index];
                }
                
                index++;
            }, 3000);
        }
        
        // Save and process
        async function saveRecording() {
            const blob = new Blob(audioChunks, { type: 'audio/webm' });
            const formData = new FormData();
            formData.append('file', blob, 'recording.webm');
            
            // Get auth token
            const token = localStorage.getItem('access_token');
            
            const headers = token ? {
                'Authorization': `Bearer ${token}`
            } : {};
            
            try {
                showAlert('Uploading and processing...', 'success');
                
                const response = await fetch('http://localhost:8000/artifacts/upload', {
                    method: 'POST',
                    headers: headers,
                    body: formData
                });
                
                if (response.ok) {
                    const result = await response.json();
                    showAlert('Recording saved! Processing with AI...', 'success');
                    
                    // Redirect to meetings page after 2 seconds
                    setTimeout(() => {
                        window.location.href = '/upload-protected';
                    }, 2000);
                } else {
                    throw new Error('Upload failed');
                }
            } catch (error) {
                console.error('Error saving recording:', error);
                showAlert('Failed to save recording. Please try again.', 'error');
            }
        }
        
        // Event listeners
        recordBtn.addEventListener('click', () => {
            if (isRecording) {
                stopRecording();
            } else {
                startRecording();
            }
        });
        
        cancelBtn.addEventListener('click', () => {
            if (isRecording) {
                stopRecording();
            }
            audioChunks = [];
            transcriptText.textContent = 'Transcript will appear here as you speak...';
            timer.textContent = '00:00';
            status.textContent = 'Click to start recording';
            status.classList.remove('recording');
            btnIcon.textContent = '🎙️';
            cancelBtn.disabled = true;
            saveBtn.disabled = true;
            transcriptBox.classList.remove('active');
        });
        
        saveBtn.addEventListener('click', saveRecording);
        
        // Check for microphone permission
        navigator.permissions.query({ name: 'microphone' }).then((result) => {
            if (result.state === 'denied') {
                showAlert('Microphone access denied. Please enable in browser settings.', 'error');
            }
        });
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html_content)




