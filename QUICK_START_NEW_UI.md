# Quick Start - New Claude-Inspired UI

## What Changed?

Your Disruptive Ventures app has been completely redesigned with a minimalistic Claude-inspired interface featuring:

✅ **Sliding sidebar navigation** (like Claude's interface)  
✅ **Four clear wheels**: People / Dealflow / Portfolio Companies / Admin  
✅ **Clean, minimal design** with subtle interactions  
✅ **Mobile-responsive** with overlay sidebar  
✅ **Integration reminders** emphasizing Google/Linear as primary tools  

## Start the App

### 1. Install Dependencies (if needed)

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The app will be available at **http://localhost:3000**

## Navigation Guide

### Home Page (`/`)
- Clean hub with four wheel cards
- Click any card to navigate to that wheel
- Each wheel has a color-coded icon

### Sliding Sidebar
- **Desktop**: Click hamburger menu (top-left) to open/close
- **Mobile**: Sidebar slides over content with dark overlay
- **Auto-close**: Sidebar closes automatically on mobile after navigation

### Four Wheels

| Wheel | Route | Color | Purpose |
|-------|-------|-------|---------|
| People | `/people` | Blue | Relationship management, contacts |
| Dealflow | `/dealflow` | Green | Investment pipeline tracking |
| Portfolio | `/portfolio` | Purple | Portfolio company monitoring |
| Admin | `/admin` | Gray | System configuration |

## Design Philosophy

### This is the "Brain"
- **Strategic oversight** - not for daily operations
- **Limited access** - only partners and admins need regular access
- **Integration-first** - most work happens in Google and Linear

### Visual Language
- **Minimalism**: Clean, white backgrounds with subtle gray borders
- **Typography-focused**: Clear hierarchy, generous spacing
- **Intentional interactions**: Smooth animations, clear feedback
- **Consistent**: Same patterns across all wheels

## Key Features by Wheel

### People Wheel
- Contact categories (Founders, Investors, Advisors, etc.)
- Recent activity feed
- Meeting intelligence integration
- Google Contacts sync reminder

### Dealflow Wheel
- Pipeline overview (Sourcing → Review → DD → Decision)
- Key metrics (investment targets, conversion rate, cycle time)
- Active deals requiring attention
- Linear integration for deal tracking

### Portfolio Wheel
- Portfolio overview (companies, invested amount, growth)
- Companies requiring attention (at risk, watch list)
- Top performers this quarter
- Multi-source data aggregation

### Admin Wheel
- System status (database, API usage)
- Integration management (Google, Linear, Whisperflow)
- Configuration sections (users, security, templates, etc.)
- Four wheels architecture documentation

## File Structure

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Home page (wheel hub)
│   ├── globals.css             # Global styles
│   ├── people/page.tsx         # People wheel
│   ├── dealflow/page.tsx       # Dealflow wheel
│   ├── portfolio/page.tsx      # Portfolio wheel
│   └── admin/page.tsx          # Admin wheel
├── components/
│   ├── sidebar.tsx             # Sliding navigation
│   ├── app-layout.tsx          # Wheel page wrapper
│   └── ui/                     # shadcn/ui components
└── lib/
    └── utils.ts                # Utilities (cn function)
```

## Testing the UI

### 1. Home Page
- ✅ Four wheel cards visible
- ✅ Hover states work (arrow animates, subtle shadow)
- ✅ Clicking cards navigates to wheels

### 2. Sidebar Navigation
- ✅ Click hamburger to open sidebar
- ✅ Sidebar slides in from left
- ✅ Active route highlighted in gray
- ✅ Click outside to close (mobile)
- ✅ Navigation links work

### 3. Responsive Design
- ✅ Resize browser to mobile width
- ✅ Sidebar becomes overlay
- ✅ Grids collapse to single column
- ✅ Touch-friendly tap targets

### 4. Each Wheel Page
- ✅ Header with colored icon badge
- ✅ Quick stats cards
- ✅ Content sections with proper spacing
- ✅ Integration reminder at bottom
- ✅ Hover states on interactive elements

## Customization

### Change Colors

Edit `app/globals.css` for theme colors:

```css
/* Current: Minimal grayscale with wheel-specific accents */
/* Wheel colors are in individual page files */
```

### Add Real Data

Pages currently show template data. To connect real data:

1. Create API routes in `app/api/`
2. Use React hooks to fetch data
3. Replace template arrays with fetched data
4. Add loading states

### Modify Sidebar

Edit `components/sidebar.tsx`:
- Change navigation items
- Adjust colors/icons
- Add user profile section
- Modify footer message

## Next Steps

### Phase 1: Connect Backend
- [ ] Create API routes for each wheel
- [ ] Fetch real data from Supabase
- [ ] Add authentication
- [ ] Implement user sessions

### Phase 2: Enhance Features
- [ ] Add search functionality
- [ ] Create detail pages (person, deal, company)
- [ ] Add data visualization charts
- [ ] Implement real-time updates

### Phase 3: Polish
- [ ] Add loading states
- [ ] Implement error handling
- [ ] Add empty states
- [ ] Create onboarding flow

## Troubleshooting

### Sidebar not appearing?
- Check browser console for errors
- Verify `components/sidebar.tsx` exists
- Make sure you're on a wheel page (not home)

### Styles not loading?
- Restart dev server: `npm run dev`
- Clear browser cache
- Check `app/globals.css` exists

### Navigation not working?
- Check Next.js routing in browser console
- Verify all page files exist in `app/` directory
- Check for TypeScript errors: `npm run build`

### Mobile layout broken?
- Test in Chrome DevTools mobile view
- Check Tailwind responsive classes (md:, sm:)
- Verify viewport meta tag in layout

## Documentation

📄 **Full Design Documentation**: `NEW_DESIGN_CLAUDE_UI.md`  
📄 **Component Details**: See individual files in `components/`  
📄 **Backend Integration**: Coming in next phase  

## Support

This is a template/starting point. All data shown is example data for layout purposes. 

**Ready to customize and connect to your real backend!**

---

**Status**: ✅ Ready to Run  
**Version**: 1.0  
**Last Updated**: December 16, 2025
