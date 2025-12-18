"""Add Coeo's Pipedrive credentials to database (encrypted)."""
from supabase import create_client
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# Coeo Pipedrive credentials
COEO_PIPEDRIVE_TOKEN = "0082d57f308450640715cf7bf106a665287ddaaa"
COEO_DOMAIN = "coeo.pipedrive.com"

def encrypt_value(value: str) -> str:
    """Encrypt a value."""
    if not value:
        return ""
    f = Fernet(ENCRYPTION_KEY.encode())
    return f.encrypt(value.encode()).decode()


def add_coeo_integration():
    """Add Coeo's Pipedrive integration to database."""
    
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    print("\n🔐 Adding Coeo Pipedrive Integration to Database\n")
    
    # Get Coeo's portfolio company ID
    result = supabase.table('portfolio_companies') \
        .select('id, organizations(name)') \
        .execute()
    
    coeo_pc = None
    for pc in result.data:
        if pc['organizations']['name'] == 'Coeo':
            coeo_pc = pc
            break
    
    if not coeo_pc:
        print("❌ Coeo not found in portfolio_companies")
        return
    
    print(f"✅ Found Coeo (ID: {coeo_pc['id']})")
    
    # Encrypt the API token
    encrypted_token = encrypt_value(COEO_PIPEDRIVE_TOKEN)
    print(f"✅ Token encrypted")
    
    # Check if integration already exists
    existing = supabase.table('portfolio_company_integrations') \
        .select('id') \
        .eq('portfolio_company_id', coeo_pc['id']) \
        .eq('integration_type', 'pipedrive') \
        .execute()
    
    integration_data = {
        'portfolio_company_id': coeo_pc['id'],
        'integration_type': 'pipedrive',
        'api_token_encrypted': encrypted_token,
        'api_url': 'https://api.pipedrive.com/v1',
        'company_domain': COEO_DOMAIN,
        'is_active': True,
        'last_sync_status': 'success',
    }
    
    try:
        if existing.data:
            # Update existing
            supabase.table('portfolio_company_integrations') \
                .update(integration_data) \
                .eq('id', existing.data[0]['id']) \
                .execute()
            print(f"✅ Updated existing integration")
        else:
            # Insert new
            supabase.table('portfolio_company_integrations') \
                .insert(integration_data) \
                .execute()
            print(f"✅ Created new integration")
        
        print("\n" + "="*60)
        print("✅ Coeo Pipedrive Integration Saved to Database!")
        print("="*60)
        print("\nNow you can:")
        print("1. Remove PIPEDRIVE_API_TOKEN from .env")
        print("2. Go to http://localhost:8000/settings")
        print("3. See Coeo showing '✅ Connected' status")
        print("4. The Building page will pull credentials from database")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    add_coeo_integration()

