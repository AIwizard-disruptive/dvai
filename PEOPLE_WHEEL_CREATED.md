# People & Network Wheel Page Created ✅

## New Page: `/wheels/people`

I've created the People & Network wheel page with **organized Google Drive documents**!

---

## Features

### Document Categories (Collapsible)
- **HR & Culture** - HR policies and culture docs
- **Recognition Program** - Employee recognition
- **Culture Program** - Culture building docs
- **Onboarding** - Onboarding materials
- **Policy Documents** - Company policies

### Each Category Shows:
- **Folder icon** (monochrome, collapsible)
- **Document count** (grey badge)
- **Click to expand/collapse**
- **Document cards** in grid layout

### Document Cards:
- **Document icon** (monochrome)
- **Title** (bold, black)
- **Description** (first 80 chars, grey)
- **Type badge** (grey badge)
- **Click** → Opens Google Drive doc in new tab

---

## Layout

```
People & Network
HR, Culture & Team Documentation

┌─────────────────────────────────────────┐
│ ▼ HR & Culture              [5 documents]│
├─────────────────────────────────────────┤
│ ┌───────┐ ┌───────┐ ┌───────┐          │
│ │ [📄]  │ │ [📄]  │ │ [📄]  │          │
│ │ Doc 1 │ │ Doc 2 │ │ Doc 3 │          │
│ │ Desc  │ │ Desc  │ │ Desc  │          │
│ └───────┘ └───────┘ └───────┘          │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ ▶ Culture Program           [3 documents]│
├─────────────────────────────────────────┤
│ (Collapsed - click to expand)           │
└─────────────────────────────────────────┘
```

---

## How It Works

### Data Source
- Pulls from `policy_documents` table in Supabase
- Uses `policy_type` field to categorize
- Uses `google_drive_url` for links

### Categorization
```python
'culture' → Culture Program
'hr' → HR & Culture
'onboarding' → Onboarding
'policy' → Policy Documents
other → HR & Culture (default)
```

### Collapsible Categories
- **Click category header** → Expand/collapse
- **Arrow icon** rotates (up = expanded, down = collapsed)
- **Smooth animation**
- **Default**: All expanded

---

## Visual Design (Monochrome)

### Category Header
- Grey folder icon
- Black title text
- Grey count badge
- Arrow for expand/collapse
- Hover effect

### Document Cards
- White background
- Grey border (1px)
- Document icon (grey)
- Title (bold, black)
- Description (grey, truncated)
- Type badge (grey)
- Hover: Subtle shadow

### All Monochrome
- Icons: Dark grey (#666666)
- No colored folders
- No colored badges
- Professional, clean

---

## Navigation

### Sidebar
**People & Network** (main link)
- → **Activity Dashboard** (nested)

**Clicking "People & Network"** → Goes to `/wheels/people`

**Clicking "Activity Dashboard"** → Goes to `/dashboard-ui`

---

## Test It

**Visit**: http://localhost:8000/wheels/people

**Hard refresh**: `Cmd + Shift + R`

**You'll see**:
1. ✅ Left sidebar (collapsible)
2. ✅ Page title: "People & Network"
3. ✅ Collapsible categories (HR & Culture, etc.)
4. ✅ Document cards with Google Drive links
5. ✅ Click document → Opens in Google Drive
6. ✅ All monochrome design
7. ✅ Dark mode toggle works

---

## Document Card Details

### What Each Card Shows:
```
┌─────────────────────┐
│ [Document Icon]     │  ← Grey icon
│                     │
│ Document Title      │  ← Bold, black
│ Short description   │  ← Grey, truncated
│ text here...        │
│                     │
│ [culture]           │  ← Type badge (grey)
└─────────────────────┘
```

### Clicking a Card:
- Opens Google Drive URL in new tab
- Direct link to document
- Secure (uses your Google permissions)

---

## Adding Documents

### To Add New Documents:
1. Go to Knowledge Bank (`/knowledge/`)
2. Click "Policies" tab
3. Add policy with:
   - Title
   - Google Drive URL
   - Policy type (culture, hr, onboarding, policy)
   - Description

### They Auto-Appear Here:
- Automatically categorized
- Shows in appropriate folder
- Clickable card created
- Updates in real-time

---

## Categories Explained

### HR & Culture
General HR policies, culture documents, company values

### Recognition Program
Employee recognition, awards, appreciation docs

### Culture Program
Culture building materials, team activities, values

### Onboarding
New hire materials, onboarding checklists, training

### Policy Documents
Official company policies, procedures, guidelines

---

## Mobile Responsive

### Desktop
- Categories: Full width
- Documents: 3 columns
- All categories visible

### Tablet
- Categories: Full width
- Documents: 2 columns
- Scroll to see all

### Mobile
- Categories: Full width
- Documents: 1 column
- Touch-friendly expand/collapse

---

## Status: ✅ Created

**Page**: People & Network wheel  
**URL**: /wheels/people  
**Features**: Collapsible categories, Google Drive links  
**Design**: Monochrome, Claude-style  
**Data**: From Supabase policy_documents  

---

**Visit it**: http://localhost:8000/wheels/people

**The page is ready with all your Google Drive documents!** 🎉

---

**Last Updated**: December 16, 2025  
**Wheel**: People & Network  
**Purpose**: HR, Culture & Team Documentation



