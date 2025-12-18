# Architecture Consolidation Plan

## Current State

### Two Separate UIs:
1. **Frontend (Next.js)** - `localhost:3000`
   - Modern dark mode UI
   - Pages: /, /people, /dealflow, /portfolio, /tasks, /settings, /admin
   - React components with Tailwind CSS

2. **Backend Admin (FastAPI)** - `localhost:8000`
   - Python HTML templates
   - Pages: /wheels/people, /wheels/dealflow, /wheels/building, /wheels/admin
   - Server-side rendered HTML

## Proposed Architecture

### Single Unified UI (Next.js Frontend)
```
Frontend (localhost:3000)
├── Public Pages
│   └── / (login)
├── User Pages (Authenticated)
│   ├── /dashboard
│   ├── /people
│   ├── /dealflow
│   ├── /portfolio
│   └── /tasks
└── Admin Pages (Role: Admin/Owner)
    └── /settings
        ├── /settings/profile
        ├── /settings/api
        ├── /settings/integrations
        ├── /settings/people-admin      ← Backend /wheels/people
        ├── /settings/dealflow-admin    ← Backend /wheels/dealflow
        ├── /settings/companies-admin   ← Backend /wheels/dealflow/companies
        ├── /settings/building-admin    ← Backend /wheels/building
        └── /settings/system            ← Backend /wheels/admin
```

### Backend becomes pure API (localhost:8000)
```
Backend API (localhost:8000/api)
├── /api/auth
├── /api/people
├── /api/companies
├── /api/dealflow
├── /api/meetings
├── /api/tasks
└── /api/integrations
```

## Implementation Steps

### Phase 1: Authentication & Roles
1. Add auth provider to Next.js
2. Define user roles: Owner, Admin, Editor, Viewer
3. Create role-based route guards
4. Add role checking middleware

### Phase 2: Move Admin Features
1. Convert backend admin pages to React components
2. Place under /settings with role checks
3. Use backend API endpoints for data
4. Keep "Admin Only" warning for restricted pages

### Phase 3: API Integration
1. Create API client in frontend
2. Call backend endpoints from React
3. Handle authentication tokens
4. Error handling and loading states

### Phase 4: Cleanup
1. Remove backend HTML templates (keep API)
2. Update all links to new structure
3. Single port deployment (3000)

## Role-Based Access Control

### User Roles
```typescript
enum UserRole {
  OWNER = 'owner',        // Full access
  ADMIN = 'admin',        // Admin pages + user pages
  EDITOR = 'editor',      // User pages, can edit
  VIEWER = 'viewer'       // User pages, read-only
}
```

### Route Protection
```typescript
// Public routes (no auth)
['/login', '/']

// User routes (any authenticated user)
['/dashboard', '/people', '/dealflow', '/portfolio', '/tasks']

// Admin routes (admin/owner only)
['/settings/*']
```

### Navigation Logic
```typescript
// Show admin menu items only if user is admin/owner
{user.role === 'admin' || user.role === 'owner' ? (
  <Link href="/settings">Settings (Admin)</Link>
) : null}
```

## Benefits

✅ **Single UI** - One port, one interface  
✅ **Better UX** - Consistent dark mode, navigation  
✅ **Proper Auth** - Role-based access control  
✅ **Easier Deploy** - One frontend app  
✅ **Better Security** - Auth checks on every route  
✅ **Cleaner Code** - React components instead of HTML templates  

## Migration Priority

### High Priority (Do First)
1. Auth system with roles
2. Move Companies page to /settings/companies
3. Move People admin to /settings/people-admin
4. Role-based navigation

### Medium Priority
5. Move Dealflow admin pages
6. Move Building companies page
7. Integrate Linear sync UI

### Low Priority
8. Remove backend HTML templates
9. Refactor backend to pure API
10. Optimize API calls

## Example: Admin Page with Role Check

```typescript
// app/settings/companies/page.tsx
'use client'

import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function CompaniesAdminPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  
  useEffect(() => {
    if (!loading && (!user || user.role === 'viewer')) {
      router.push('/dashboard')
    }
  }, [user, loading, router])
  
  if (loading) return <div>Loading...</div>
  if (!user || user.role === 'viewer') return null
  
  return (
    <div>
      {/* Admin Only Banner */}
      <AdminAlert />
      
      {/* Companies Admin Content */}
      <CompaniesGrid />
    </div>
  )
}
```

## Tech Stack

### Frontend (Keep)
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Dark mode support

### Backend (Refactor to API-only)
- FastAPI (Python)
- Supabase (Database)
- Remove: HTML templates
- Keep: API endpoints, business logic

## Timeline Estimate

- **Week 1**: Auth system + roles
- **Week 2**: Move 3 key admin pages
- **Week 3**: Complete migration
- **Week 4**: Testing + cleanup

## Next Steps

1. Create auth context and hooks
2. Add role checking to existing pages
3. Create /settings/companies page (migrated from backend)
4. Update navigation with role checks
5. Test thoroughly before removing backend UI

---

**Decision**: Proceed with consolidation? This will modernize the entire system.


