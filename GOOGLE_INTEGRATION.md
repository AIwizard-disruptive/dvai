# Google Workspace Integration Guide

Complete guide to integrating Gmail, Google Calendar, and Google Drive/Docs with your Meeting Intelligence Platform.

## 🎯 What You Can Do with Google Integration

Once configured, the platform will:

### 📧 Gmail Integration
- ✅ **Create email drafts** with meeting summaries, decisions, and action items
- ✅ **Send follow-up emails** automatically (optional, via feature flag)
- ✅ **Include all attendees** with proper formatting
- ✅ **Link to source quotes** for every insight

### 📅 Calendar Integration
- ✅ **Create calendar events** for follow-up meetings
- ✅ **Add all participants** as attendees
- ✅ **Include meeting notes** in event description
- ✅ **Send invites** automatically (optional, via feature flag)
- ✅ **Propose meeting times** based on action items

### 📄 Google Docs Integration (Future)
- ✅ **Export meeting notes** as Google Docs
- ✅ **Share docs** with participants
- ✅ **Create collaborative agendas**

---

## 📋 Prerequisites

- Google Cloud account (free tier works)
- Access to Google Cloud Console
- Your Supabase backend running
- Admin access to create OAuth credentials

---

## 🚀 Setup Guide (15 minutes)

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"New Project"** (top navigation)
3. Enter project details:
   - **Name**: `Meeting Intelligence Platform`
   - **Organization**: (your org or leave default)
4. Click **"Create"**
5. Wait for project to be created (~30 seconds)
6. Select your new project from the dropdown

### Step 2: Enable Required APIs

1. Go to **APIs & Services** → **Library**
2. Search and enable these APIs (click "Enable" for each):

   **Required APIs:**
   - ✅ **Gmail API** - For email drafts and sending
   - ✅ **Google Calendar API** - For calendar events
   - ✅ **Google Drive API** - For docs (future)
   - ✅ **Google People API** - For contact info

3. Each will take a few seconds to enable

### Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose **External** (unless you have Google Workspace)
3. Click **"Create"**

4. Fill in **App Information**:
   - **App name**: `Meeting Intelligence Platform`
   - **User support email**: (your email)
   - **App logo**: (optional)
   - **Application home page**: `http://localhost:8000` (or your domain)
   - **Application privacy policy**: (optional for development)
   - **Application terms of service**: (optional for development)
   - **Authorized domains**: Add `localhost` for development
   - **Developer contact**: (your email)

5. Click **"Save and Continue"**

6. **Add Scopes** (click "Add or Remove Scopes"):
   ```
   https://www.googleapis.com/auth/gmail.compose
   https://www.googleapis.com/auth/gmail.send
   https://www.googleapis.com/auth/calendar
   https://www.googleapis.com/auth/calendar.events
   https://www.googleapis.com/auth/drive.file
   https://www.googleapis.com/auth/userinfo.email
   https://www.googleapis.com/auth/userinfo.profile
   ```

   Or check these boxes:
   - Gmail API: `.../auth/gmail.compose` (Create drafts)
   - Gmail API: `.../auth/gmail.send` (Send emails)
   - Calendar API: `.../auth/calendar` (Full calendar access)
   - Calendar API: `.../auth/calendar.events` (Manage events)
   - Drive API: `.../auth/drive.file` (Create/manage files)

7. Click **"Update"** → **"Save and Continue"**

8. **Add Test Users** (for development):
   - Click **"Add Users"**
   - Add your email and any team members who will test
   - Click **"Save and Continue"**

9. Review and click **"Back to Dashboard"**

### Step 4: Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. Configure:
   - **Application type**: `Web application`
   - **Name**: `Meeting Intelligence Backend`
   
4. **Authorized JavaScript origins**:
   ```
   http://localhost:8000
   http://localhost:3000
   ```
   (Add your production domain later)

5. **Authorized redirect URIs**:
   ```
   http://localhost:8000/integrations/google/callback
   http://localhost:3000/auth/google/callback
   ```
   (Add your production URLs later)

6. Click **"Create"**

7. **Save Your Credentials**:
   - Copy the **Client ID** (looks like: `123456789-abc123.apps.googleusercontent.com`)
   - Copy the **Client Secret** (looks like: `GOCSPX-abc123...`)
   - Click **"Download JSON"** (backup)

### Step 5: Configure Your Application

Add to `backend/.env`:

```env
# Google OAuth
GOOGLE_CLIENT_ID=123456789-abc123def456.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8000/integrations/google/callback

# Feature Flags (start with false for safety)
ENABLE_EMAIL_SEND=false
ENABLE_CALENDAR_BOOKING=false
```

**Important**: Keep `ENABLE_EMAIL_SEND=false` until you're ready to actually send emails!

---

## 🔐 Connecting Your Google Account

### Option 1: Via API (Backend)

1. **Start your backend**:
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. **Initiate OAuth flow**:
   ```bash
   # This opens your browser to Google's consent screen
   open "http://localhost:8000/integrations/google/oauth?org_id=YOUR_ORG_ID"
   ```

