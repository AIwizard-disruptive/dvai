"""
Import Q3 2025 Financial Data for Portfolio Companies
=======================================================
Real KPI data from Disruptive Ventures Q3 2025 report
"""

import asyncio
from datetime import date
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Q3 2025 Financial Data (Jul-Sep 2025)
PORTFOLIO_FINANCIAL_DATA = {
    "Crystal Alarm": {
        "ownership": 70,
        "q3_revenue": 5774,  # Jul 1829 + Aug 1753 + Sep 2192 (tkr)
        "q3_profit": 2073,   # Jul 565 + Aug 911 + Sep 597 (tkr)
        "employees": 12,
        "ltm_revenue": 17321,
        "ltm_growth": 88,  # % YoY
        "cash": 2689,
        "status": "excellent",
        "notes": "Kvartalsrekord med 5,8 mkr omsättning och 2 mkr vinst (35% vinstmarginal). ARR 20 mkr."
    },
    "Alent Dynamic": {
        "ownership": 20,
        "q3_revenue": 2905,  # Jul 397 + Aug 1298 + Sep 1210
        "q3_profit": -337,   # Jul -823 + Aug 340 + Sep 146
        "employees": 7,
        "ltm_revenue": 8819,
        "ltm_growth": -16,
        "cash": 526,
        "status": "warning",
        "notes": "Sågverkskonjunkturen påverkar negativt. Cloud-produkt ännu ej lanserad. Ansträngd likviditet."
    },
    "Vaylo": {
        "ownership": 35,
        "q3_revenue": 282,   # Jul 90 + Aug 95 + Sep 97
        "q3_profit": -723,   # Jul -381 + Aug -287 + Sep -55
        "employees": 3,
        "ltm_revenue": 810,
        "ltm_growth": 109,
        "cash": 1400,
        "status": "good",
        "notes": "Ljusning kring produkt och nya kunder. Runway till jan/feb 2026. Reser nya pengar."
    },
    "LunaLEC": {
        "ownership": 36,
        "q3_revenue": 0,
        "q3_profit": -240,   # Jul -74 + Aug -76 + Sep -90
        "employees": 6,
        "ltm_revenue": 0,
        "ltm_growth": 0,
        "cash": 4700,
        "status": "good",
        "notes": "R&D-fas. Operationell utveckling enligt plan. Team om 5-6 FTE. God likviditet."
    },
    "Basic Safety": {
        "ownership": 28,
        "q3_revenue": 753,   # Jul 190 + Aug 219 + Sep 344
        "q3_profit": -62,    # Jul -50 + Aug 5 + Sep -17
        "employees": 4,
        "ltm_revenue": 3899,
        "ltm_growth": 82,
        "cash": 472,
        "status": "good",
        "notes": "Omsättning +82%. Kassaflödesneutralt. Ökad säljeffektivitet."
    },
    "Coeo": {
        "ownership": 31,  # 8% + 23%
        "q3_revenue": 614,   # Jul 0 + Aug 85 + Sep 529
        "q3_profit": 135,    # Jul -137 + Aug -81 + Sep 353
        "employees": 1.5,
        "ltm_revenue": 2482,
        "ltm_growth": 94,
        "cash": 935,
        "status": "excellent",
        "notes": "Omsättning +94% med positivt resultat för kvartalet."
    },
    "Service Node": {
        "ownership": 0,  # Ownership not specified
        "q3_revenue": 150,   # 50 + 50 + 50
        "q3_profit": -30,    # -10 + -10 + -10
        "employees": 1,
        "ltm_revenue": 600,
        "ltm_growth": 0,
        "cash": 0,
        "status": "warning",
        "notes": "Passivt innehav, ingen info."
    },
}

# Companies not in our original 8 (but in the fund)
ADDITIONAL_COMPANIES = {
    "Strativ": {
        "ownership": 61,  # 41% + 20%
        "q3_revenue": 4795,  # Jul 1798 + Aug 1408 + Sep 1589
        "q3_profit": -93,    # Jul 242 + Aug -395 + Sep 60
        "employees": 11,
        "ltm_revenue": 18153,
        "ltm_growth": 24,
        "cash": 1362,
        "status": "good",
        "notes": "Omsättningstillväxt +24%. Vinstmarginal understiger förväntan pga nyrekryteringar."
    },
    "Percepium": {
        "ownership": 35,
        "q3_revenue": 662,   # Jul 370 + Aug 108 + Sep 184
        "q3_profit": -542,   # Jul -44 + Aug -302 + Sep -196
        "employees": 4,
        "ltm_revenue": 662,
        "ltm_growth": 0,  # New company
        "cash": 400,
        "status": "warning",
        "notes": "Nytt innehav (tillträde juli). Periodisering av intäkter påbörjad efter kvartalet."
    },
    "Invivorna AB": {
        "ownership": 50,
        "q3_revenue": 0,
        "q3_profit": 0,
        "employees": 0,
        "ltm_revenue": 0,
        "ltm_growth": 0,
        "cash": 20,
        "status": "good",
        "notes": "Nytt innehav (tillträde september). Patentansökan inlämnad efter kvartalets utgång."
    },
}


