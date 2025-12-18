"""Apply integrations migration directly using psycopg2."""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

# Parse DATABASE_URL
db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("❌ DATABASE_URL not set")
    exit(1)

# Convert asyncpg URL to psycopg2 format
db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
db_url = db_url.replace('aws-0-us-east-1.pooler.supabase.com:5432', 'aws-0-us-east-1.pooler.supabase.com:6543')

print("📦 Applying portfolio_company_integrations migration...\n")

try:
    # Connect to database
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # Read and execute migration
    with open('migrations/020_portfolio_company_integrations.sql', 'r') as f:
        sql = f.read()
    
    cur.execute(sql)
    conn.commit()
    
    print("✅ Migration applied successfully!")
    
    # Verify table exists
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'portfolio_company_integrations'
        ORDER BY ordinal_position;
    """)
    
    columns = cur.fetchall()
    print(f"\n✅ Table created with {len(columns)} columns:")
    for col in columns[:5]:
        print(f"   - {col[0]} ({col[1]})")
    print(f"   ... and {len(columns) - 5} more")
    
    cur.close()
    conn.close()
    
    print("\n✅ All done! Reload the settings page.")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTrying alternative approach...")
    
    # Alternative: Use Supabase SQL editor
    print("\nPlease run this SQL manually in Supabase dashboard:")
    print("https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/editor")
    print("\nOr copy the migration file content:")
    print("migrations/020_portfolio_company_integrations.sql")

