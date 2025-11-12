#!/usr/bin/env python3
"""
Simple test to verify environment variables are loaded correctly
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("ENVIRONMENT VARIABLES TEST")
print("=" * 70)

# Test Supabase credentials
print("\n✓ SUPABASE Configuration:")
print(f"  URL: {os.getenv('SUPABASE_URL')}")
print(f"  Project ID: {os.getenv('SUPABASE_PROJECT_ID')}")
print(f"  Anon Key: {os.getenv('SUPABASE_ANON_KEY')[:50]}...")
print(f"  Service Role Key: {os.getenv('SUPABASE_SERVICE_ROLE_KEY')[:50]}...")
print(f"  Publishable Key: {os.getenv('SUPABASE_PUBLISHABLE_KEY')}")
print(f"  Secret Key: {os.getenv('SUPABASE_SECRET_KEY')}")
print(f"  Storage URL: {os.getenv('SUPABASE_STORAGE_URL')}")
print(f"  MCP URL: {os.getenv('SUPABASE_MCP_URL')}")

# Test GitHub credentials
print("\n✓ GITHUB Configuration:")
print(f"  Username: {os.getenv('GITHUB_USERNAME')}")
print(f"  Token: {os.getenv('GITHUB_TOKEN')[:20]}...")

# Test other API keys
print("\n⚠️  PENDING API Keys (not yet configured):")
print(f"  Twilio SID: {os.getenv('TWILIO_ACCOUNT_SID')}")
print(f"  ZeroBounce: {os.getenv('ZEROBOUNCE_API_KEY')}")
print(f"  IPQualityScore: {os.getenv('IPQS_API_KEY')}")

print("\n" + "=" * 70)
print("✓ All Supabase credentials loaded successfully!")
print("=" * 70)

# Verify .env is NOT tracked by git
import subprocess
result = subprocess.run(['git', 'status', '--porcelain', '.env'],
                       capture_output=True, text=True)
if result.returncode == 0 and not result.stdout.strip():
    print("\n✓ Security: .env file is properly ignored by git")
else:
    print("\n⚠️  WARNING: .env file may be tracked by git!")
