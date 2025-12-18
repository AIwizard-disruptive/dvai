# AI Meeting Agenda Generator with Google Calendar Sync

## 🎯 Overview

**NEW FEATURE**: Create meetings with AI-generated agendas that automatically sync to Google Calendar!

This system allows you to:
1. ✅ Input meeting name + description
2. ✅ AI generates comprehensive agenda with:
   - Discussion topics with time estimates
   - Expected decisions to make
   - Proposed next steps
   - Preparation notes
3. ✅ Automatically creates Google Calendar event with the agenda in the description
4. ✅ Sends calendar invites to attendees (optional)

## 🚀 Quick Start

### 1. Create a Meeting with AI Agenda

```bash
curl -X POST http://localhost:8000/meetings/with-agenda \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_name": "Q1 2025 Planning Meeting",
    "meeting_description": "We need to finalize our Q1 roadmap, decide on resource allocation for the new product launch, and establish clear success metrics for the quarter. Key stakeholders from engineering, product, and marketing will attend.",
    "start_time": "2025-01-15T10:00:00Z",
    "duration_minutes": 90,
    "location": "Conference Room A (or Zoom link)",
    "attendee_emails": [
      "alice@company.com",
      "bob@company.com",
      "charlie@company.com"
    ],
    "create_calendar_event": true,
    "send_invites": true,
    "meeting_type": "planning",
    "company_context": "Tech startup preparing for Series A launch"
  }'
```

### 2. Response

```json
{
  "meeting_id": "123e4567-e89b-12d3-a456-426614174000",
  "meeting_name": "Q1 2025 Planning Meeting",
  "agenda": {
    "meeting_objective": "Finalize Q1 2025 roadmap, allocate resources for product launch, and establish success metrics",
    "agenda_topics": [
      {
        "topic": "Review current product development status",
        "duration_minutes": 15,
        "owner": "alice@company.com"
      },
      {
        "topic": "Discuss resource allocation for new product launch",
        "duration_minutes": 30,
        "owner": null
      },
      {
        "topic": "Define Q1 success metrics and KPIs",
        "duration_minutes": 25,
        "owner": "bob@company.com"
      },
      {
        "topic": "Finalize timeline and milestones",
        "duration_minutes": 20,
        "owner": null
      }
    ],
    "expected_decisions": [
      {
        "decision_point": "Resource allocation for product launch",
        "context": "Need to decide how many engineers and designers to assign to the new product",
        "options": [
          "Dedicate 50% of engineering team",
          "Hire additional contractors",
          "Shift resources from maintenance work"
        ]
      },
      {
        "decision_point": "Q1 success metrics",
        "context": "Define measurable outcomes to track quarterly progress",
        "options": [
          "User acquisition targets",
          "Revenue milestones",
          "Product feature completion"
        ]
      }
    ],
    "proposed_next_steps": [
      {
        "action": "Prepare detailed resource allocation proposal",
        "owner": "alice@company.com",
        "timeline": "by end of week"
      },
      {
        "action": "Draft Q1 OKRs document",
        "owner": "bob@company.com",
        "timeline": "within 3 days"
      },
      {
        "action": "Schedule follow-up check-in meeting",
        "owner": null,
        "timeline": "within 2 weeks"
      }
    ],
    "suggested_duration_minutes": 90,
    "preparation_notes": [
      "Review current sprint progress and backlog",
      "Prepare budget estimates for Q1",
      "Come with 3 potential success metrics per department"
    ]
  },
  "agenda_markdown": "# Meeting Agenda\n\n## Objective\n...",
  "calendar_event_id": null,
  "calendar_event_link": null,
  "status": "queued_calendar_event"
}
```

### 3. What Happens Next

1. ✅ **Meeting record created** in database with full agenda
2. ✅ **Calendar event queued** for creation (async)
3. ✅ **Google Calendar event created** with formatted agenda in description
4. ✅ **Invites sent** to all attendees (if `send_invites: true`)

---

## 📋 API Endpoints

### Create Meeting with AI Agenda

**POST** `/meetings/with-agenda`

Creates a meeting record with AI-generated agenda and optionally syncs to Google Calendar.

**Request Body:**

```typescript
{
  // Required
  meeting_name: string;          // Meeting title (1-500 chars)
  meeting_description: string;   // Description (min 10 chars)
  
  // Calendar Event Details (optional)
  start_time?: datetime;         // When meeting starts (ISO 8601)
  duration_minutes?: number;     // Duration (defaults to AI suggestion)
  location?: string;             // Location or video link
  attendee_emails: string[];     // List of attendee emails
  
  // Options
  create_calendar_event: boolean;  // Create Google Calendar event (default: true)
  send_invites: boolean;          // Send calendar invites (default: false)
  
  // AI Context (optional)
  meeting_type?: string;          // e.g., "planning", "review", "decision"
  company_context?: string;       // Additional context for AI
}
```