3. **Authorize the app**:
   - Log in to your Google account
   - Review permissions
   - Click **"Allow"**

4. **Get redirected back** to your app with access token

### Option 2: Via Frontend (Recommended)

Once your frontend is running:

1. Go to `http://localhost:3000/dashboard/settings`
2. Click **"Connect Google Account"**
3. Follow OAuth flow
4. Tokens stored securely in your database

### Testing the Connection

```bash
# Test if tokens are stored
curl http://localhost:8000/integrations \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"

# Should show Google integration with "enabled: true"
```

---

## 📧 Using Gmail Integration

### Automatic Draft Creation

After a meeting is processed, the system automatically creates a draft:

```python
# This happens automatically in the pipeline
# See: backend/app/worker/tasks/pipeline.py

# Draft includes:
# - Meeting summary
# - Key decisions with source quotes
# - Action items with assignees
# - Links back to full transcript
```

### Manual Email Creation

```bash
curl -X POST http://localhost:8000/sync/google/email/meeting/$MEETING_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

Response:
```json
{
  "status": "queued",
  "draft_id": "draft_abc123",
  "message": "Email draft created in your Gmail"
}
```

### View Draft in Gmail

1. Go to [Gmail](https://mail.google.com)
2. Click **"Drafts"** in left sidebar
3. Find draft with subject: `Follow-up: [Meeting Title]`
4. Review, edit, and send manually

### Enable Automatic Sending (Careful!)

Only when you're ready to actually send emails:

```env
# In backend/.env
ENABLE_EMAIL_SEND=true
```

Then restart your backend. Now emails will be sent automatically instead of saved as drafts.

---

## 📅 Using Calendar Integration

### Automatic Event Creation

When action items have due dates or follow-up meetings are mentioned:

```bash
curl -X POST http://localhost:8000/sync/google/calendar/meeting/$MEETING_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

### What Gets Created

**Calendar Event includes**:
- **Title**: "Follow-up: [Meeting Topic]"
- **Date/Time**: Based on action item due dates or AI-suggested times
- **Attendees**: All meeting participants
- **Description**: 
  ```
  Meeting Summary
  
  Decisions:
  - [Decision 1]
  - [Decision 2]
  
  Action Items:
  - [ ] Task 1 (@owner)
  - [ ] Task 2 (@owner)
  
  View full transcript: [link]
  ```

### Calendar Proposals (Default Mode)

By default, events are saved as "proposals" in your database:

```bash
# View proposals
curl http://localhost:8000/calendar-proposals \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"

# Approve a proposal to create actual event
curl -X POST http://localhost:8000/calendar-proposals/$PROPOSAL_ID/approve \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

### Enable Automatic Booking (Careful!)

Only enable when you want events automatically created:

```env
# In backend/.env
ENABLE_CALENDAR_BOOKING=true
```

Restart backend, and now events will be created immediately.

---

## 🔧 Advanced Configuration

### Custom Email Templates

Edit the email generation in `backend/app/worker/tasks/sync.py`:

```python
async def generate_follow_up_email(meeting_id: uuid.UUID):
    """Generate follow-up email content."""
    # Customize subject line
    subject = f"Follow-up: {meeting.title}"
    
    # Customize email body
    body_html = f"""
    <html>
      <body>
        <h2>Meeting Summary</h2>
        <p>{summary.content_md}</p>
        
        <h3>Key Decisions</h3>
        <ul>
          {decisions_html}
        </ul>
        
        <h3>Action Items</h3>
        <ul>
          {action_items_html}
        </ul>
        
        <p><a href="{meeting_url}">View full transcript</a></p>
      </body>
    </html>
    """
```

### Custom Calendar Event Details

Edit event creation in `backend/app/integrations/google_client.py`:

```python
# Customize event details
event = {
    "summary": f"Follow-up: {meeting.title}",
    "description": custom_description,
    "start": {
        "dateTime": start_time.isoformat(),
        "timeZone": "America/Los_Angeles",  # Your timezone
    },
    # Add conferencing (Meet link)
    "conferenceData": {
        "createRequest": {"requestId": f"meet-{meeting_id}"}
    },
    # Add reminders
    "reminders": {
        "useDefault": False,
        "overrides": [
            {"method": "email", "minutes": 24 * 60},
            {"method": "popup", "minutes": 30},
        ],
    },
}
```

### Smart Meeting Time Suggestions

The AI can suggest optimal meeting times based on:
- Action item due dates
- Mentioned timeframes in transcript
- Historical meeting patterns

Enable in `backend/app/services/extraction.py`:

```python
# Add to extraction schema
suggested_follow_ups: list[FollowUpMeeting] = Field(
    default_factory=list,
    description="Suggested follow-up meetings with proposed times"
)
```

---

## 📄 Google Docs Export (Coming Soon)

### Export Meeting as Google Doc

```python
# Future functionality
async def export_to_google_doc(meeting_id: uuid.UUID):
    """Export meeting as formatted Google Doc."""
    
    # Create doc
    doc = drive_service.files().create(
        body={
            "name": f"Meeting Notes - {meeting.title}",
            "mimeType": "application/vnd.google-apps.document"
        }
    ).execute()
    
    # Add content with formatting
    requests = [
        {
            "insertText": {
                "location": {"index": 1},
                "text": meeting_content
            }
        }
    ]
    
    # Share with participants
    for participant in participants:
        drive_service.permissions().create(
            fileId=doc["id"],
            body={"type": "user", "role": "writer", "emailAddress": participant.email}
        ).execute()
