# Authentication Setup Guide

This guide explains how to set up secure authentication for your Meeting Intelligence Platform.

## Overview

The app now supports:
- ✅ **Email/Password Login** - Traditional authentication
- ✅ **Google OAuth** - Sign in with Google
- ✅ **Row Level Security (RLS)** - Data isolation per organization
- ✅ **JWT Tokens** - Secure API access

## 1. Supabase Auth Configuration

### Enable Authentication Providers

1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Navigate to **Authentication** → **Providers**
3. Enable the following providers:

#### Email Provider
- Already enabled by default
- Configure email templates if needed

#### Google Provider
1. Click on **Google** provider
2. You'll need:
   - **Client ID**
   - **Client Secret**
3. Follow the steps below to get these credentials

## 2. Google OAuth Setup

### Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google+ API**:
   - Go to **APIs & Services** → **Library**
   - Search for "Google+ API"
   - Click **Enable**

4. Create OAuth Credentials:
   - Go to **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **OAuth 2.0 Client ID**
   - Application type: **Web application**
   - Name: "Meeting Intelligence Platform"
   
5. Add Authorized redirect URIs:
   ```
   https://YOUR_SUPABASE_PROJECT.supabase.co/auth/v1/callback
   http://localhost:8000/auth/callback  (for local development)
   ```

6. Copy the **Client ID** and **Client Secret**

### Configure Supabase with Google Credentials

1. Go back to Supabase Dashboard → **Authentication** → **Providers** → **Google**
2. Enable Google provider
3. Paste your **Client ID** and **Client Secret**
4. Save changes

## 3. Row Level Security (RLS) Policies

RLS ensures users can only access data within their organization.

### Enable RLS on Tables

Run this SQL in Supabase SQL Editor:

```sql
-- Enable RLS on all tables
ALTER TABLE orgs ENABLE ROW LEVEL SECURITY;
ALTER TABLE org_memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE meetings ENABLE ROW LEVEL SECURITY;
ALTER TABLE artifacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE transcript_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE action_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE people ENABLE ROW LEVEL SECURITY;
ALTER TABLE meeting_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE meeting_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE meeting_entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE links ENABLE ROW LEVEL SECURITY;
ALTER TABLE processing_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE external_refs ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;

-- Create RLS Policies for Organizations
CREATE POLICY "Users can view orgs they are members of"
  ON orgs FOR SELECT
  USING (
    id IN (
      SELECT org_id FROM org_memberships
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update orgs where they are owners or admins"
  ON orgs FOR UPDATE
  USING (
    id IN (
      SELECT org_id FROM org_memberships
      WHERE user_id = auth.uid()
      AND role IN ('owner', 'admin')
    )
  );

-- Org Memberships Policies
CREATE POLICY "Users can view memberships of their orgs"
  ON org_memberships FOR SELECT
  USING (
    org_id IN (
      SELECT org_id FROM org_memberships
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert themselves into orgs they own"
  ON org_memberships FOR INSERT
  WITH CHECK (
    org_id IN (
      SELECT org_id FROM org_memberships
      WHERE user_id = auth.uid()
      AND role = 'owner'
    )
    OR user_id = auth.uid()  -- Allow first user to create membership
  );

-- Meetings Policies
CREATE POLICY "Users can view meetings in their orgs"
  ON meetings FOR SELECT
  USING (
    org_id IN (
      SELECT org_id FROM org_memberships
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can create meetings in their orgs"
  ON meetings FOR INSERT
  WITH CHECK (
    org_id IN (
      SELECT org_id FROM org_memberships
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update meetings in their orgs"
  ON meetings FOR UPDATE
  USING (
    org_id IN (
      SELECT org_id FROM org_memberships
      WHERE user_id = auth.uid()
    )
  );

-- Artifacts Policies
CREATE POLICY "Users can view artifacts in their orgs"
  ON artifacts FOR SELECT
  USING (
    org_id IN (
      SELECT org_id FROM org_memberships
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can create artifacts in their orgs"
  ON artifacts FOR INSERT
  WITH CHECK (
    org_id IN (
      SELECT org_id FROM org_memberships
      WHERE user_id = auth.uid()
    )
  );

-- Action Items Policies
CREATE POLICY "Users can view action items in their orgs"
  ON action_items FOR SELECT
  USING (
    org_id IN (
      SELECT org_id FROM org_memberships
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can create action items in their orgs"
  ON action_items FOR INSERT
  WITH CHECK (
    org_id IN (
      SELECT org_id FROM org_memberships
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update action items in their orgs"
  ON action_items FOR UPDATE
  USING (
    org_id IN (
      SELECT org_id FROM org_memberships
      WHERE user_id = auth.uid()
    )
  );

-- Similar policies for other tables...
-- (Repeat the pattern for decisions, summaries, people, etc.)
```

