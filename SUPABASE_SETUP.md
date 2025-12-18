# Supabase Setup Guide

## Getting Your Credentials

You've provided:
- **URL**: `https://gqpupmuzriqarmrsuwev.supabase.co`
- **Anon Key**: `sb_publishable_-X1shl13fQAH68_E-bz7ww_cDCitgVM`

You still need to get these from the Supabase Dashboard:

### 1. Get Service Role Key & JWT Secret

1. Go to https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/settings/api
2. Find these values:
   - **service_role key** (secret) - needed for migrations and bypassing RLS
   - **JWT Secret** - needed for token validation

### 2. Get Database Password

1. Go to https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/settings/database
2. Find your database password (or reset it)
3. Your connection string format:
   ```
   postgresql+asyncpg://postgres.gqpupmuzriqarmrsuwev:YOUR_PASSWORD@aws-0-us-east-1.pooler.supabase.com:5432/postgres
   ```

### 3. Update Configuration

Edit `backend/.env.production` with your credentials:

```bash
cd backend
cp .env.production .env
nano .env  # or use your favorite editor
```

Update these lines:
```env
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...  # From step 1
SUPABASE_JWT_SECRET=your-jwt-secret    # From step 1
DATABASE_URL=postgresql+asyncpg://postgres.gqpupmuzriqarmrsuwev:YOUR_PASSWORD@aws-0-us-east-1.pooler.supabase.com:5432/postgres
```

### 4. Generate Encryption Key

```bash
python -c "import base64; import os; print(base64.b64encode(os.urandom(32)).decode())"
```

Add to `.env`:
```env
ENCRYPTION_KEY=<generated-key>
```

### 5. Add at least one API key

For testing, add OpenAI key:
```env
OPENAI_API_KEY=sk-...
DEFAULT_TRANSCRIPTION_PROVIDER=openai
```

## Test Connection

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/test_connection.py
```

This will:
- ✓ Test PostgreSQL connection
- ✓ Test Supabase client
- ✓ Try to create a test organization
- ✓ Show your configuration status

## Run Migrations

Once connection test passes:

```bash
python scripts/migrate.py
```

This creates:
- All tables with multi-tenant schema
- Row Level Security policies
- Indexes and triggers

## Verify in Supabase Dashboard

1. Go to Table Editor: https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/editor
2. You should see these tables:
   - `orgs`
   - `org_memberships`
   - `meetings`
   - `artifacts`
   - `transcript_chunks`
   - `action_items`
   - `decisions`
   - And more...

## Create Your First User

### Option A: Via Supabase Dashboard

1. Go to Authentication: https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/auth/users
2. Click "Add user" → "Create new user"
3. Enter email and password
4. Copy the user ID

### Option B: Via SQL

```sql
-- In Supabase SQL Editor
-- This creates a user in auth.users
-- (Better to use the dashboard for this)
```

## Create Your First Organization

```bash
# Get a user token first (login via frontend or Supabase dashboard)
# Then create org via API:

curl -X POST http://localhost:8000/orgs \
  -H "Authorization: Bearer $YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Organization"}'
```

## API Access via Shell

### Using curl

```bash
# Health check (no auth needed)
curl http://localhost:8000/health

# List orgs (needs auth + token)
curl http://localhost:8000/orgs \
  -H "Authorization: Bearer $TOKEN"

# Upload artifact
curl -X POST http://localhost:8000/artifacts/upload \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" \
  -F "file=@meeting.mp3"
```

### Using Python

```python
import requests

API_URL = "http://localhost:8000"
TOKEN = "your-supabase-jwt-token"
ORG_ID = "your-org-id"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-Org-Id": ORG_ID,
}

# List meetings
response = requests.get(f"{API_URL}/meetings", headers=headers)
print(response.json())

# Upload file
files = {"file": open("meeting.mp3", "rb")}
response = requests.post(
    f"{API_URL}/artifacts/upload",
    headers=headers,
    files=files,
)
print(response.json())
```

### Direct Database Access

```python
from supabase import create_client

supabase = create_client(
    "https://gqpupmuzriqarmrsuwev.supabase.co",
    "sb_publishable_-X1shl13fQAH68_E-bz7ww_cDCitgVM"
)

# Note: This will fail with RLS unless authenticated
# Use service_role key to bypass RLS (be careful!)

# Query orgs
response = supabase.table('orgs').select("*").execute()
print(response.data)
```

## Troubleshooting

### "relation does not exist"
→ Run migrations: `python scripts/migrate.py`

### "permission denied"
→ Check you're using service_role key for migrations
→ Check user has org membership for queries

### "connection refused"
→ Check DATABASE_URL is correct
→ Check Supabase project is not paused

### RLS blocking queries
→ This is expected! RLS protects tenant data
→ Use service_role key to bypass (admin only)
→ Or authenticate properly and pass org_id

## Next Steps

1. ✓ Run connection test
2. ✓ Run migrations
3. ✓ Create first user (Supabase dashboard)
4. ✓ Create first org (API)
5. ✓ Upload test meeting
6. ✓ View results in dashboard

## Quick Reference

| Resource | URL |
|----------|-----|
| Project Dashboard | https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev |
| API Settings | https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/settings/api |
| Database Settings | https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/settings/database |
| Table Editor | https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/editor |
| Auth Users | https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/auth/users |
| SQL Editor | https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/sql |





