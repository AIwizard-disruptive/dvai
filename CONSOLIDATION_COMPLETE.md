# Frontend/Backend Consolidation - Phase 1 Complete ✅

## What Was Built

Successfully started the consolidation of backend admin UI into the Next.js frontend with role-based access control.

## ✅ Completed

### 1. Authentication System
**Files Created:**
- `frontend/contexts/auth-context.tsx` - Auth context with role management
- `frontend/components/admin-route-guard.tsx` - Route protection component

**Features:**
- User roles: Owner, Admin, Editor, Viewer
- Role hierarchy with permission checks
- Mock authentication (ready for real API)
- Login/Logout functions
- `isAdmin` and `isOwner` helpers

### 2. Role-Based Navigation
**Updated:**
- `frontend/components/sidebar.tsx`

**Features:**
- Shows admin menu ONLY if user has admin/owner role
- Amber-colored "Admin Access" section
- Direct links to admin pages under settings
- Displays user role badge
- Dynamic user avatar with initials

### 3. First Admin Page Migrated
**Created:**
- `frontend/app/settings/companies/page.tsx`

**Features:**
- Protected by AdminRouteGuard
- Companies grid with logos from Clearbit
- Stats dashboard
- Responsive layout
- Dark mode support
- Ready to connect to backend API

### 4. Provider Integration
**Updated:**
- `frontend/components/providers.tsx`

**Order:**
```
QueryClient → AuthProvider → ThemeProvider → children
```

## Architecture

### Current Structure
```
Frontend (localhost:3000)
├── Public Pages
│   └── / (dashboard - will add login later)
├── User Pages (Authenticated)
│   ├── /people
│   ├── /dealflow
│   ├── /portfolio
│   └── /tasks
└── Admin Pages (Role: Admin/Owner Only)
    └── /settings
        ├── /settings (profile, API keys)
        └── /settings/companies → NEW! Admin only
```

### Role-Based Access

```typescript
// Role Hierarchy
Owner (4)    → Full access to everything
Admin (3)    → Admin pages + user pages
Editor (2)   → User pages, can edit
Viewer (1)   → User pages, read-only
```

### Permission Checking

```typescript
// In any component
const { isAdmin, checkPermission } = useAuth()

// Show admin content
{isAdmin && <AdminMenu />}

// Check specific role
{checkPermission('admin') && <AdminFeature />}
```

## Navigation Flow

### Before (Two Separate UIs)
```
localhost:3000 (Next.js)  → User pages
localhost:8000 (FastAPI)  → Admin pages
```

### After (Unified)
```
localhost:3000 (Next.js)
├── User pages (Everyone)
└── /settings/* (Admin/Owner only)
    └── Shows admin content with role check
```

## Admin Menu in Sidebar

```
┌─────────────────────────────────┐
│ ADMIN ACCESS                     │
│ [shield icon]                    │
│ → Companies Admin                │
│ → System Admin                   │
└─────────────────────────────────┘
```

Only visible if `user.role === 'admin' || 'owner'`

## Example: Protected Admin Page

```typescript
// app/settings/companies/page.tsx
export default function CompaniesAdminPage() {
  return (
    <AdminRouteGuard requiredRole="admin">
      <AppLayout>
        {/* Admin content here */}
      </AppLayout>
    </AdminRouteGuard>
  )
}
```

### How Route Guard Works:
1. Checks if user is logged in
2. Checks if user has required role
3. Shows loading spinner while checking
4. Redirects if unauthorized
5. Shows content if authorized

## Migration Status

### ✅ Migrated to Frontend
- [x] Companies page (from `/wheels/dealflow/companies`)
- [x] Role-based navigation
- [x] Auth system with roles
- [x] Admin route protection

### 🔄 To Be Migrated
- [ ] People admin (from `/wheels/people`)
- [ ] Dealflow admin (from `/wheels/dealflow`)
- [ ] Building companies (from `/wheels/building`)
- [ ] System admin (from `/wheels/admin`)

