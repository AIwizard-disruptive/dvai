# Meeting Intelligence Platform

A production-ready multi-tenant application that transforms meetings into actionable intelligence.

## Features

- 🎤 **Multi-source Ingestion**: Upload Word documents and audio files
- 🔊 **Transcription**: Pluggable providers (Klang, Mistral, OpenAI)
- 🧠 **AI Extraction**: Structured summaries, decisions, and action items
- 🔗 **Integrations**: Linear (tasks), Gmail (follow-ups), Google Calendar (bookings)
- 🏢 **Multi-tenant**: Strict org isolation with Row Level Security
- 🔍 **Provenance**: Every insight linked to source quotes

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Frontend   │────▶│   FastAPI    │────▶│  Supabase   │
│  Next.js    │     │   Backend    │     │  Postgres   │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
                    ┌──────▼───────┐
                    │    Celery    │
                    │   Workers    │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼────┐    ┌──────▼─────┐   ┌─────▼──────┐
    │  Klang   │    │   Linear   │   │   Google   │
    │ Mistral  │    │    API     │   │  Workspace │
    │  OpenAI  │    └────────────┘   └────────────┘
    └──────────┘
```

## Tech Stack

### Backend
- **API**: FastAPI (async), Pydantic v2, uvicorn
- **Database**: Supabase Postgres (SQLAlchemy 2.0 + asyncpg)
- **Storage**: Supabase Storage
- **Workers**: Celery + Redis
- **Auth**: Supabase Auth (JWT)

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI**: shadcn/ui + Tailwind CSS
- **State**: React Query
- **Auth**: Supabase client

### Integrations
- Klang API (transcription)
- Mistral API (transcription)
- OpenAI API (transcription + extraction)
- Linear API (task sync)
- Google Gmail API (follow-ups)
- Google Calendar API (bookings)

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Redis
- Supabase project

### 1. Clone and Setup

```bash
git clone <repository-url>
cd dv
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required environment variables:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
DATABASE_URL=postgresql+asyncpg://postgres:password@db.xxx.supabase.co:5432/postgres

# Redis
REDIS_URL=redis://localhost:6379/0

# Transcription
KLANG_API_KEY=your-klang-key
MISTRAL_API_KEY=your-mistral-key
OPENAI_API_KEY=your-openai-key

# Integrations
LINEAR_API_KEY=your-linear-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Security
ENCRYPTION_KEY=your-32-byte-base64-key

# Feature Flags
ENABLE_EMAIL_SEND=false
ENABLE_CALENDAR_BOOKING=false
```

### 3. Database Setup

Run migrations:

```bash
cd backend
python -m scripts.migrate
```

This creates:
- Multi-tenant schema with `orgs` and `org_memberships`
- Meeting intelligence tables with `org_id` columns
- RLS policies for all tenant-scoped tables

### 4. Start Backend Services

Terminal 1 - API:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Terminal 2 - Celery Worker:
```bash
cd backend
source venv/bin/activate
celery -A app.worker.celery_app worker --loglevel=info
```

Terminal 3 - Redis:
```bash
redis-server
```

### 5. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
```

Configure `.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start dev server:

```bash
npm run dev
```

Visit http://localhost:3000

## Usage

### 1. Organization Setup

Create an organization and invite members:

```bash
# Via API
curl -X POST http://localhost:8000/orgs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Acme Corp"}'
```

### 2. Configure Integrations

Navigate to Settings → Integrations and add:
- Linear API key
- Google OAuth credentials
- Transcription provider keys

### 3. Upload Meeting Artifact

```bash
# Upload a file
curl -X POST http://localhost:8000/artifacts/upload \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" \
  -F "file=@meeting-recording.mp3"
```

### 4. Process Meeting

The pipeline runs automatically:
1. **Ingest**: Store file in Supabase Storage
2. **Transcribe**: Convert audio to text (Klang/Mistral/OpenAI)
3. **Extract**: Generate summaries, decisions, action items (OpenAI)
4. **Sync**: Push to Linear, Gmail, Calendar

### 5. View Results

```bash
# Get meeting details
curl http://localhost:8000/meetings/$MEETING_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

Response includes:
- Transcript with speaker diarization
- Summary
- Decisions with source quotes
- Action items with Linear sync status