```

---

## 🔒 Security Best Practices

### Token Storage

Tokens are encrypted in your database:
```python
# Stored in integrations table
# secrets_encrypted contains:
{
    "access_token": "ya29.a0...",
    "refresh_token": "1//0g...",
    "token_expiry": "2025-12-13T10:00:00Z"
}
```

### Token Refresh

Tokens auto-refresh when expired:
```python
if credentials.expired:
    credentials.refresh(Request())
    # Update in database
```

### Revoke Access

Users can revoke access:
```bash
curl -X DELETE http://localhost:8000/integrations/google \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

Or via Google: https://myaccount.google.com/permissions

---

## 🧪 Testing

### Test Email Draft Creation

```bash
# Process a test meeting
curl -X POST http://localhost:8000/artifacts/upload \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" \
  -F "file=@test_meeting.mp3"

# Wait for processing to complete
# Check Gmail drafts - should see a new draft
```

### Test Calendar Event

```bash
# Create calendar proposal
curl -X POST http://localhost:8000/sync/google/calendar/meeting/$MEETING_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"

# Check Google Calendar - should see new event (if auto-booking enabled)
# Or check proposals in your app
```

### Verify Scopes

```bash
# Check what permissions you've granted
curl http://localhost:8000/integrations/google/scopes \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"
```

---

## 🐛 Troubleshooting

### "Access blocked: This app hasn't been verified"

**Solution**: Add yourself as a test user
1. Go to OAuth consent screen
2. Add test users
3. Try again

### "Redirect URI mismatch"

**Solution**: Check your redirect URI matches exactly
```env
GOOGLE_REDIRECT_URI=http://localhost:8000/integrations/google/callback
```

Must match what's in Google Cloud Console → Credentials

### "Invalid grant: Token has been expired or revoked"

**Solution**: Re-authenticate
```bash
# Delete old tokens
curl -X DELETE http://localhost:8000/integrations/google

# Re-connect
open http://localhost:8000/integrations/google/oauth?org_id=$ORG_ID
```

### "Insufficient permissions"

**Solution**: Add more scopes
1. Update OAuth consent screen with new scopes
2. Re-authenticate to get new permissions

### Emails/Events Not Creating

**Check**:
1. Feature flags: `ENABLE_EMAIL_SEND`, `ENABLE_CALENDAR_BOOKING`
2. Integration connected: `GET /integrations`
3. Token not expired
4. Check Celery logs for errors

---

## 📊 Usage Examples

### Complete Workflow Example

```bash
# 1. Upload meeting
ARTIFACT_ID=$(curl -X POST http://localhost:8000/artifacts/upload \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" \
  -F "file=@board_meeting.mp3" | jq -r '.id')

# 2. Wait for processing (check status)
curl http://localhost:8000/artifacts/$ARTIFACT_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"

# 3. Get meeting ID
MEETING_ID=$(curl http://localhost:8000/meetings \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" | jq -r '.[0].id')

# 4. Create email draft
curl -X POST http://localhost:8000/sync/google/email/meeting/$MEETING_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"

# 5. Create calendar event
curl -X POST http://localhost:8000/sync/google/calendar/meeting/$MEETING_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID"

# 6. Check Gmail for draft
# 7. Check Google Calendar for event
```

---

## 🎯 Next Steps

1. ✅ Complete OAuth setup (above)
2. ✅ Connect your Google account
3. ✅ Process a test meeting
4. ✅ Review draft email in Gmail
5. ✅ Review calendar proposal
6. ⚠️ Enable auto-send/booking (when ready)
7. 🚀 Use in production!

---

## 📚 Additional Resources

- [Google OAuth 2.0 Docs](https://developers.google.com/identity/protocols/oauth2)
- [Gmail API Reference](https://developers.google.com/gmail/api)
- [Calendar API Reference](https://developers.google.com/calendar/api)
- [Google Drive API Reference](https://developers.google.com/drive/api)

---

## ⚡ Quick Reference

| Action | Endpoint | Method |
|--------|----------|--------|
| Connect Google | `/integrations/google/oauth` | GET |
| Create email draft | `/sync/google/email/meeting/{id}` | POST |
| Create calendar event | `/sync/google/calendar/meeting/{id}` | POST |
| List integrations | `/integrations` | GET |
| Remove integration | `/integrations/google` | DELETE |

---

**You're ready to integrate Google Workspace! 🚀**

Start with OAuth setup, then test with email drafts before enabling auto-send.