### 📋 API Endpoints Needed
```
Backend API (localhost:8000/api)
├── GET  /api/companies          → List companies
├── GET  /api/companies/:domain  → Get company details
├── POST /api/companies          → Create company
└── ... (more endpoints)
```

## User Roles

### Development Default
```typescript
// Currently defaults to Owner role
{
  id: '1',
  name: 'Markus Löwegren',
  email: 'markus.lowegren@disruptiveventures.com',
  role: 'owner',
  organization: 'Disruptive Ventures'
}
```

### To Change Role (Development)
```javascript
// In browser console
localStorage.setItem('dv-user', JSON.stringify({
  id: '2',
  name: 'Test User',
  email: 'test@example.com',
  role: 'viewer', // or 'editor', 'admin', 'owner'
  organization: 'Test Org'
}))

// Refresh page
location.reload()
```

## Testing

### Test Admin Access
1. **Start frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Visit pages:**
   - http://localhost:3000/ → Should work
   - http://localhost:3000/settings → Should work
   - http://localhost:3000/settings/companies → Should work (you're owner)

3. **Test role restriction:**
   ```javascript
   // In browser console
   localStorage.setItem('dv-user', JSON.stringify({
     role: 'viewer', name: 'Viewer', email: 'viewer@test.com'
   }))
   location.reload()
   ```
   - Admin menu should disappear
   - /settings/companies should redirect to /dashboard

### Test Navigation
1. Open sidebar
2. Look for "ADMIN ACCESS" section (amber colored)
3. Should show:
   - Companies Admin link
   - System Admin link
4. Only visible if you're admin/owner

## Benefits Achieved

✅ **Single UI** - No more switching between ports  
✅ **Role-based access** - Proper security with role checks  
✅ **Better UX** - Consistent dark mode, navigation  
✅ **Admin protection** - Route guards prevent unauthorized access  
✅ **Easy to extend** - Add more admin pages with same pattern  

## Next Steps

### Phase 2: Migrate More Admin Pages
1. `/settings/people-admin` (from `/wheels/people`)
2. `/settings/dealflow-admin` (from `/wheels/dealflow`)
3. `/settings/building-admin` (from `/wheels/building`)
4. `/settings/system` (from `/wheels/admin`)

### Phase 3: Real Authentication
```typescript
// Replace mock auth with real API
const login = async (email, password) => {
  const response = await fetch('http://localhost:8000/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password })
  })
  const userData = await response.json()
  setUser(userData)
}
```

### Phase 4: Connect to Backend APIs
```typescript
// In admin pages, call backend
const companies = await fetch('http://localhost:8000/api/companies')
const data = await companies.json()
```

### Phase 5: Remove Backend HTML
Once all admin pages migrated:
- Remove FastAPI HTML template routes
- Keep only API endpoints
- Backend becomes pure API server

## File Structure

```
frontend/
├── app/
│   └── settings/
│       ├── page.tsx              # Settings home
│       ├── companies/
│       │   └── page.tsx          # Admin: Companies (NEW)
│       ├── people-admin/
│       │   └── page.tsx          # Admin: People (TODO)
│       └── system/
│           └── page.tsx          # Admin: System (TODO)
├── components/
│   ├── admin-route-guard.tsx     # Route protection (NEW)
│   ├── sidebar.tsx               # Updated with admin menu
│   └── providers.tsx             # Added AuthProvider
└── contexts/
    └── auth-context.tsx          # Auth + roles (NEW)
```

## Summary

✅ **Phase 1 Complete**  
✅ **Auth system** with Owner/Admin/Editor/Viewer roles  
✅ **Route protection** with AdminRouteGuard  
✅ **Role-based navigation** in sidebar  
✅ **First admin page** migrated (Companies)  
✅ **Ready to migrate** more admin pages  

**Status:** Foundation complete, ready to migrate remaining pages ✨  
**Next:** Migrate People, Dealflow, Building, System admin pages