## 4. Environment Configuration

Update your `.env` file:

```env
# Supabase Auth
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Google OAuth (optional - for Google Sign-In)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

## 5. API Endpoints

### Authentication Endpoints

All available at `/auth/`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/signup` | POST | Register new user |
| `/auth/login` | POST | Login with email/password |
| `/auth/logout` | POST | Logout current user |
| `/auth/google` | GET | Initiate Google OAuth |
| `/auth/callback` | GET | OAuth callback handler |
| `/auth/me` | GET | Get current user info |
| `/auth/refresh` | POST | Refresh access token |

### Protected Routes

All API endpoints now require authentication via Bearer token:

```bash
curl -X GET http://localhost:8000/meetings \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 6. Using the Protected Upload UI

### Access the Protected Interface

Navigate to: **http://localhost:8000/upload**

### Features:
- ✅ Login with email/password
- ✅ Sign up for new account
- ✅ Google OAuth sign-in
- ✅ Secure file upload with authentication
- ✅ Automatic token management
- ✅ Session persistence

### First Time Setup:

1. Open http://localhost:8000/upload
2. Click "Sign Up"
3. Enter your email and password
4. Check your email for verification link (if email is configured)
5. Log in with your credentials
6. Start uploading files!

## 7. Testing Authentication

### Test Signup
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'
```

### Test Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

Response includes:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {
    "id": "uuid",
    "email": "test@example.com"
  },
  "message": "Logged in successfully"
}
```

### Test Protected Endpoint
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 8. Security Best Practices

✅ **Password Requirements**:
- Minimum 8 characters
- Mix of letters, numbers, and symbols recommended

✅ **Token Storage**:
- Access tokens stored in localStorage
- Refresh tokens for long-term sessions
- Tokens expire after configured time

✅ **RLS Ensures**:
- Users only see their organization's data
- No data leakage between organizations
- Database-level security enforcement

✅ **HTTPS in Production**:
- Always use HTTPS in production
- Secure cookie settings
- CORS properly configured

## 9. Troubleshooting

### "Invalid credentials" error
- Check email/password are correct
- Verify user exists in Supabase Auth dashboard
- Check if email is verified (if required)

### Google OAuth not working
- Verify Google credentials in Supabase
- Check redirect URIs are correct
- Ensure Google+ API is enabled

### RLS blocking queries
- Check user is member of organization
- Verify org_id is being passed correctly
- Review RLS policies in Supabase SQL editor

### Token expired
- Use refresh token endpoint to get new access token
- Check token expiration settings in Supabase

## 10. Next Steps

Once authentication is working:

1. **Create Organizations**: Users can create/join organizations
2. **Invite Team Members**: Share access within organizations
3. **Configure Integrations**: Set up Linear, Google Calendar, etc.
4. **Upload Meetings**: Start processing meeting files
5. **Extract Insights**: View action items, decisions, summaries

## Support

For issues:
1. Check Supabase Auth logs
2. Review browser console for errors
3. Verify environment variables
4. Test with curl commands above




