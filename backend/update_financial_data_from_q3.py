"""
Update Portfolio Companies with Q3 2025 Financial Data
========================================================
Real financial data from Disruptive Ventures Q3 2025 KPI report
"""

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Q3 2025 Financial Data (Jul-Sep 2025) - All values in thousands SEK (tkr)
Q3_FINANCIAL_DATA = {
    "Crystal Alarm": {
        "q3_revenue": 5774,      # Jul 1829 + Aug 1753 + Sep 2192
        "q3_profit": 2073,       # Jul 565 + Aug 911 + Sep 597
        "ltm_revenue": 17321,
        "ltm_growth_pct": 88,
        "employees": 12,
        "cash": 2689,
        "ownership_pct": 70,
        "status_note": "Kvartalsrekord med 35% vinstmarginal. ARR 20 mkr."
    },
    "Alent Dynamic": {
        "q3_revenue": 2905,
        "q3_profit": -337,
        "ltm_revenue": 8819,
        "ltm_growth_pct": -16,
        "employees": 7,
        "cash": 526,
        "ownership_pct": 20,
        "status_note": "Sågverkskonjunktur påverkar. Cloud-produkt ej lanserad. Ansträngd likviditet."
    },
    "Vaylo": {
        "q3_revenue": 282,
        "q3_profit": -723,
        "ltm_revenue": 810,
        "ltm_growth_pct": 109,
        "employees": 3,
        "cash": 1400,
        "ownership_pct": 35,
        "status_note": "Ljusning kring produkt. Runway till jan/feb 2026."
    },
    "LunaLEC": {
        "q3_revenue": 0,
        "q3_profit": -240,
        "ltm_revenue": 0,
        "ltm_growth_pct": 0,
        "employees": 6,
        "cash": 4700,
        "ownership_pct": 36,
        "status_note": "R&D-fas. Utveckling enligt plan. God likviditet."
    },
    "Basic Safety": {
        "q3_revenue": 753,
        "q3_profit": -62,
        "ltm_revenue": 3899,
        "ltm_growth_pct": 82,
        "employees": 4,
        "cash": 472,
        "ownership_pct": 28,
        "status_note": "Omsättning +82%. Kassaflödesneutralt. Ökad säljeffektivitet."
    },
    "Coeo": {
        "q3_revenue": 614,
        "q3_profit": 135,
        "ltm_revenue": 2482,
        "ltm_growth_pct": 94,
        "employees": 1.5,
        "cash": 935,
        "ownership_pct": 31,
        "status_note": "Omsättning +94% med positivt resultat."
    },
    "Service Node": {
        "q3_revenue": 150,
        "q3_profit": -30,
        "ltm_revenue": 600,
        "ltm_growth_pct": 0,
        "employees": 1,
        "cash": 0,
        "ownership_pct": 0,
        "status_note": "Passivt innehav."
    },
}


def update_financial_data():
    """Update portfolio companies with Q3 financial data."""
    
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    print("\n💰 Updating Portfolio Companies with Q3 2025 Financial Data\n")
    
    # Get portfolio companies
    result = supabase.table('portfolio_companies') \
        .select('id, organization_id, organizations(name)') \
        .execute()
    
    updated_count = 0
    
    for pc in result.data:
        org = pc.get('organizations', {})
        company_name = org.get('name', '')
        
        if company_name not in Q3_FINANCIAL_DATA:
            print(f"⚠️  No Q3 data for: {company_name}")
            continue
        
        data = Q3_FINANCIAL_DATA[company_name]
        
        print(f"📊 {company_name}")
        print(f"   Q3 Revenue: {data['q3_revenue']:,} tkr")
        print(f"   Q3 Profit: {data['q3_profit']:,} tkr")
        print(f"   LTM Revenue: {data['ltm_revenue']:,} tkr")
        print(f"   Growth: {data['ltm_growth_pct']}%")
        print(f"   Cash: {data['cash']:,} tkr")
        
        # Calculate valuation estimate (6x ARR for SaaS/tech companies)
        arr_kr = data['ltm_revenue'] * 1000  # Convert tkr to kr
        estimated_valuation = arr_kr * 6
        
        # Calculate investment amount based on ownership
        ownership_pct = data['ownership_pct']
        if ownership_pct > 0:
            investment_amount = estimated_valuation * (ownership_pct / 100)
        else:
            investment_amount = 0
        
        # Update portfolio_companies
        update_data = {
            'ownership_percentage': ownership_pct,
            'investment_amount': investment_amount,
            'current_valuation': estimated_valuation,
        }
        
        try:
            supabase.table('portfolio_companies').update(update_data).eq('id', pc['id']).execute()
            print(f"   ✅ Updated (Valuation: {(estimated_valuation/1000000):.1f}M kr)")
            updated_count += 1
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    print("="*60)
    print(f"✅ Updated {updated_count} companies with Q3 2025 financial data")
    print("="*60)


if __name__ == "__main__":
    update_financial_data()

