# 🚀 Quick Setup with Your OpenAI Key

Your OpenAI API key has been added! Here's how to complete the setup:

## Step 1: Copy Configuration File

```bash
cd "/Users/marcus/Library/Mobile Documents/com~apple~CloudDocs/Documents/Cursor-projects/Disruptive Ventures/DV Legacy/dv/backend"

cp env.local.configured .env
```

## Step 2: Get Remaining Supabase Credentials

You still need these from your Supabase dashboard:

### A. Service Role Key & JWT Secret
1. Visit: https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/settings/api
2. Copy **service_role** key (starts with `eyJ...`)
3. Copy **JWT Secret**
4. Update in `.env`:
   ```env
   SUPABASE_SERVICE_ROLE_KEY=eyJ...
   SUPABASE_JWT_SECRET=your-jwt-secret
   ```

### B. Database Password
1. Visit: https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/settings/database
2. Find or reset your database password
3. Update in `.env`:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres.gqpupmuzriqarmrsuwev:YOUR_ACTUAL_PASSWORD@aws-0-us-east-1.pooler.supabase.com:5432/postgres
   ```

### C. Generate Encryption Key
```bash
python3 -c "import base64; import os; print(base64.b64encode(os.urandom(32)).decode())"
```

Copy the output and update in `.env`:
```env
ENCRYPTION_KEY=<paste-generated-key-here>
```

## Step 3: Install Dependencies & Test

```bash
# Create virtual environment (if not exists)
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test connection
python scripts/test_connection.py
```

## Step 4: Run Migrations

```bash
python scripts/migrate.py
```

This creates all tables with Row Level Security policies in your Supabase database.

## Step 5: Start the Application

### Terminal 1 - API Server
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 - Redis
```bash
redis-server
```

### Terminal 3 - Celery Worker
```bash
cd backend
source venv/bin/activate
celery -A app.worker.celery_app worker --loglevel=info
```

## Step 6: Verify It's Working

```bash
# Health check
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","service":"Meeting Intelligence Platform","environment":"development"}
```

Visit API docs: http://localhost:8000/docs

## Step 7: Create Your First User & Org

### A. Create User in Supabase Dashboard
1. Go to: https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/auth/users
2. Click "Add user" → "Create new user"
3. Enter email and password
4. **Copy the User ID** (you'll need this)

### B. Get Auth Token
You can get a JWT token by:
- Using Supabase client to sign in
- Or temporarily using your service role key for testing (not recommended for production)

### C. Create Organization via API
```bash
# Replace $TOKEN with your JWT token
curl -X POST http://localhost:8000/orgs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Company"}'
```

Save the returned `org_id`.

## Step 8: Upload Your First Meeting

```bash
# Replace $TOKEN and $ORG_ID with your values
curl -X POST http://localhost:8000/artifacts/upload \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" \
  -F "file=@path/to/meeting.mp3"
```

The system will:
1. ✓ Upload file to Supabase Storage
2. ✓ Transcribe using OpenAI Whisper (your key is configured!)
3. ✓ Extract summaries, decisions, action items using GPT-4
4. ✓ Store everything in your database

## Quick Test Without Audio File

If you don't have an audio file, you can test with a text document:

```bash
# Create a test meeting document
cat > test_meeting.txt << 'EOF'
Meeting Notes - Q1 Planning
Date: 2025-12-12

Attendees: Alice, Bob, Charlie

Discussion:
- Decided to launch new product in Q2
- Alice will complete the design mockups by Dec 20
- Bob will review the pricing proposal
- Charlie agreed to schedule a follow-up meeting next week

Action Items:
1. Alice: Complete design mockups - Due Dec 20
2. Bob: Review pricing proposal - Due Dec 15
3. Charlie: Schedule follow-up - Due Dec 13
EOF

# Upload (if you save as .docx it will work better, but text files work for testing)
```

## What's Already Configured

✅ **OpenAI API Key** - For transcription and extraction  
✅ **Supabase URL** - Your project endpoint  
✅ **Supabase Anon Key** - For public access  
✅ **Default Provider** - Set to OpenAI  

## What You Need to Add

⬜ **Service Role Key** - From Supabase API settings  
⬜ **JWT Secret** - From Supabase API settings  
⬜ **Database Password** - From Supabase Database settings  
⬜ **Encryption Key** - Generate with Python command  

## Troubleshooting

### "Module not found" errors
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### "Connection refused" to database
- Double-check your database password in DATABASE_URL
- Ensure Supabase project is not paused

### OpenAI API errors
- Your key is already configured! Just make sure you have credits in your OpenAI account
- Test at: https://platform.openai.com/api-keys

### Redis connection errors
```bash
# Install Redis if needed (macOS)
brew install redis

# Start Redis
redis-server

# Or start as background service
brew services start redis
```

## Next Steps After Setup

1. **Set up Frontend**: 
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

2. **Configure Integrations** (optional):
   - Linear API for task sync
   - Google OAuth for Gmail/Calendar

3. **Read Documentation**:
   - `README.md` - Full documentation
   - `SUPABASE_SETUP.md` - Detailed Supabase guide
   - `QUICKSTART.md` - General quick start

## Need Help?

- Check logs: `tail -f backend/logs/app.log` (if logging configured)
- Check Celery logs in Terminal 3
- Visit http://localhost:8000/docs for API documentation
- Test connection: `python scripts/test_connection.py`

---

**You're almost there! Just 3 more credentials to add and you're ready to go! 🚀**



