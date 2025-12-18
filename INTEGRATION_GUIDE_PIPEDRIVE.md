# How to Connect Pipedrive CRM - Step-by-Step Guide 🎯

**For:** Sales pipeline and deal tracking  
**Difficulty:** ⭐ Easy (5 minutes)  
**Required Access:** Pipedrive account admin

---

## What You'll Get

Once connected, you'll see:
- ✅ All deals and opportunities in the Dealflow board
- ✅ Real-time pipeline value
- ✅ Deal stages (Lead → Qualified → Meeting → Won)
- ✅ Customer and contact information
- ✅ Deal values and forecasts

**Example:** Coeo has 193 deals worth 2.77M SEK showing live!

---

## Step 1: Log Into Pipedrive

1. Go to your Pipedrive account:
   ```
   https://yourcompany.pipedrive.com
   ```
   
2. Use your email and password to log in

3. Make sure you're logged in as an **admin user** or someone with API access

---

## Step 2: Find Your API Settings

### 2A: Click Your Profile Picture
- Located in the **top right corner**
- It's a circular icon with your initials or photo

### 2B: Select "Personal preferences"
- A dropdown menu appears
- Click "Personal preferences" (near the bottom)

### 2C: Go to the API Tab
- You'll see several tabs at the top
- Click "**API**"
- This is where your API token lives!

---

## Step 3: Generate Your API Token

### If You Don't Have a Token Yet:

1. Click the button: **"Generate new token"**

2. Give it a name:
   ```
   DV Portfolio Platform
   ```

3. Click **"Generate"**

4. **IMPORTANT:** Copy the token immediately!
   - It looks like: `abc123def456ghi789...`
   - You won't be able to see it again
   - Save it somewhere temporarily (notepad, password manager)

### If You Already Have a Token:

1. You'll see existing tokens listed
2. Copy the token value (click the copy icon)
3. Or generate a new one if you prefer

---

## Step 4: Note Your Company Domain

Your Pipedrive domain is in your URL:

```
https://[YOUR-COMPANY].pipedrive.com
      ↑
      This part!
```

**Examples:**
- `coeo.pipedrive.com` → Domain is "coeo"
- `disruptiveventures.pipedrive.com` → Domain is "disruptiveventures"

Write down your full domain (including .pipedrive.com)

---

## Step 5: Add to DV Platform

### 5A: Go to Settings Page
Open in your browser:
```
http://localhost:8000/settings
```

### 5B: Navigate to Portfolio Companies Tab
- You'll see 3 tabs at the top: **General | API Keys | Portfolio Companies**
- Click **"Portfolio Companies (8)"**

### 5C: Find Your Company
- Scroll through the list
- Find the company you want to connect
- Example: "Coeo" or "Crystal Alarm"

### 5D: Click "Connect" on Pipedrive CRM
- Each company has 3-6 integration boxes
- Find the one labeled **"Pipedrive CRM"**
- Click the **"Connect"** button

### 5E: Fill in the Form
A popup window appears with 2 fields:

**Field 1: API Token**
- Paste the token you copied in Step 3
- It's a password field (shows dots)
- Example: `0082d57f308450640715cf7bf106a665287ddaaa`

**Field 2: Company Domain**
- Enter your company's Pipedrive domain
- Include `.pipedrive.com`
- Example: `coeo.pipedrive.com`

### 5F: Click "Save Integration"
- Blue button at the bottom right
- The system will:
  - Encrypt your token
  - Store it securely in the database
  - Test the connection

### 5G: See Success Message
You should see:
```
✅ Integration saved successfully!
```

The page will reload and show **"✅ Connected"** next to Pipedrive!

---

## Step 6: Verify It's Working

### 6A: Go to Building Companies Page
```
http://localhost:8000/wheels/building
```

### 6B: Select Your Company
- Use the dropdown at the top
- Select the company you just connected (e.g., "Coeo")

### 6C: Click "Dealflow" Tab
- You'll see 4 tabs: Activities | **Dealflow** | Financial | Team
- Click **Dealflow**