## Pipeline Stages

### Stage 1: Ingestion
- Store in Supabase Storage: `orgs/{org_id}/artifacts/{artifact_id}/{filename}`
- Calculate SHA-256 for deduplication
- Parse filename heuristics (date, participants, company)

### Stage 2: Transcription
- **Audio files**: Send to Klang/Mistral/OpenAI
- **Word docs**: Extract text with python-docx
- Store chunks with speaker labels, timestamps, confidence

### Stage 3: LLM Extraction
OpenAI with strict JSON schema:
```json
{
  "summary_md": "Meeting overview...",
  "decisions": [
    {
      "decision": "Decided to...",
      "rationale": "Because...",
      "confidence": "high",
      "source_chunk_indices": [5, 6]
    }
  ],
  "action_items": [
    {
      "title": "Complete design",
      "description": "...",
      "owner_name": "Alice",
      "due_date": "2025-12-20",
      "status": "open",
      "confidence": "high",
      "source_chunk_indices": [12]
    }
  ],
  "tags": ["product", "design"],
  "entities": [{"kind": "person", "name": "Alice"}]
}
```

### Stage 4: Sync Integrations

**Linear**: Create issues for action items
- Upsert using `external_refs` for idempotency
- Map statuses: `open` → `Todo`, `in_progress` → `In Progress`

**Gmail**: Generate follow-up emails
- Default: Create draft (store `gmail_draft` ID)
- Feature flag: Send email

**Google Calendar**: Create meeting proposals
- Default: Store as `calendar_proposal` in `external_refs`
- Feature flag: Create actual event with invites

## Multi-tenancy & Security

### Row Level Security (RLS)

All tenant-scoped tables enforce:

```sql
-- Users can only access their org's data
CREATE POLICY org_isolation ON meetings
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM org_memberships
      WHERE org_id = meetings.org_id
      AND user_id = auth.uid()
    )
  );
```

### Org Context

Every request requires:
- `Authorization: Bearer <supabase-jwt>` header
- `X-Org-Id: <org-id>` header

Backend validates:
1. JWT is valid (Supabase Auth)
2. User is a member of specified org
3. User has required role for operation

### Roles

- **viewer**: Read-only access
- **member**: Can create meetings, run pipeline
- **admin**: Can manage integrations, invite users
- **owner**: Full control including billing

### Secrets Management

API keys and OAuth tokens encrypted at rest:
- Postgres `pgcrypto` extension
- Server-side encryption key (32-byte)
- Separate secrets table with encrypted column

## API Reference

### Authentication

All endpoints require Supabase JWT + org context:

```bash
Authorization: Bearer <supabase-jwt>
X-Org-Id: <org-uuid>
```

### Endpoints

#### Artifacts

```
POST   /artifacts/upload           Upload file (returns signed URL)
GET    /artifacts                  List artifacts
GET    /artifacts/{id}             Get artifact details
DELETE /artifacts/{id}             Delete artifact
```

#### Meetings

```
GET    /meetings                   List meetings (paginated)
POST   /meetings                   Create meeting manually
GET    /meetings/{id}              Get meeting with full details
PATCH  /meetings/{id}              Update meeting metadata
DELETE /meetings/{id}              Delete meeting
POST   /meetings/{id}/process      Trigger processing pipeline
```

#### Action Items

```
GET    /action-items               List action items
PATCH  /action-items/{id}          Update status/owner/due date
POST   /action-items/{id}/sync-linear   Manual Linear sync
```

#### Decisions

```
GET    /decisions                  List decisions
GET    /decisions/{id}             Get decision with source quotes
```

#### Sync

```
POST   /sync/linear/meeting/{id}            Sync all action items to Linear
POST   /sync/google/email/meeting/{id}      Generate follow-up email
POST   /sync/google/calendar/meeting/{id}   Create calendar event
```

#### Organizations

```
GET    /orgs                       List user's orgs
POST   /orgs                       Create org (user becomes owner)
GET    /orgs/{id}                  Get org details
PATCH  /orgs/{id}                  Update org settings (admin+)
```

#### Memberships