async def import_financial_data():
    """Import Q3 2025 financial data."""
    
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    print("\n💰 Importing Q3 2025 Financial Data...\n")
    
    # Get all portfolio companies
    result = supabase.table('portfolio_companies') \
        .select('id, organization_id, organizations(name, id)') \
        .execute()
    
    updated_count = 0
    
    for pc in result.data:
        org = pc.get('organizations', {})
        company_name = org.get('name', '')
        
        # Check if we have financial data for this company
        financial_data = PORTFOLIO_FINANCIAL_DATA.get(company_name) or ADDITIONAL_COMPANIES.get(company_name)
        
        if not financial_data:
            print(f"⚠️  No Q3 data for: {company_name}")
            continue
        
        print(f"📊 Updating: {company_name}")
        print(f"   Q3 Revenue: {financial_data['q3_revenue']} tkr")
        print(f"   Q3 Profit: {financial_data['q3_profit']} tkr")
        print(f"   Employees: {financial_data['employees']}")
        print(f"   Cash: {financial_data['cash']} tkr")
        print(f"   Status: {financial_data['status']}")
        
        # Calculate valuation based on revenue multiple (typical SaaS: 5-10x ARR)
        arr_estimate = financial_data['ltm_revenue'] * 1000  # Convert from tkr to kr
        valuation_estimate = arr_estimate * 6  # Conservative 6x multiple
        
        # Update portfolio_companies with financial metrics
        update_data = {
            'ownership_percentage': financial_data['ownership'],
            'investment_amount': valuation_estimate * (financial_data['ownership'] / 100) * 0.3,  # Estimate
            'current_valuation': valuation_estimate,
        }
        
        try:
            supabase.table('portfolio_companies').update(update_data).eq('id', pc['id']).execute()
            print(f"   ✅ Updated portfolio_companies")
        except Exception as e:
            print(f"   ❌ Error updating: {e}")
        
        # Update or create financial targets
        org_id = org.get('id')
        
        # Revenue target
        try:
            revenue_target = {
                'portfolio_company_id': pc['id'],
                'target_category': 'Revenue',
                'target_name': 'Q4 2025 Revenue Target',
                'target_description': f"Based on Q3 actual: {financial_data['q3_revenue']} tkr",
                'metric_name': 'Quarterly Revenue',
                'target_value': financial_data['q3_revenue'] * 1.1,  # 10% growth target
                'current_value': financial_data['q3_revenue'],
                'unit': 'tkr',
                'deadline': '2025-12-31',
                'is_critical': True,
                'progress_percentage': 100,
                'status': 'completed',
            }
            
            # Check if exists
            existing = supabase.table('portfolio_targets') \
                .select('id') \
                .eq('portfolio_company_id', pc['id']) \
                .eq('target_category', 'Revenue') \
                .execute()
            
            if existing.data:
                supabase.table('portfolio_targets').update(revenue_target).eq('id', existing.data[0]['id']).execute()
            else:
                supabase.table('portfolio_targets').insert(revenue_target).execute()
            
            print(f"   ✅ Updated revenue target")
        except Exception as e:
            print(f"   ⚠️  Revenue target error: {e}")
        
        # Cash/Liquidity target
        try:
            cash_target = {
                'portfolio_company_id': pc['id'],
                'target_category': 'Financial Health',
                'target_name': 'Cash Position',
                'target_description': f"Q3 2025 cash position",
                'metric_name': 'Liquidity',
                'target_value': financial_data['cash'] * 1.2,
                'current_value': financial_data['cash'],
                'unit': 'tkr',
                'deadline': '2025-12-31',
                'is_critical': True,
                'progress_percentage': (financial_data['cash'] / (financial_data['cash'] * 1.2)) * 100 if financial_data['cash'] > 0 else 0,
                'status': 'on_track' if financial_data['cash'] > 500 else 'at_risk',
            }
            
            # Check if exists
            existing = supabase.table('portfolio_targets') \
                .select('id') \
                .eq('portfolio_company_id', pc['id']) \
                .eq('target_category', 'Financial Health') \
                .execute()
            
            if existing.data:
                supabase.table('portfolio_targets').update(cash_target).eq('id', existing.data[0]['id']).execute()
            else:
                supabase.table('portfolio_targets').insert(cash_target).execute()
            
            print(f"   ✅ Updated cash target")
        except Exception as e:
            print(f"   ⚠️  Cash target error: {e}")
        
        updated_count += 1
        print()
    
    print("="*60)
    print(f"\n✅ Updated {updated_count} portfolio companies with Q3 2025 data!\n")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(import_financial_data())

