# 🔐 Google OAuth Setup Guide

## ✅ What's Already Done

I've already implemented:
- ✅ **Auto-org creation** - When you sign in, your organization is created automatically
- ✅ **Auto-user setup** - You're added as owner automatically
- ✅ **Login UI** - Beautiful login page at `/login`
- ✅ **OAuth flow** - Complete Google OAuth integration
- ✅ **Token handling** - Automatic token storage

---

## 🚀 Quick Start (3 Steps)

### Step 1: Enable Google OAuth in Supabase

1. Go to: https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/auth/providers

2. Find **Google** in the providers list

3. Toggle **Enable Sign in with Google** to ON

4. You'll see two options:
   - **Use Supabase's OAuth credentials** (Quick & Easy) ← **Use this for testing**
   - **Use your own OAuth credentials** (Production)

5. For testing, choose **"Use Supabase's credentials"** and click Save

That's it! Google OAuth is now enabled.

---

### Step 2: Test the Login Flow

1. **Open the login page:**
   ```
   http://localhost:8000/login
   ```

2. **Click "Sign in with Google"**

3. **Choose your Google account**

4. **Grant permissions**

5. **You'll be redirected back** with:
   - ✅ Organization created (named "[Your Name]'s Organization")
   - ✅ You're set as owner
   - ✅ Access token stored
   - ✅ Ready to upload files!

---

### Step 3: Upload Files with Full Processing

After logging in, you can use:

**Option A: Protected Upload UI**
```
http://localhost:8000/upload-protected
```
- ✅ Saves to database
- ✅ AI processing enabled
- ✅ Action items extracted
- ✅ Decisions extracted

**Option B: Use the test file I created**
```bash
curl -X POST http://localhost:8000/artifacts/upload \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@/tmp/test_meeting_notes.docx"
```

---

## 🔧 For Production: Use Your Own OAuth Credentials

### Step 1: Create Google OAuth App

1. Go to: https://console.cloud.google.com/apis/credentials

2. Create a new project or select existing

3. Click **"Create Credentials"** → **"OAuth client ID"**

4. Configure:
   - **Application type:** Web application
   - **Name:** Meeting Intelligence Platform
   - **Authorized redirect URIs:** Add these:
     ```
     https://gqpupmuzriqarmrsuwev.supabase.co/auth/v1/callback
     http://localhost:8000/auth/callback
     ```

5. Click **Create**

6. Copy your **Client ID** and **Client Secret**

### Step 2: Update Supabase

1. Go to: https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/auth/providers

2. Find **Google** provider

3. Choose **"Use your own OAuth credentials"**

4. Paste:
   - **Client ID** (from Google Console)
   - **Client Secret** (from Google Console)

5. Click **Save**

### Step 3: Update Your .env (Optional)

```bash
# In backend/.env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

---

## 🎯 What Happens When You Login

### Automatic Flow:

```
1. Click "Sign in with Google"
   ↓
2. Redirected to Google login
   ↓
3. Grant permissions
   ↓
4. Supabase creates/authenticates user
   ↓
5. **Backend checks if user has org**
   ↓
6. **If no org:**
   - Creates org named "[Your Name]'s Organization"
   - Adds you as owner
   ↓
7. Returns access token & refresh token
   ↓
8. Redirected to success page
   ↓
9. Tokens stored in localStorage
   ↓
10. Auto-redirect to upload page
```

---

## 📋 Test the Full Flow

### Step 1: Login

```
http://localhost:8000/login
```

Click "Sign in with Google"

### Step 2: Verify Your Org Was Created

In Supabase SQL Editor:
```sql
-- Check your user
SELECT * FROM auth.users ORDER BY created_at DESC LIMIT 1;

-- Check your org
SELECT * FROM orgs ORDER BY created_at DESC LIMIT 1;

-- Check your membership
SELECT * FROM org_memberships ORDER BY created_at DESC LIMIT 1;
```

You should see:
- ✅ Your user in `auth.users`
- ✅ Your org in `orgs` (named after you)
- ✅ Your membership in `org_memberships` (role = 'owner')

### Step 3: Upload a File

```
http://localhost:8000/upload-protected
```

Upload the test file from `/tmp/test_meeting_notes.docx`

### Step 4: Verify Processing

```sql
-- Check uploaded artifact
SELECT * FROM artifacts ORDER BY created_at DESC LIMIT 1;

-- Check extracted action items
SELECT * FROM action_items ORDER BY created_at DESC;

-- Check extracted decisions
SELECT * FROM decisions ORDER BY created_at DESC;
```

---

## 🧪 Available Endpoints

| Endpoint | What It Does | Auth Required |
|----------|--------------|---------------|
| `/login` | Login page with Google OAuth | No |
| `/auth/google` | Start Google OAuth flow | No |
| `/auth/callback` | OAuth callback (auto-creates org) | No |
| `/auth/success` | Success page with tokens | No |
| `/upload-protected` | Upload with full processing | Yes |
| `/upload-ui` | Dev mode upload (no processing) | No |
| `/meetings` | List your meetings | Yes |
| `/action-items` | List action items | Yes |
| `/decisions` | List decisions | Yes |

---

## 🔍 Troubleshooting

### "Failed to initiate Google OAuth"
- Check Supabase dashboard → Authentication → Providers
- Make sure Google provider is enabled
- For testing, use "Supabase's credentials"

### "OAuth callback failed"
- Check redirect URI is correct in Google Console
- Should be: `https://gqpupmuzriqarmrsuwev.supabase.co/auth/v1/callback`

### "Organization not created"
- Check backend logs in terminal 14
- Verify database connection is working
- Try: `curl http://localhost:8000/health`

### "File uploads but no processing"
- Check Celery worker is running (terminal 16)
- Check Redis is running: `/tmp/redis-stable/src/redis-cli ping`
- Check logs for errors

---

## ✅ Success Checklist

- [ ] Google OAuth enabled in Supabase
- [ ] Can access `/login` page
- [ ] Can click "Sign in with Google"
- [ ] Gets redirected to Google
- [ ] Returns to `/auth/success`
- [ ] Organization auto-created
- [ ] Can access `/upload-protected`
- [ ] Files upload to database
- [ ] AI processing extracts data

---

## 🎉 You're Ready!

Once Google OAuth is enabled in Supabase, you can:

1. **Login:** http://localhost:8000/login
2. **Upload:** http://localhost:8000/upload-protected
3. **View Results:** Check Supabase database tables

Your org is created automatically - no manual SQL needed! 🚀

---

## 📚 Next Steps

- Configure Linear integration (optional)
- Add team members to your org
- Set up production domain
- Configure email verification
- Add custom branding

---

**Questions?** Everything should work automatically once Google OAuth is enabled in Supabase!