**Response:**

```typescript
{
  meeting_id: string;           // UUID of created meeting
  meeting_name: string;         // Meeting title
  agenda: MeetingAgenda;        // Full AI-generated agenda
  agenda_markdown: string;      // Markdown-formatted agenda
  calendar_event_id?: string;   // Google Calendar event ID (if created)
  calendar_event_link?: string; // Link to calendar event
  status: string;               // "queued_calendar_event" or "created_no_calendar"
}
```

---

### Get Meeting Agenda

**GET** `/meetings/{meeting_id}/agenda`

Retrieves the AI-generated agenda for a meeting.

**Response:**

```json
{
  "meeting_id": "...",
  "meeting_name": "...",
  "agenda": { /* Full agenda object */ },
  "agenda_markdown": "..."
}
```

---

### Regenerate Meeting Agenda

**POST** `/meetings/{meeting_id}/regenerate-agenda`

Regenerates the AI agenda for an existing meeting.

**Use cases:**
- Meeting details changed
- Want a different perspective
- Initial agenda wasn't detailed enough

**Response:**

```json
{
  "meeting_id": "...",
  "meeting_name": "...",
  "agenda": { /* New agenda */ },
  "agenda_markdown": "...",
  "status": "regenerated"
}
```

---

## 🧠 AI Agenda Structure

The AI generates a comprehensive agenda with the following components:

### 1. Meeting Objective
A clear, concise statement of what the meeting aims to achieve.

### 2. Agenda Topics
Specific discussion items with:
- **Topic**: What will be discussed
- **Duration**: Estimated time in minutes
- **Owner**: Person leading the topic (if known)

### 3. Expected Decisions
Key decisions that need to be made:
- **Decision Point**: What needs to be decided
- **Context**: Why this decision is important
- **Options**: Possible choices or approaches

### 4. Proposed Next Steps
Actions to take after the meeting:
- **Action**: What needs to be done
- **Owner**: Suggested responsible person
- **Timeline**: When it should be completed

### 5. Preparation Notes
Things participants should prepare beforehand to make the meeting more effective.

---

## 📅 Google Calendar Integration

### Calendar Event Format

When a calendar event is created, the agenda is formatted beautifully:

```
🎯 Meeting Objective
Finalize Q1 2025 roadmap, allocate resources for product launch...

📋 Agenda (90 minutes)
1. Review current product development status (alice@company.com) — 15 min
2. Discuss resource allocation for new product launch — 30 min
3. Define Q1 success metrics and KPIs (bob@company.com) — 25 min
4. Finalize timeline and milestones — 20 min

✅ Key Decisions to Make
• Resource allocation for product launch
  Options: Dedicate 50% of engineering team, Hire additional contractors, Shift resources from maintenance work
• Q1 success metrics
  Options: User acquisition targets, Revenue milestones, Product feature completion

🚀 Proposed Next Steps
• Prepare detailed resource allocation proposal (@alice@company.com) — by end of week
• Draft Q1 OKRs document (@bob@company.com) — within 3 days
• Schedule follow-up check-in meeting — within 2 weeks

📚 Preparation
• Review current sprint progress and backlog
• Prepare budget estimates for Q1
• Come with 3 potential success metrics per department
```

### Event Details

- **Summary**: Meeting name
- **Start/End Time**: Based on provided time + AI-suggested duration
- **Location**: Your specified location or video link
- **Attendees**: All provided email addresses
- **Description**: Beautifully formatted agenda (above)

---

## 🔧 Configuration

### Environment Variables

No new environment variables required! The system uses your existing:

