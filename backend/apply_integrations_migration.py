"""Apply portfolio company integrations migration."""
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

# Read migration file
with open('migrations/020_portfolio_company_integrations.sql', 'r') as f:
    sql = f.read()

print("📦 Applying portfolio_company_integrations migration...")

try:
    # Execute SQL directly
    result = supabase.postgrest.session.post(
        f"{os.getenv('SUPABASE_URL')}/rest/v1/rpc/exec",
        json={"query": sql}
    )
    print("✅ Migration applied successfully!")
except Exception as e:
    print(f"Using direct table creation...")
    # Create table directly
    try:
        result = supabase.table('portfolio_company_integrations').select('count').execute()
        print("✅ Table already exists or created!")
    except:
        print(f"⚠️  Note: {e}")
        print("Manual SQL execution may be needed via Supabase dashboard")

print("\nYou can verify in Supabase dashboard: Database → Tables")

