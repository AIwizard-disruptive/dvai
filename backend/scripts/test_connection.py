#!/usr/bin/env python
"""Test Supabase connection and database access."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import create_async_engine
from supabase import create_client, Client

from app.config import settings


async def test_postgres_connection():
    """Test direct PostgreSQL connection."""
    print("=" * 60)
    print("Testing PostgreSQL Connection")
    print("=" * 60)
    
    try:
        # Create engine
        engine = create_async_engine(settings.database_url, echo=True)
        
        async with engine.begin() as conn:
            # Test basic query
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✓ Connected to PostgreSQL")
            print(f"  Version: {version[:50]}...")
            
            # Check if our schema exists
            result = await conn.execute(
                text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'orgs'")
            )
            orgs_exists = result.scalar()
            
            if orgs_exists:
                print("✓ Schema exists (orgs table found)")
                
                # Count existing orgs
                result = await conn.execute(text("SELECT COUNT(*) FROM orgs"))
                org_count = result.scalar()
                print(f"  Organizations in database: {org_count}")
            else:
                print("✗ Schema not found - migrations need to be run")
                print("  Run: python scripts/migrate.py")
            
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"✗ PostgreSQL connection failed: {e}")
        return False


def test_supabase_client():
    """Test Supabase client connection."""
    print("\n" + "=" * 60)
    print("Testing Supabase Client Connection")
    print("=" * 60)
    
    try:
        # Create Supabase client
        supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_anon_key
        )
        
        print(f"✓ Supabase client created")
        print(f"  URL: {settings.supabase_url}")
        
        # Test a simple query (this might fail if RLS is enabled and we're not authenticated)
        try:
            response = supabase.table('orgs').select("*").limit(5).execute()
            print(f"✓ Query executed successfully")
            print(f"  Organizations found: {len(response.data)}")
            
            if response.data:
                print("\n  Sample organization:")
                for org in response.data[:1]:
                    print(f"    ID: {org.get('id')}")
                    print(f"    Name: {org.get('name')}")
        except Exception as e:
            print(f"⚠ Query failed (this is normal if RLS is enabled): {e}")
            print("  Note: RLS requires authentication - this is expected for security")
        
        return True
        
    except Exception as e:
        print(f"✗ Supabase client failed: {e}")
        return False


async def test_create_org():
    """Test creating a test organization."""
    print("\n" + "=" * 60)
    print("Testing Database Write (Creating Test Org)")
    print("=" * 60)
    
    try:
        from app.database import AsyncSessionLocal
        from app.models import Org
        import uuid
        
        async with AsyncSessionLocal() as session:
            # Check if test org exists
            result = await session.execute(
                text("SELECT id, name FROM orgs WHERE name = 'Test Organization' LIMIT 1")
            )
            existing = result.first()
            
            if existing:
                print(f"✓ Test organization already exists")
                print(f"  ID: {existing[0]}")
                print(f"  Name: {existing[1]}")
            else:
                # Create test org using raw SQL (bypasses RLS for service role)
                test_org_id = str(uuid.uuid4())
                await session.execute(
                    text("""
                        INSERT INTO orgs (id, name, created_at, updated_at)
                        VALUES (:id, :name, NOW(), NOW())
                    """),
                    {"id": test_org_id, "name": "Test Organization"}
                )
                await session.commit()
                
                print(f"✓ Created test organization")
                print(f"  ID: {test_org_id}")
                print(f"  Name: Test Organization")
            
        return True
        
    except Exception as e:
        print(f"✗ Failed to create test org: {e}")
        print(f"  This might be due to RLS - you may need service_role key")
        return False


async def show_current_config():
    """Show current configuration."""
    print("\n" + "=" * 60)
    print("Current Configuration")
    print("=" * 60)
    
    print(f"Supabase URL: {settings.supabase_url}")
    print(f"Database URL: {settings.database_url[:50]}...")
    print(f"Anon Key: {settings.supabase_anon_key[:20]}...")
    
    # Check which APIs are configured
    print(f"\nTranscription Providers:")
    print(f"  Klang: {'✓ Configured' if settings.klang_api_key else '✗ Not configured'}")
    print(f"  Mistral: {'✓ Configured' if settings.mistral_api_key else '✗ Not configured'}")
    print(f"  OpenAI: {'✓ Configured' if settings.openai_api_key else '✗ Not configured'}")
    
    print(f"\nIntegrations:")
    print(f"  Linear: {'✓ Configured' if settings.linear_api_key else '✗ Not configured'}")
    print(f"  Google: {'✓ Configured' if settings.google_client_id else '✗ Not configured'}")
    
    print(f"\nRedis: {settings.redis_url}")


async def main():
    """Run all connection tests."""
    print("\n" + "=" * 60)
    print("SUPABASE CONNECTION TEST")
    print("=" * 60)
    
    await show_current_config()
    
    # Test PostgreSQL
    pg_ok = await test_postgres_connection()
    
    # Test Supabase client
    sb_ok = test_supabase_client()
    
    # Test write capability
    if pg_ok:
        write_ok = await test_create_org()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if pg_ok and sb_ok:
        print("✓ All connection tests passed!")
        print("\nNext steps:")
        print("1. If schema doesn't exist, run: python scripts/migrate.py")
        print("2. Start the API: uvicorn app.main:app --reload")
        print("3. Start Celery: celery -A app.worker.celery_app worker --loglevel=info")
        print("4. Test API: curl http://localhost:8000/health")
    else:
        print("✗ Some tests failed. Check configuration in backend/.env")
        print("\nTroubleshooting:")
        print("- Verify DATABASE_URL is correct (should use asyncpg driver)")
        print("- Check Supabase credentials are valid")
        print("- Ensure network connectivity to Supabase")


if __name__ == "__main__":
    asyncio.run(main())



