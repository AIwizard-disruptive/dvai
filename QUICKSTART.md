# Quick Start Guide

Get your Meeting Intelligence Platform running in minutes.

## Prerequisites

- Python 3.11+
- Node.js 18+
- Redis (for Celery)
- Supabase account

## 1. Backend Setup (5 minutes)

### Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configure Environment

```bash
cp env.example .env
```

Edit `.env` with your credentials:

```env
# Supabase (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
DATABASE_URL=postgresql+asyncpg://postgres:password@db.xxx.supabase.co:5432/postgres

# Redis (Required)
REDIS_URL=redis://localhost:6379/0

# Generate encryption key
ENCRYPTION_KEY=$(python -c "import base64; import os; print(base64.b64encode(os.urandom(32)).decode())")

# At least one transcription provider (choose one)
KLANG_API_KEY=your-klang-key
# OR
MISTRAL_API_KEY=your-mistral-key  
# OR
OPENAI_API_KEY=your-openai-key

# For AI extraction (Required)
OPENAI_API_KEY=your-openai-key
```

### Run Database Migrations

```bash
python scripts/migrate.py
```

This creates all tables and RLS policies in your Supabase database.

### Start Services

Terminal 1 - FastAPI:
```bash
uvicorn app.main:app --reload --port 8000
```

Terminal 2 - Redis:
```bash
redis-server
```

Terminal 3 - Celery Worker:
```bash
celery -A app.worker.celery_app worker --loglevel=info
```

API is now running at http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## 2. Frontend Setup (3 minutes)

```bash
cd frontend
npm install
cp env.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start dev server:

```bash
npm run dev
```

Frontend is now running at http://localhost:3000

## 3. First Use

### Create an Account

1. Visit http://localhost:3000
2. Click "Sign Up"
3. Enter email and password
4. Verify email (if Supabase email is enabled)

### Create an Organization

```bash
curl -X POST http://localhost:8000/orgs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Company"}'
```

Save the `org_id` from the response.

### Upload Your First Meeting

#### Option A: Via API

```bash
curl -X POST http://localhost:8000/artifacts/upload \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" \
  -F "file=@meeting-recording.mp3"
```

#### Option B: Via UI

1. Go to http://localhost:3000/dashboard
2. Click "Upload Meeting"
3. Select audio file or Word document
4. Wait for processing (check status in dashboard)

### View Results

```bash
curl http://localhost:8000/meetings \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

Or visit the dashboard at http://localhost:3000/dashboard

## 4. Configure Integrations (Optional)

### Linear

1. Get your Linear API key from https://linear.app/settings/api
2. Add integration:

```bash
curl -X POST http://localhost:8000/integrations \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "linear",
    "secrets": {"api_key": "your-linear-key"},
    "config": {"team_id": "your-team-id"}
  }'
```

### Google (Gmail + Calendar)

1. Create OAuth credentials in Google Cloud Console
2. Add to your `.env`:

```env
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

3. Start OAuth flow:

Visit http://localhost:8000/integrations/google/oauth

## Troubleshooting

### "Module not found" errors

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Database connection errors

- Check your Supabase credentials
- Ensure database URL is correct (including `/postgres` suffix)
- Verify migrations ran successfully: `python scripts/migrate.py`

### RLS errors

- Ensure you're passing `X-Org-Id` header
- Check user is a member of the org
- Verify RLS policies were created (check Supabase dashboard)

### Celery not processing

- Check Redis is running: `redis-cli ping` (should return "PONG")
- Check Celery worker logs
- Verify `CELERY_BROKER_URL` in `.env`

### Transcription fails

- Verify you have at least one provider API key configured
- Check provider is set correctly: `DEFAULT_TRANSCRIPTION_PROVIDER`
- Review Celery worker logs for detailed errors

## Next Steps

- [Read full documentation](README.md)
- [Configure integrations](README.md#integrations)
- [Set up team members](README.md#organizations)
- [Review security settings](README.md#security)
- [Enable feature flags](README.md#feature-flags)

## Production Deployment

Before deploying to production:

1. **Security**:
   - Generate new `ENCRYPTION_KEY` (never reuse dev key)
   - Use strong database passwords
   - Enable HTTPS only
   - Review CORS settings

2. **Scaling**:
   - Use managed Redis (e.g., Upstash, Redis Cloud)
   - Increase Celery workers based on load
   - Configure database connection pooling

3. **Monitoring**:
   - Set up Sentry: `SENTRY_DSN`
   - Configure logging
   - Monitor Celery queue depth

4. **Feature Flags**:
   - Enable when ready: `ENABLE_EMAIL_SEND=true`
   - Enable when ready: `ENABLE_CALENDAR_BOOKING=true`

See [README.md](README.md) for detailed production deployment guide.





