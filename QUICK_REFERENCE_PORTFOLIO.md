# Portfolio Companies - Quick Reference 🚀

## What Was Done

✅ **Added 8 portfolio companies** to database  
✅ **Created 24 portfolio targets** (3 per company)  
✅ **Added 6 founder records** to people table  
✅ **Styled company selector** with modern design  
✅ **Dark mode support** fully implemented  
✅ **Responsive design** for mobile devices  

---

## Access the Feature

**URL:** http://localhost:8000/wheels/building

---

## Portfolio Companies

| # | Company | Website | Industry |
|---|---------|---------|----------|
| 1 | Crystal Alarm | crystalalarm.se | Security Tech |
| 2 | LumberScan | lumberscan.com | Forest Tech |
| 3 | Alent Dynamic | alentdynamic.se | Industrial Tech |
| 4 | LunaLEC | lunalec.com | Lighting Tech |
| 5 | Vaylo | vaylo.com | Travel Tech |
| 6 | Coeo | coeo.events | Event Tech |
| 7 | Basic Safety | basic-safety.se | Safety Equipment |
| 8 | Service Node | servicenode.se | Service Tech |

---

## Key Features

### 1. Company Selector Dropdown
- Select between DV and 8 portfolio companies
- Beautiful gradient design
- Custom icons and emojis
- LocalStorage persistence

### 2. Three Kanban Boards
- **Activities** - Linear task tracking
- **Dealflow** - Pipedrive deal pipeline
- **Financial** - Fortnox invoice tracking

### 3. Portfolio Targets
Each company tracks:
- Revenue targets (MRR)
- Growth targets (customers)
- Product targets (completion %)

---

## Run Scripts

### Add Companies (if needed again):
```bash
cd backend
source venv/bin/activate
python add_portfolio_companies.py
```

### Add Sample Data:
```bash
cd backend
source venv/bin/activate
python add_portfolio_company_data.py
```

---

## Database Tables

- `organizations` - Company records
- `portfolio_companies` - Investment details
- `portfolio_targets` - KPI tracking
- `people` - Founder records

---

## Files Modified

1. `backend/app/api/wheel_building.py` - Enhanced with company selector
2. `backend/add_portfolio_companies.py` - Created
3. `backend/add_portfolio_company_data.py` - Created

---

## Documentation

- `PORTFOLIO_COMPANIES_ADDED.md` - Full details
- `COMPANY_SELECTOR_STYLING.md` - Design specs
- `QUICK_REFERENCE_PORTFOLIO.md` - This file

---

## What's Next?

### Recommended Enhancements:
1. Add company logos (run logo scraper)
2. Create company cards view (grid layout)
3. Filter tasks/deals by selected company
4. Add financial dashboard per company
5. Setup CEO dashboard URLs

### Integration Ideas:
- Linear: Company-specific projects
- Pipedrive: Deal tracking per company
- Fortnox: Per-company financials
- Email: Automated investor updates

---

## Quick Commands

### Start Backend:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Check Health:
```bash
curl http://localhost:8000/health
```

### View Page:
```bash
open http://localhost:8000/wheels/building
```

---

## Support

Need to update a company? Check these files:
- Database: Use Supabase dashboard
- Scripts: `/backend/add_portfolio_*.py`
- UI: `/backend/app/api/wheel_building.py`

---

**Status:** ✅ Complete and Ready for Production

**Last Updated:** December 17, 2025

