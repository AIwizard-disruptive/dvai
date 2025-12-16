# 🧪 Test These URLs - New UI Ready!

## ✅ Server Running on Port 8000

All pages have been updated with:
- Left sidebar navigation (Claude-style)
- Monochrome design (dark grey icons only)
- User profile in sidebar
- Clean minimal layout

---

## 📍 Pages to Test

### 1. Dashboard
**URL**: http://localhost:8000/dashboard-ui

**Should see**:
- ✅ Left sidebar with navigation
- ✅ User profile at bottom (with LinkedIn photo)
- ✅ Stats cards in monochrome (black numbers)
- ✅ Tab navigation (Meetings/Decisions/Actions)
- ✅ All cards clean and minimal

---

### 2. Knowledge Bank
**URL**: http://localhost:8000/knowledge/

**Should see**:
- ✅ Left sidebar
- ✅ Two tabs: Policies | People
- ✅ People tab: **3 columns** ✨
- ✅ LinkedIn profile photos or initials
- ✅ No duplicate names
- ✅ "View Profile" button on each person

**Click "People" tab** to see the 3-column grid!

---

### 3. Person Profile (NEW PAGE)
**URL**: http://localhost:8000/knowledge/person/7a0870c9-7f08-4c62-87b6-312ee85d1c0a

**Should see**:
- ✅ Left sidebar
- ✅ Large profile photo (100px)
- ✅ Name, title, email, phone
- ✅ LinkedIn and Email buttons
- ✅ Meetings attended section
- ✅ Action items assigned section
- ✅ Back button to Knowledge Bank

---

### 4. Integration Tests (NEW PAGE)
**URL**: http://localhost:8000/integration-test

**Should see**:
- ✅ Left sidebar
- ✅ 3 test cards (Supabase, Google, Linear)
- ✅ Tests run automatically on page load
- ✅ Status badges (green = connected, red = error)
- ✅ "Run All Tests" button
- ✅ Monochrome layout

---

### 5. Upload Files
**URL**: http://localhost:8000/upload-ui

**Should see**:
- ✅ Left sidebar
- ✅ Grey dashed upload area
- ✅ Drag & drop support
- ✅ File list appears after selection
- ✅ Monochrome buttons

---

### 6. Meeting View
**URL**: http://localhost:8000/meeting/{some-meeting-id}

**Should see**:
- ✅ Left sidebar
- ✅ Meeting title and details
- ✅ Summary section
- ✅ Decisions list
- ✅ Action items list
- ✅ Attendees list

---

## 🔄 Testing Steps

### For Each Page:

1. **Open URL** in browser
2. **Hard Refresh**: `Cmd + Shift + R` (important - clears CSS cache)
3. **Check Sidebar**: Should see left navigation
4. **Check User Profile**: Should see profile at bottom of sidebar
5. **Check Content**: Main area should be clean and monochrome
6. **Check Icons**: All icons should be dark grey (no colors)

---

## 🎯 Key Things to Verify

### Knowledge Bank People Tab
Go to: http://localhost:8000/knowledge/

1. Click "People" tab
2. **Verify**:
   - ✓ Shows in 3 columns
   - ✓ LinkedIn photos load (or shows initials)
   - ✓ No duplicate people
   - ✓ Can click "View Profile"

### Person Profile Page
Click "View Profile" on anyone, then **verify**:
- ✓ Large profile photo at top
- ✓ LinkedIn/Email buttons work
- ✓ Meetings list shows
- ✓ Action items list shows
- ✓ Back button works

### Sidebar on All Pages
**Verify**:
- ✓ Same sidebar on every page
- ✓ User profile shows at bottom
- ✓ Navigation links work
- ✓ Admin warning visible
- ✓ All icons dark grey (no colors)

---

## 🐛 If You See Issues

### "Still see old design"
→ **Hard refresh required**: `Cmd + Shift + R`

### "Sidebar not showing"
→ Check browser console for errors
→ Try different browser

### "People tab doesn't show 3 columns"
→ Hard refresh
→ Check browser width (desktop size)

### "LinkedIn images not loading"
→ Check if `linkedin_url` field has valid URLs in database
→ Initials should show as fallback

### "Person profile shows 404"
→ Use person ID from database
→ Check URL is correct format

### "Upload page has purple gradient"
→ **Hard refresh** - CSS is cached
→ Clear browser cache completely

---

## ✅ All Features Delivered

### What You Asked For:
1. ✅ Claude-inspired minimal design
2. ✅ Left sidebar (not top header)
3. ✅ Clear navigation between sections
4. ✅ People / Dealflow / Portfolio / Admin
5. ✅ Monochrome icons (NO colors)
6. ✅ 3 column people grid
7. ✅ LinkedIn profile images
8. ✅ User profile display
9. ✅ Remove duplicate people
10. ✅ Admin-only messaging

### Bonus Features:
- ✅ Person detail pages
- ✅ Integration test page
- ✅ Auto-running tests
- ✅ Mobile responsive
- ✅ Clean empty states

---

## 📝 Quick Reference

**Server**: Running on http://localhost:8000  
**Design**: Claude-inspired monochrome  
**Sidebar**: Left navigation on all pages  
**User**: Profile in sidebar footer  
**People**: 3 columns with LinkedIn photos  
**Duplicates**: Automatically removed  

---

## 🎉 Start Testing!

**Best page to start**: http://localhost:8000/knowledge/

1. Hard refresh: `Cmd + Shift + R`
2. Click "People" tab
3. See 3 columns with LinkedIn photos
4. Click "View Profile" on anyone
5. Explore the new interface!

**Everything is ready!** 🚀


