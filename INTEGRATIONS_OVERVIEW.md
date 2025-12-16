# 🔗 Integrations Overview

Complete guide to all external integrations available in your Meeting Intelligence Platform.

## 📊 Integration Status

| Integration | Status | Documentation | Features |
|-------------|--------|---------------|----------|
| **OpenAI** | ✅ Configured | Built-in | Transcription, AI extraction |
| **Google Workspace** | 📝 Setup Ready | GOOGLE_INTEGRATION.md | Gmail drafts, Calendar events |
| **Linear** | 📝 Setup Ready | Below | Task sync |
| **Klang** | ⏳ Optional | Built-in | Transcription alternative |
| **Mistral** | ⏳ Optional | Built-in | Transcription alternative |

---

## 🤖 OpenAI (Active)

**Status**: ✅ Already configured with your API key

### What It Does
- **Transcription**: Audio → text with speaker detection (Whisper)
- **AI Extraction**: Summaries, decisions, action items (GPT-4)
- **Confidence Scores**: Quality metrics on every insight
- **Source Linking**: Every insight linked to transcript segment

### No Additional Setup Required
Your key is configured and ready to use!

### Usage
Automatically used when you upload meetings. No manual intervention needed.

---

## 📧 Google Workspace (Gmail + Calendar)

**Status**: 📝 Ready to configure (5 minutes)

### What It Does