```env
# OpenAI (for AI agenda generation)
OPENAI_API_KEY=sk-proj-...

# Google Calendar (for event creation)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

### Feature Flags

Control calendar event behavior:

```env
# Create actual calendar events (vs just proposals)
ENABLE_CALENDAR_BOOKING=true
```

**Recommendation**: Start with `false` to review events before they're created, then enable when confident.

---

## 💡 Usage Examples

### Example 1: Product Launch Planning

```json
{
  "meeting_name": "Product Launch Strategy",
  "meeting_description": "Plan the go-to-market strategy for our new mobile app. Need to coordinate marketing campaign, app store optimization, press outreach, and launch event. Budget is $50K.",
  "start_time": "2025-01-20T14:00:00Z",
  "attendee_emails": ["marketing@company.com", "product@company.com", "ceo@company.com"],
  "create_calendar_event": true,
  "meeting_type": "planning"
}
```

**AI will generate:**
- Discussion topics: Marketing channels, budget allocation, timeline, success metrics
- Decisions: Launch date, marketing budget split, PR strategy
- Next steps: Create marketing materials, book venues, finalize app store listing

---

### Example 2: Performance Review

```json
{
  "meeting_name": "Q4 Performance Review - Engineering Team",
  "meeting_description": "Review engineering team's Q4 performance, discuss individual achievements, address challenges, and plan Q1 growth opportunities. Focus on both technical accomplishments and team collaboration.",
  "start_time": "2025-01-10T15:00:00Z",
  "duration_minutes": 60,
  "attendee_emails": ["engineering-manager@company.com", "hr@company.com"],
  "meeting_type": "review",
  "send_invites": false
}
```

**AI will generate:**
- Discussion topics: Q4 achievements, challenges faced, growth areas, Q1 goals
- Decisions: Promotion recommendations, training needs, team restructuring
- Next steps: Document feedback, schedule 1-on-1s, create development plans

---

### Example 3: Client Kickoff Meeting

```json
{
  "meeting_name": "New Client Onboarding - Acme Corp",
  "meeting_description": "Initial kickoff meeting with Acme Corp. Introduce team members, understand their requirements for the CRM integration project, set expectations, and establish communication cadence. Their main pain point is data migration from legacy system.",
  "start_time": "2025-01-18T11:00:00Z",
  "location": "Zoom: https://zoom.us/j/123456789",
  "attendee_emails": [
    "contact@acmecorp.com",
    "pm@company.com",
    "tech-lead@company.com"
  ],
  "company_context": "B2B SaaS company, client is enterprise retail",
  "create_calendar_event": true,
  "send_invites": true
}
```

**AI will generate:**
- Discussion topics: Introductions, requirements gathering, technical architecture, timeline
- Decisions: Project scope, timeline, communication channels
- Next steps: Technical discovery, proposal draft, contract review
- Preparation: Review Acme's current tech stack, prepare questions about data migration

---

## 🔒 Security & Privacy (GDPR Compliant)

### What the AI Does NOT Do

✅ **Following GDPR principles:**
- ❌ Does NOT fabricate names, emails, or personal data
- ❌ Does NOT assign owners unless participants are explicitly provided
- ❌ Does NOT invent due dates or commitments
- ❌ Does NOT make assumptions about people's roles

### What Data is Stored

The system stores:
- Meeting name and description (provided by you)
- AI-generated agenda (stored in `meeting_metadata` JSONB field)
- Participant emails (only what you provide)
- Calendar event references (external IDs only)

All data is:
- ✅ Encrypted in transit (HTTPS)
- ✅ Isolated per organization (RLS policies)
- ✅ Audit-logged (via `updated_at` timestamps)

---

## 🧪 Testing the System

### Test Script

```bash
#!/bin/bash
# Test AI Meeting Agenda Generator

# 1. Set environment variables
export TOKEN="your-supabase-jwt-token"
export ORG_ID="your-org-uuid"
export API_URL="http://localhost:8000"

# 2. Create meeting with AI agenda
echo "Creating meeting with AI agenda..."
RESPONSE=$(curl -s -X POST "$API_URL/meetings/with-agenda" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_name": "Test Planning Meeting",
    "meeting_description": "This is a test meeting to validate the AI agenda generation system. We need to discuss project timeline, resource allocation, and success metrics.",
    "start_time": "2025-01-15T10:00:00Z",
    "duration_minutes": 60,
    "attendee_emails": ["test@example.com"],
    "create_calendar_event": true,
    "send_invites": false
  }')

# 3. Extract meeting ID
MEETING_ID=$(echo $RESPONSE | jq -r '.meeting_id')
echo "✓ Meeting created: $MEETING_ID"

# 4. View the generated agenda
echo "Generated Agenda:"
echo $RESPONSE | jq '.agenda'

# 5. Wait for calendar event creation (async)
echo "Waiting for calendar event creation..."
sleep 5