### 6D: See Your Real Deals!
You should now see:
- All your deals organized by stage
- Lead → Qualified → Meeting → Due Diligence → Proposal → Closed Won
- Deal titles, organizations, and values
- Real-time data from your Pipedrive!

---

## What Data Gets Pulled

### From Pipedrive API:
- ✅ **Deals**: Title, value, currency, stage
- ✅ **Organizations**: Company names
- ✅ **Contacts**: Person names
- ✅ **Owner**: Who's responsible for each deal
- ✅ **Dates**: Created, updated, expected close
- ✅ **Status**: Open, won, lost

### How It's Mapped:
Your Pipedrive stages → Standard DV stages

| Your Pipedrive Stage | Maps To |
|---------------------|---------|
| Lead, Kvalificerade, etc. | **Lead** |
| Prospekt, Kontakt skapad | **Qualified** |
| Demo bokad, Bokat möte | **Meeting** |
| Offert, Offert lämnad | **Due Diligence** |
| Förhandling, Nästan där | **Proposal** |
| OK verbal acceptans, Genomfört | **Closed Won** |

Negative stages (Nej tack, Inte nu, etc.) are automatically filtered out.

---

## Troubleshooting

### ❌ "Failed to save integration"

**Check:**
- Is the API token correct? (copy-paste without spaces)
- Is the domain correct? (include .pipedrive.com)
- Do you have admin access in Pipedrive?

**Fix:**
- Generate a new API token
- Try again with fresh token

### ❌ No deals showing

**Check:**
- Hard refresh the page (Cmd+Shift+R or Ctrl+Shift+R)
- Is the correct company selected in the dropdown?
- Are there actually deals in Pipedrive?

**Fix:**
- Open browser console (F12)
- Look for error messages
- Check server logs

### ❌ Wrong deals showing

**Check:**
- Are you viewing the right company?
- Multiple Pipedrive accounts configured?

**Fix:**
- Select correct company from dropdown
- Each company shows their own deals

---

## Security Notes

### ✅ Your Token is Safe:
- Encrypted with Fernet before storing
- Never appears in logs
- Never sent to frontend
- Stored in secure database
- Only decrypted when making API calls

### 🔒 Best Practices:
- Generate a dedicated token for this integration
- Don't share your token
- Rotate tokens every 6 months
- Revoke unused tokens

---

## Data Refresh

### How Often:
- **Every page load**: Pulls latest deals from Pipedrive
- **Typical delay**: 3-5 seconds
- **Cache**: In-memory during page render

### Manual Refresh:
- Reload the page to get latest data
- Or click "Sync Now" button (coming soon)

---

## Multiple Companies

You can connect **multiple companies**, each with their own Pipedrive:

1. Coeo → `coeo.pipedrive.com`
2. Crystal Alarm → Their Pipedrive account
3. Alent Dynamic → Their Pipedrive account
4. And so on...

Each company's deals will show when you select them!

---

## Rate Limits

Pipedrive allows:
- **100 requests per 2 seconds**
- Very generous!
- Unlikely to hit limits with normal usage

---

## Support

### Pipedrive Help:
- Documentation: https://developers.pipedrive.com
- Support: https://pipedrive.com/support

### DV Platform Help:
- Check `PIPEDRIVE_FORTNOX_SETUP.md`
- Check server logs: `tail -50 /tmp/uvicorn_pipedrive.log`

---

## Summary Checklist

- [ ] Log into Pipedrive
- [ ] Go to Personal preferences → API
- [ ] Generate API token
- [ ] Copy token
- [ ] Note company domain
- [ ] Go to http://localhost:8000/settings
- [ ] Click Portfolio Companies tab
- [ ] Find your company
- [ ] Click Connect on Pipedrive
- [ ] Paste token and domain
- [ ] Click Save Integration
- [ ] See "✅ Connected" status
- [ ] Go to Building page
- [ ] Select company
- [ ] Click Dealflow tab
- [ ] See your real deals! 🎉

---

**Time Required:** 5 minutes  
**Technical Knowledge:** None required  
**Result:** Live CRM data in your portfolio platform!

---

Need help? The token and domain are the ONLY two things you need! 🚀

