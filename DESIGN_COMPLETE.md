# Complete Design System - Ready ✅

## All Pages Updated with Left Sidebar + Monochrome Design

Every backend admin page now has:
- ✅ **Left sidebar navigation** (Claude-style, 280px)
- ✅ **Monochrome design** (NO colored icons, NO gradients)
- ✅ **User profile** in sidebar footer (with LinkedIn image support)
- ✅ **Admin warnings** where appropriate
- ✅ **Clean minimal layout**

---

## Updated Pages ✅

### 1. **Dashboard** - `/dashboard-ui`
- Left sidebar
- User profile with LinkedIn image
- Stats in monochrome (black numbers, grey text)
- Tab navigation (Meetings/Decisions/Actions)
- All cards monochrome

### 2. **Knowledge Bank** - `/knowledge/`
- Left sidebar
- User profile in sidebar
- **People in 3 columns** ✅
- **LinkedIn avatars with fallback** ✅
- **Deduplicated names** ✅
- Policies grid monochrome

### 3. **Upload Files** - `/upload-ui`
- Left sidebar
- User profile
- Drag & drop area (grey dashed border)
- File list clean
- Monochrome buttons

### 4. **Meeting View** - `/meeting/{id}`
- Left sidebar
- User profile
- Meeting details
- Decisions/Actions sections
- Attendees with avatars

### 5. **Integration Tests** - `/integration-test`  
- Left sidebar
- User profile
- Test cards in grid (3 columns)
- Supabase, Google, Linear tests
- Status badges (green/red only for status, otherwise monochrome)
- Run all tests button

---

## User Profile Feature

### Location
**Sidebar Footer** (bottom of left sidebar on every page)

### What It Shows
- User avatar (LinkedIn image or initials)
- User name
- User email
- Styled in monochrome (grey background)

### How It Works
```python
get_admin_sidebar(
    active_page='dashboard',
    user_name='Markus Löwegren',
    user_email='markus.lowegren@disruptiveventures.se',
    user_image_url='https://linkedin.com/photo.jpg'  # LinkedIn image
)
```

### Fallback
- If no image URL: Shows initials (e.g., "ML")
- If image fails to load: Shows initials
- Initials in grey on light grey background

---

## Design Rules (STRICTLY ENFORCED)

### Monochrome Color Palette
```css
/* Text Colors */
--gray-900: #1a1a1a    /* Headers, primary text */
--gray-700: #374151    /* Secondary text */
--gray-600: #666666    /* Tertiary text, icons */
--gray-500: #808080    /* Muted text */

/* Backgrounds */
#ffffff            /* White cards, main bg */
--gray-50: #fafafa     /* Subtle backgrounds */
--gray-100: #f5f5f5    /* Light grey backgrounds */

/* Borders */
--gray-200: #e5e5e5    /* Standard borders */
--gray-300: #d1d5db    /* Hover borders */

/* Icons - ALWAYS */
--icon-color: #666666  /* Dark grey - NEVER colored */
```

### Exceptions (ONLY for status indicators)
- ✅ Success: Green (`#f0fdf4` bg, `#166534` text) - for "Connected" badges
- ❌ Error: Red (`#fef2f2` bg, `#991b1b` text) - for "Error" badges
- ⚠️ Warning: Amber (`#fffbeb` bg, `#78350f` text) - for admin warnings only

### NEVER Use
- ❌ Blue icons
- ❌ Purple gradients
- ❌ Green progress bars  
- ❌ Colored card borders
- ❌ Colored avatars (except photos)
- ❌ Any bright colors

---

## Sidebar Navigation

### Available Links
1. **Dashboard** - `/dashboard-ui`
2. **Knowledge Bank** - `/knowledge/`
3. **Upload Files** - `/upload-ui`
4. **Integrations** - `/integration-test`
5. **Settings** - `/user-integrations/settings`

### Active State
- Current page highlighted with grey background
- Icon stays same color (no color change)

### Admin Warning
Amber banner in sidebar saying:
> "⚠️ Admin Only - Partners & administrators only. Team uses Google & Linear."