**Gmail Integration**:
- ✅ Auto-create follow-up email drafts
- ✅ Include meeting summary, decisions, action items
- ✅ Add all participants automatically
- ✅ Link to full transcript
- ⚠️ Safe default: Drafts only (doesn't send)
- 🔓 Optional: Enable auto-send via feature flag

**Calendar Integration**:
- ✅ Create meeting proposals (review before booking)
- ✅ Suggest optimal follow-up times
- ✅ Add all participants as attendees
- ✅ Include meeting notes in description
- ⚠️ Safe default: Proposals only
- 🔓 Optional: Enable auto-booking via feature flag

### Quick Setup (5 min)

1. **Get credentials** from [Google Cloud Console](https://console.cloud.google.com/):
   - Create project
   - Enable Gmail API + Calendar API
   - Create OAuth credentials

2. **Add to `.env`**:
   ```env
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-secret
   ```

3. **Connect account**:
   ```bash
   open "http://localhost:8000/integrations/google/oauth?org_id=$ORG_ID"
   ```

### Documentation
- **Quick Start**: `GOOGLE_QUICKSTART.md` (5 min)
- **Full Guide**: `GOOGLE_INTEGRATION.md` (detailed)

### API Endpoints
```bash
# Create email draft
POST /sync/google/email/meeting/{meeting_id}

# Create calendar proposal
POST /sync/google/calendar/meeting/{meeting_id}

# List proposals
GET /calendar/proposals

# Approve proposal
POST /calendar/proposals/{id}/approve
```

---

## 📋 Linear

**Status**: 📝 Ready to configure (2 minutes)

### What It Does
- ✅ Sync action items → Linear issues
- ✅ Map owners to Linear users
- ✅ Set due dates and priorities
- ✅ Link back to meeting transcript
- ✅ Two-way sync (updates flow back)

### Quick Setup

1. **Get Linear API key**:
   - Go to [Linear Settings](https://linear.app/settings/api)
   - Create new API key
   - Copy the key

2. **Get Team ID**:
   ```bash
   # Use Linear GraphQL explorer or API
   # Find your team's ID
   ```

3. **Add via API**:
   ```bash
   curl -X POST http://localhost:8000/integrations \
     -H "Authorization: Bearer $TOKEN" \
     -H "X-Org-Id: $ORG_ID" \
     -H "Content-Type: application/json" \
     -d '{
       "provider": "linear",
       "secrets": {
         "api_key": "lin_api_xxx"
       },
       "config": {
         "team_id": "your-team-id"
       }
     }'
   ```

### Usage

**Automatic**: After meeting processing, action items auto-sync

**Manual**:
```bash
POST /sync/linear/meeting/{meeting_id}
```

### Status Mapping
| Meeting Status | Linear State |
|----------------|--------------|
| open | Todo |
| in_progress | In Progress |
| blocked | Blocked |
| done | Done |

### API Endpoints
```bash
# Sync meeting action items
POST /sync/linear/meeting/{meeting_id}

# Sync single action item
POST /action-items/{id}/sync-linear

# View Linear issues
GET /integrations/linear/issues
```

---

## 🎙️ Alternative Transcription Providers

### Klang API

**Status**: ⏳ Optional (if you have Klang API access)

**Advantages**:
- Native speaker diarization
- High accuracy
- Industry-specific models

**Setup**:
```env
KLANG_API_KEY=your-klang-key
KLANG_API_URL=https://api.klang.ai/v1
DEFAULT_TRANSCRIPTION_PROVIDER=klang
```

### Mistral API

**Status**: ⏳ Optional (alternative to OpenAI)

**Advantages**:
- Cost-effective
- European data residency
- Good multilingual support

**Setup**:
```env
MISTRAL_API_KEY=your-mistral-key
MISTRAL_API_URL=https://api.mistral.ai/v1
DEFAULT_TRANSCRIPTION_PROVIDER=mistral
```

---

## 🎯 Integration Workflow

### Complete Meeting Processing

```
1. Upload Meeting
   ↓
2. Transcribe (OpenAI/Klang/Mistral)
   ↓
3. Extract Intelligence (OpenAI GPT-4)
   ├─→ Summary
   ├─→ Decisions
   └─→ Action Items
   ↓
4. Sync Integrations (Parallel)
   ├─→ Linear (Create issues)
   ├─→ Gmail (Create draft)
   └─→ Calendar (Create proposal)
   ↓
5. Review & Approve
   ├─→ Edit draft in Gmail
   ├─→ Approve calendar proposal
   └─→ Update Linear issues
   ↓
6. Send/Book (Optional - Feature Flags)
   ├─→ Send email (ENABLE_EMAIL_SEND=true)
   └─→ Book meeting (ENABLE_CALENDAR_BOOKING=true)
```

---

## 🔐 Security & Privacy

### Token Storage
- All tokens encrypted at rest (pgcrypto)
- Server-side encryption key required
- Per-organization isolation (RLS)

### OAuth Scopes
Only request minimum required permissions:
- Gmail: `gmail.compose` + `gmail.send`
- Calendar: `calendar` + `calendar.events`
- Drive: `drive.file` (only files we create)

### Revocation
Users can revoke access anytime:
```bash
DELETE /integrations/{provider}
```

Or via provider's settings:
- Google: https://myaccount.google.com/permissions
- Linear: https://linear.app/settings/api

---

## 🚦 Feature Flags

Control integration behavior with environment variables:

```env
# Email Behavior
ENABLE_EMAIL_SEND=false    # false = drafts only (safe)
                           # true = auto-send emails

# Calendar Behavior  
ENABLE_CALENDAR_BOOKING=false  # false = proposals only (safe)
                               # true = auto-book events
```

**Recommendation**: Start with both `false`, test thoroughly, then enable.

---

## 📈 Usage Examples

### End-to-End Example

```bash
# 1. Upload meeting
curl -X POST http://localhost:8000/artifacts/upload \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" \
  -F "file=@board_meeting.mp3"

# 2. Wait for processing (~2-5 min depending on length)

# 3. Check results
MEETING_ID=$(curl http://localhost:8000/meetings \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" | jq -r '.[0].id')

# 4. View Gmail draft
# Go to https://mail.google.com → Drafts

# 5. View Linear issues
# Go to https://linear.app

# 6. Review calendar proposal
curl http://localhost:8000/calendar/proposals \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"

# 7. Approve calendar proposal
PROPOSAL_ID=$(curl http://localhost:8000/calendar/proposals \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" | jq -r '.[0].id')

curl -X POST http://localhost:8000/calendar/proposals/$PROPOSAL_ID/approve \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

---

## 🔧 Configuration Reference

### Environment Variables

```env
# ✅ Already Configured
OPENAI_API_KEY=sk-proj-xxx...
DEFAULT_TRANSCRIPTION_PROVIDER=openai

# 📝 Add These for Google
GOOGLE_CLIENT_ID=123-abc.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxx
GOOGLE_REDIRECT_URI=http://localhost:8000/integrations/google/callback

# 📝 Add These for Linear (optional)
LINEAR_API_KEY=lin_api_xxx

# ⏳ Add These for Alternative Transcription (optional)
KLANG_API_KEY=your-key
MISTRAL_API_KEY=your-key

# 🚦 Feature Flags (start with false)
ENABLE_EMAIL_SEND=false
ENABLE_CALENDAR_BOOKING=false
```

---

## 📚 Documentation Index

| Document | Purpose | Time |
|----------|---------|------|
| **GOOGLE_QUICKSTART.md** | Quick Google setup | 5 min |
| **GOOGLE_INTEGRATION.md** | Detailed Google guide | 15 min |
| **INTEGRATIONS_OVERVIEW.md** | This document | Reference |
| **README.md** | Complete platform docs | Full guide |
| **SETUP_NOW.md** | Initial setup | 5 min |

---

## ✅ Integration Checklist

### Core (Required)
- [x] OpenAI API key configured
- [x] Supabase connected
- [x] Backend running

### Google (Recommended)
- [ ] Google Cloud project created
- [ ] OAuth credentials obtained
- [ ] Credentials added to `.env`
- [ ] Google account connected
- [ ] Test email draft created
- [ ] Test calendar proposal created

### Linear (Optional)
- [ ] Linear API key obtained
- [ ] Team ID found
- [ ] Integration added via API
- [ ] Test issue synced

### Advanced (Optional)
- [ ] Alternative transcription provider configured
- [ ] Feature flags enabled (if desired)
- [ ] Custom email templates configured
- [ ] Smart meeting time suggestions enabled

---

## 🎯 Next Steps

1. **Start with Google**: Follow `GOOGLE_QUICKSTART.md` (5 min)
2. **Test the flow**: Upload a meeting, review drafts
3. **Add Linear**: Sync action items to your workflow
4. **Enable auto-actions**: When ready, flip feature flags
5. **Customize**: Modify templates and behavior

---

## 💡 Pro Tips

- **Start conservative**: Use drafts/proposals, not auto-send/book
- **Test thoroughly**: Use test meetings before production
- **Review outputs**: AI is smart but not perfect - review before sending
- **Customize templates**: Adjust email/calendar formats to your style
- **Monitor usage**: Watch OpenAI API costs with heavy use

---

**Ready to connect your tools? Start with GOOGLE_QUICKSTART.md! 🚀**