```
GET    /orgs/{org_id}/members      List org members
POST   /orgs/{org_id}/invites      Invite user (admin+)
DELETE /orgs/{org_id}/members/{id} Remove member (admin+)
PATCH  /orgs/{org_id}/members/{id} Update member role (owner only)
```

#### Integrations

```
GET    /integrations               List org integrations
POST   /integrations               Add integration
PATCH  /integrations/{id}          Update integration config
DELETE /integrations/{id}          Remove integration
GET    /integrations/google/oauth  Start Google OAuth flow
GET    /integrations/google/callback  OAuth callback
```

## Testing

### Run All Tests

```bash
cd backend
pytest
```

### Test Categories

**Unit Tests**: Provider adapters, extraction logic
```bash
pytest tests/unit/
```

**Integration Tests**: API endpoints, database operations
```bash
pytest tests/integration/
```

**RLS Tests**: Policy enforcement
```bash
pytest tests/security/
```

### Key Test Files

- `tests/unit/test_docx_extraction.py`: Word document parsing
- `tests/unit/test_transcription_adapters.py`: Klang/Mistral/OpenAI contracts
- `tests/unit/test_extraction_schema.py`: LLM output validation
- `tests/security/test_rls_policies.py`: Multi-tenant isolation
- `tests/integration/test_pipeline.py`: End-to-end processing

## Development

### Project Structure

```
dv/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Settings
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models/              # SQLAlchemy models
│   │   ├── api/                 # FastAPI routes
│   │   ├── services/            # Business logic
│   │   ├── providers/           # Transcription adapters
│   │   ├── integrations/        # External APIs
│   │   ├── middleware/          # Auth, org context
│   │   └── worker/              # Celery tasks
│   ├── migrations/              # Database migrations
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── app/                     # Next.js app router
│   ├── components/              # React components
│   ├── lib/                     # Utilities
│   └── package.json
└── README.md
```

### Adding a New Transcription Provider

1. Implement the `TranscriptionProvider` interface:

```python
class NewProvider(TranscriptionProvider):
    async def transcribe(
        self,
        file_url: str,
        language_hint: Optional[str] = None
    ) -> TranscriptionResult:
        # Implementation
        pass
```

2. Register in `app/providers/__init__.py`

3. Add configuration to `app/config.py`

4. Add tests in `tests/unit/test_transcription_adapters.py`

### Adding a New Integration

1. Create adapter in `app/integrations/your_service.py`
2. Add config to `integrations` table schema
3. Implement sync task in `app/worker/tasks/sync.py`
4. Add API endpoint in `app/api/sync.py`

## Deployment

### Production Checklist

- [ ] Set strong `ENCRYPTION_KEY` (32 random bytes, base64-encoded)
- [ ] Use production Supabase project
- [ ] Configure Redis with persistence
- [ ] Set up SSL/TLS for API
- [ ] Enable CORS for frontend domain only
- [ ] Configure logging and monitoring
- [ ] Set up backup strategy for Postgres
- [ ] Review and test all RLS policies
- [ ] Rate limit API endpoints
- [ ] Set up error tracking (Sentry)

### Environment-specific Settings

**Production**: 
- `DEBUG=false`
- `ENABLE_EMAIL_SEND=true` (when ready)
- `ENABLE_CALENDAR_BOOKING=true` (when ready)

**Staging**: 
- `DEBUG=false`
- Feature flags = `false`

**Development**: 
- `DEBUG=true`
- Feature flags = `false`

## Troubleshooting

### Pipeline Failures

Check processing runs:
```bash
curl http://localhost:8000/meetings/$MEETING_ID/runs \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

View Celery logs:
```bash
celery -A app.worker.celery_app inspect active
celery -A app.worker.celery_app inspect stats
```

### RLS Issues

Test policy enforcement:
```sql
-- Connect as specific user
SET request.jwt.claims = '{"sub": "user-uuid"}';
SELECT * FROM meetings;  -- Should only return user's org data
```

### Integration Errors

Check integration status:
```bash
curl http://localhost:8000/integrations \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

Test connection:
```bash
curl -X POST http://localhost:8000/integrations/test/linear \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## License

MIT

## Support

- Documentation: [docs/](docs/)
- Issues: GitHub Issues
- Email: support@example.com