---

## Page Structure

Every page follows this pattern:

```html
<body>
    <!-- Left Sidebar (280px, fixed) -->
    {get_admin_sidebar(page, user_name, user_email, user_image)}
    
    <!-- Main Content (left margin: 280px) -->
    <div class="main-content">
        <!-- Page Header -->
        <div class="page-header">
            <div class="page-header-left">
                <h1 class="page-title">Page Title</h1>
                <p class="page-description">Description</p>
            </div>
        </div>
        
        <!-- Content Container -->
        <div class="container">
            <!-- Page content here -->
        </div>
    </div>
</body>
```

---

## Testing Checklist

Visit each page and verify:

### ✅ Dashboard (`/dashboard-ui`)
- [ ] Left sidebar visible
- [ ] User profile in sidebar footer
- [ ] Stats numbers in black/grey (not blue)
- [ ] Tab navigation works
- [ ] Meeting cards monochrome
- [ ] No colored elements

### ✅ Knowledge Bank (`/knowledge/`)
- [ ] Left sidebar visible
- [ ] User profile in sidebar
- [ ] People tab shows 3 columns
- [ ] LinkedIn images load (or show initials)
- [ ] No duplicate names
- [ ] All elements monochrome
- [ ] Policies tab works

### ✅ Upload (`/upload-ui`)
- [ ] Left sidebar visible
- [ ] User profile in sidebar
- [ ] Grey dashed border on drop area
- [ ] File list appears
- [ ] Buttons monochrome

### ✅ Integration Test (`/integration-test`)
- [ ] Left sidebar visible
- [ ] User profile in sidebar
- [ ] 3 test cards in grid
- [ ] Test buttons work
- [ ] Status badges show (green/red ok for status)
- [ ] Auto-runs on load

### ✅ Meeting View (`/meeting/{id}`)
- [ ] Left sidebar visible
- [ ] User profile in sidebar
- [ ] Meeting title and meta
- [ ] Decisions section
- [ ] Action items section
- [ ] Attendees list

---

## How to Test

### 1. Hard Refresh
Clear cached CSS:
- **macOS**: `Cmd + Shift + R`
- **Windows**: `Ctrl + Shift + R`

### 2. Visit Each Page
- http://localhost:8000/dashboard-ui
- http://localhost:8000/knowledge/
- http://localhost:8000/upload-ui
- http://localhost:8000/integration-test
- http://localhost:8000/meeting/{some-id}

### 3. Check Consistency
- All pages have left sidebar
- All pages show user profile
- All pages monochrome (except status indicators)
- No colored icons anywhere

---

## Mobile Responsive

### Desktop (>768px)
- Sidebar visible (280px)
- Main content has left margin
- Full width grids

### Tablet/Mobile (<768px)
- Sidebar slides out (off-screen)
- Hamburger menu to toggle
- Single column grids
- Touch-friendly buttons

---

## User Profile Integration

### Current (Placeholder)
- Uses first person from database
- Shows name, email, LinkedIn image

### Future (With Auth)
```python
# Get from authenticated session
user = get_current_user(request)

get_admin_sidebar(
    active_page='dashboard',
    user_name=user.name,
    user_email=user.email,
    user_image_url=user.linkedin_url
)
```

---

## Status: ✅ COMPLETE

**All core pages updated**:
- ✅ Dashboard
- ✅ Knowledge Bank (3 columns, LinkedIn images, no duplicates)
- ✅ Upload Files
- ✅ Integration Tests (NEW PAGE)
- ✅ Meeting View

**User Profile**:
- ✅ Shown in sidebar footer on all pages
- ✅ LinkedIn image support
- ✅ Initials fallback
- ✅ Email display

**Design**:
- ✅ Monochrome throughout
- ✅ Left sidebar navigation
- ✅ Clean minimal aesthetic
- ✅ Claude-inspired layout

---

**Test now**: Hard refresh and visit `/integration-test` to see the new page! 🚀

**Last Updated**: December 16, 2025


