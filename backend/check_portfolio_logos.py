"""Check portfolio company logos."""
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Get portfolio companies with their organization info
result = supabase.table('portfolio_companies') \
    .select('*, organizations(*)') \
    .execute()

print("\n📊 Portfolio Companies Logos:\n")
for pc in result.data:
    org = pc.get('organizations', {})
    print(f"Company: {org.get('name')}")
    print(f"  Website: {org.get('website_url')}")
    print(f"  Logo URL: {org.get('logo_url')}")
    print(f"  Favicon URL: {org.get('favicon_url')}")
    print()