# 6. Check calendar (if you have Google OAuth connected)
echo "✓ Check your Google Calendar for the event!"
echo "✓ Meeting ID: $MEETING_ID"
```

### Manual Testing Steps

1. **Create Meeting:**
   ```bash
   POST /meetings/with-agenda
   ```

2. **Verify Meeting Record:**
   ```bash
   GET /meetings/{meeting_id}
   ```

3. **Check Generated Agenda:**
   ```bash
   GET /meetings/{meeting_id}/agenda
   ```

4. **Verify Google Calendar:**
   - Open Google Calendar
   - Look for event with meeting name
   - Verify agenda is in description

5. **Test Regeneration:**
   ```bash
   POST /meetings/{meeting_id}/regenerate-agenda
   ```

---

## 🐛 Troubleshooting

### Issue: "No AI agenda found"

**Cause**: Meeting was created without AI agenda generation.

**Solution**: Use the `/meetings/with-agenda` endpoint, not the regular `/meetings` endpoint.

---

### Issue: "Google not configured"

**Cause**: Google OAuth credentials not set up.

**Solution**:
1. Follow [GOOGLE_INTEGRATION.md](GOOGLE_INTEGRATION.md) to set up OAuth
2. Connect your Google account
3. Try again

---

### Issue: Calendar event not created

**Possible causes:**
- Calendar event creation is async (wait 5-10 seconds)
- Google OAuth tokens expired (re-authenticate)
- `ENABLE_CALENDAR_BOOKING=false` (events created as proposals only)

**Check status:**
```bash
# View calendar proposals
GET /calendar/proposals

# Check Celery worker logs
celery -A app.worker.celery_app inspect active
```

---

### Issue: Agenda is too generic

**Solution**: Provide more context:
- Use `meeting_description` with specific details
- Add `company_context` field
- Include participant emails so AI can assign owners
- Specify `meeting_type` for better tailoring

---

## 📊 Workflow Diagram

```
User Input
  ↓
┌─────────────────────────────────────┐
│ POST /meetings/with-agenda          │
│ - meeting_name                      │
│ - meeting_description               │
│ - start_time, attendees             │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ AI Agenda Generation (OpenAI)       │
│ - Analyze name + description        │
│ - Generate structured agenda        │
│   • Topics with durations           │
│   • Expected decisions              │
│   • Proposed next steps             │
│   • Preparation notes               │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ Create Meeting Record (DB)          │
│ - Store in meetings table           │
│ - Save agenda in metadata JSONB     │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ Queue Calendar Event (Celery)       │
│ - Async task creation               │
│ - Format agenda for calendar        │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ Create Google Calendar Event        │
│ - Call Google Calendar API          │
│ - Include formatted agenda          │
│ - Send invites (if enabled)         │
│ - Store external_ref                │
└─────────────────────────────────────┘
  ↓
Done! ✓
```

---

## 🎯 Best Practices

### 1. Provide Detailed Descriptions

**Good:**
```
"Plan Q1 product roadmap. Need to decide on feature priorities, allocate engineering resources between maintenance (20%) and new features (80%), establish launch timeline for mobile app v2.0, and define success metrics."
```

**Bad:**
```
"Planning meeting"
```

### 2. Include Relevant Context

Use optional fields for better AI generation:
- `meeting_type`: Helps AI understand the nature (planning, review, decision, brainstorm)
- `company_context`: Provides industry/domain context
- `attendee_emails`: Enables AI to assign topic owners

### 3. Review Before Enabling Auto-Send

Start with:
```json
{
  "create_calendar_event": true,
  "send_invites": false  // Review first!
}
```

Then enable `send_invites: true` once you're confident.

### 4. Use Regeneration for Refinement

If the initial agenda isn't perfect:
```bash
POST /meetings/{meeting_id}/regenerate-agenda
```

AI will create a fresh perspective each time.

---

## 🚀 Future Enhancements

Planned features:
- [ ] Agenda templates by meeting type
- [ ] Integration with meeting notes during the actual meeting
- [ ] Post-meeting agenda vs. actual discussion comparison
- [ ] Smart scheduling suggestions based on team availability
- [ ] Auto-populate from previous similar meetings

---

## 📞 Support

**Issues?** Check:
1. [Troubleshooting](#-troubleshooting) section above
2. [GOOGLE_INTEGRATION.md](GOOGLE_INTEGRATION.md) for OAuth setup
3. API logs: `uvicorn` output
4. Worker logs: `celery worker` output

**Feature requests?** This system is designed to be extended!

---

## ✅ Summary

You now have a complete AI-powered meeting agenda generation system that:

✅ Takes meeting name + description as input  
✅ Generates comprehensive, actionable agendas using AI  
✅ Creates Google Calendar events with the agenda  
✅ Sends invites to attendees  
✅ Follows GDPR principles (no fabricated data)  
✅ Supports regeneration and refinement  
✅ Integrates seamlessly with your existing meeting platform  

**Start creating intelligent meetings today!** 🎉


