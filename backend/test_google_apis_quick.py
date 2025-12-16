#!/usr/bin/env python3
"""
Quick test to see which Google APIs are enabled and working
Run this to check current status without needing Google Cloud Console access
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.config import get_settings

settings = get_settings()

print("=" * 70)
print("GOOGLE API STATUS CHECK")
print("=" * 70)
print()

# Check OAuth credentials
print("✅ OAuth Credentials:")
print(f"   Client ID: {settings.google_client_id[:20]}...{settings.google_client_id[-10:]}")
print(f"   Client Secret: {settings.google_client_secret[:10]}...{settings.google_client_secret[-5:]}")
print()

# Check which APIs we can test
print("📋 APIs to test:")
print("   - Google Tasks API")
print("   - Google People API (Contacts)")
print("   - Google Directory API")
print()

print("🔧 How to test:")
print()
print("1. Start your backend server:")
print("   cd backend")
print("   uvicorn app.main:app --reload")
print()
print("2. Open in browser:")
print("   http://localhost:8000/integration-test")
print()
print("3. Click 'Connect Google' and authorize")
print()
print("4. After authorization, try these endpoints:")
print()
print("   Test Google Tasks:")
print("   curl http://localhost:8000/google/tasks")
print()
print("   Test Google Contacts:")
print("   curl http://localhost:8000/google/contacts")
print()
print("   Test Google Calendar:")
print("   curl http://localhost:8000/google/calendar")
print()
print("=" * 70)
print()

# Try to detect if we're already authorized
print("💡 Quick check - Do you have existing credentials?")
print()

# Check if there's a token file (common pattern)
token_files = [
    backend_path / "token.json",
    backend_path / "credentials.json",
    backend_path / ".credentials" / "token.json",
]

found_tokens = False
for token_file in token_files:
    if token_file.exists():
        print(f"   ✅ Found: {token_file}")
        found_tokens = True

if not found_tokens:
    print("   ℹ️  No existing token files found")
    print("   → You'll need to authorize via OAuth flow")
else:
    print()
    print("   ⚠️  Found existing tokens - might work without re-auth!")

print()
print("=" * 70)
print()
print("🎯 NEXT STEPS:")
print()
print("If APIs are NOT enabled, you'll see errors like:")
print('   "Google Tasks API has not been enabled"')
print('   "Access Not Configured"')
print()
print("If APIs ARE enabled but need authorization:")
print('   "Invalid Credentials" or "Login Required"')
print()
print("If APIs ARE enabled AND you\'re authorized:")
print("   ✅ You'll see actual task lists / contacts!")
print()
print("=" * 70)
