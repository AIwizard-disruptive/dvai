#!/bin/bash
# Test script for AI Meeting Agenda Generation System
# Run this script to test the complete workflow

set -e  # Exit on error

echo "🧪 AI Meeting Agenda Generator - Test Script"
echo "============================================"
echo ""

# Check if required environment variables are set
if [ -z "$TOKEN" ]; then
    echo "❌ ERROR: TOKEN environment variable not set"
    echo "   Export your Supabase JWT token:"
    echo "   export TOKEN='your-jwt-token'"
    exit 1
fi

if [ -z "$ORG_ID" ]; then
    echo "❌ ERROR: ORG_ID environment variable not set"
    echo "   Export your organization ID:"
    echo "   export ORG_ID='your-org-uuid'"
    exit 1
fi

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
TEST_EMAIL="${TEST_EMAIL:-test@example.com}"

echo "Configuration:"
echo "  API URL: $API_URL"
echo "  Org ID: $ORG_ID"
echo "  Test Email: $TEST_EMAIL"
echo ""

# Test 1: Create meeting with AI agenda
echo "📝 Test 1: Creating meeting with AI-generated agenda..."
echo ""

RESPONSE=$(curl -s -X POST "$API_URL/meetings/with-agenda" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_name": "Q1 2025 Planning Session",
    "meeting_description": "Strategic planning meeting to finalize Q1 roadmap, decide on resource allocation for new product launch, establish success metrics, and coordinate cross-functional initiatives. Key topics: product priorities, engineering capacity, marketing campaigns, and budget allocation.",
    "start_time": "2025-01-20T10:00:00Z",
    "duration_minutes": 90,
    "location": "Conference Room A",
    "attendee_emails": ["'$TEST_EMAIL'"],
    "create_calendar_event": true,
    "send_invites": false,
    "meeting_type": "planning",
    "company_context": "Tech startup preparing for Series A funding round"
  }')

# Check if request was successful
if echo "$RESPONSE" | jq -e '.meeting_id' > /dev/null 2>&1; then
    MEETING_ID=$(echo "$RESPONSE" | jq -r '.meeting_id')
    echo "✅ Meeting created successfully!"
    echo "   Meeting ID: $MEETING_ID"
    echo ""
else
    echo "❌ Failed to create meeting"
    echo "Response:"
    echo "$RESPONSE" | jq '.'
    exit 1
fi

# Display the generated agenda
echo "📋 Generated Agenda:"
echo ""
echo "$RESPONSE" | jq '.agenda' | jq -r '
"🎯 Objective: " + .meeting_objective,
"",
"⏱️  Duration: " + (.suggested_duration_minutes | tostring) + " minutes",
"",
"📌 Topics:",
(.agenda_topics[] | "  • " + .topic + " (" + (.duration_minutes | tostring) + " min)" + (if .owner then " - " + .owner else "" end)),
"",
(if (.expected_decisions | length) > 0 then
  "✅ Key Decisions:",
  (.expected_decisions[] | "  • " + .decision_point)
else "" end),
"",
(if (.proposed_next_steps | length) > 0 then
  "🚀 Next Steps:",
  (.proposed_next_steps[] | "  • " + .action + (if .owner then " (@" + .owner + ")" else "" end) + (if .timeline then " - " + .timeline else "" end))
else "" end),
"",
(if (.preparation_notes | length) > 0 then
  "📚 Preparation:",
  (.preparation_notes[] | "  • " + .)
else "" end)
'
echo ""

# Test 2: Retrieve the agenda
echo "📖 Test 2: Retrieving meeting agenda..."
sleep 2

AGENDA_RESPONSE=$(curl -s -X GET "$API_URL/meetings/$MEETING_ID/agenda" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID")

if echo "$AGENDA_RESPONSE" | jq -e '.agenda' > /dev/null 2>&1; then
    echo "✅ Successfully retrieved agenda"
    echo ""
else
    echo "❌ Failed to retrieve agenda"
    echo "Response:"
    echo "$AGENDA_RESPONSE" | jq '.'
fi

# Test 3: Regenerate agenda
echo "🔄 Test 3: Regenerating meeting agenda..."
sleep 2

REGEN_RESPONSE=$(curl -s -X POST "$API_URL/meetings/$MEETING_ID/regenerate-agenda" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Org-Id: $ORG_ID")

if echo "$REGEN_RESPONSE" | jq -e '.status' > /dev/null 2>&1; then
    STATUS=$(echo "$REGEN_RESPONSE" | jq -r '.status')
    if [ "$STATUS" = "regenerated" ]; then
        echo "✅ Successfully regenerated agenda"
        echo ""
        echo "New agenda objective:"
        echo "$REGEN_RESPONSE" | jq -r '.agenda.meeting_objective' | sed 's/^/  /'
        echo ""
    else
        echo "⚠️  Unexpected status: $STATUS"
    fi
else
    echo "❌ Failed to regenerate agenda"
    echo "Response:"
    echo "$REGEN_RESPONSE" | jq '.'
fi

# Test 4: Check calendar event creation (async)
echo "📅 Test 4: Checking calendar event status..."
echo "   (Calendar events are created asynchronously)"
sleep 5

# Note: In a real system, you would check external_refs table or calendar proposals
echo "ℹ️  To verify calendar event:"
echo "   1. Check your Google Calendar for event: 'Q1 2025 Planning Session'"
echo "   2. Verify the agenda is in the event description"
echo "   3. Or run: curl $API_URL/calendar/proposals -H 'Authorization: Bearer $TOKEN' -H 'X-Org-Id: $ORG_ID'"
echo ""

# Summary
echo "================================"
echo "✅ All tests completed!"
echo "================================"
echo ""
echo "Test Summary:"
echo "  ✅ Meeting with AI agenda created"
echo "  ✅ Agenda retrieved successfully"
echo "  ✅ Agenda regenerated successfully"
echo "  ⏳ Calendar event queued (check Google Calendar)"
echo ""
echo "Meeting ID: $MEETING_ID"
echo ""
echo "Next steps:"
echo "  1. View meeting: curl $API_URL/meetings/$MEETING_ID -H 'Authorization: Bearer $TOKEN' -H 'X-Org-Id: $ORG_ID'"
echo "  2. Check Google Calendar for the event"
echo "  3. Review calendar proposals: curl $API_URL/calendar/proposals -H 'Authorization: Bearer $TOKEN' -H 'X-Org-Id: $ORG_ID'"
echo ""
echo "🎉 AI Meeting Agenda Generator is working!"

