# Start Frontend Server on Port 8000

## Current Situation

- ✅ **Backend server**: Running on port 8000 (Terminal 2)
- ⏳ **Frontend server**: Not started yet

## Option 1: Keep Backend on 8000, Frontend on 3000 (Recommended)

### Start Frontend (Default Port 3000)
Open a new terminal and run:

```bash
cd "/Users/marcus/Library/Mobile Documents/com~apple~CloudDocs/Documents/Cursor-projects/Disruptive Ventures/DV Legacy/dv/frontend"
npm install  # Only needed first time
npm run dev
```

Then visit: **http://localhost:3000**

---

## Option 2: Stop Backend, Run Frontend on 8000

### Step 1: Stop Backend Server
In Terminal 2 (where backend is running), press: **Ctrl+C**

### Step 2: Start Frontend on Port 8000
Open a new terminal and run:

```bash
cd "/Users/marcus/Library/Mobile Documents/com~apple~CloudDocs/Documents/Cursor-projects/Disruptive Ventures/DV Legacy/dv/frontend"
./start-frontend.sh
```

Or manually:

```bash
cd "/Users/marcus/Library/Mobile Documents/com~apple~CloudDocs/Documents/Cursor-projects/Disruptive Ventures/DV Legacy/dv/frontend"
npm install  # Only needed first time
npm run dev -- -p 8000
```

Then visit: **http://localhost:8000**

---

## Option 3: Both Running (Different Ports)

**Backend on 8000** + **Frontend on 3000** = Full System

### Keep backend running in Terminal 2
(Already running - no action needed)

### Start frontend in a new terminal:

```bash
cd "/Users/marcus/Library/Mobile Documents/com~apple~CloudDocs/Documents/Cursor-projects/Disruptive Ventures/DV Legacy/dv/frontend"
npm run dev
```

**Access:**
- Frontend UI: http://localhost:3000 (New Claude-style interface)
- Backend API: http://localhost:8000 (API endpoints)

---

## Quick Command Summary

### Stop Backend (Terminal 2):
Press: `Ctrl+C`

### Start Frontend on 8000:
```bash
cd "/Users/marcus/Library/Mobile Documents/com~apple~CloudDocs/Documents/Cursor-projects/Disruptive Ventures/DV Legacy/dv/frontend"
npm run dev -- -p 8000
```

### Start Frontend on 3000 (default):
```bash
cd "/Users/marcus/Library/Mobile Documents/com~apple~CloudDocs/Documents/Cursor-projects/Disruptive Ventures/DV Legacy/dv/frontend"
npm run dev
```

---

## Troubleshooting

### "Port 8000 already in use"
- Backend is still running on 8000
- Go to Terminal 2 and press Ctrl+C to stop it
- Or use port 3000 for frontend instead

### "npm: command not found"
- Node.js not installed or not in PATH
- Install Node.js from: https://nodejs.org/
- Or use Homebrew: `brew install node`

### "Cannot find module 'next'"
```bash
cd frontend
npm install
```

---

## What You'll See

Once the frontend starts successfully, you'll see:

```
- ready started server on 0.0.0.0:8000, url: http://localhost:8000
- event compiled client and server successfully
```

Then you can visit the new Claude-inspired UI at the URL shown!

---

**Recommendation**: Run frontend on port 3000 (default) so both frontend and backend can run simultaneously.


