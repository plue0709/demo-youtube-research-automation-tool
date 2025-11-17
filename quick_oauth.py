"""
Quick OAuth2 Setup (Non-Interactive)

Run this, then immediately open the URL in your browser
"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from youtube_auth import YouTubeAuthManager

load_dotenv()

print("\n" + "=" * 70)
print("🔐 YouTube OAuth2 Setup")
print("=" * 70)
print("\n📝 When the URL appears:")
print("   1. Copy it completely")
print("   2. Open in your browser")
print("   3. Sign in & authorize")
print("   4. Wait for 'Success!' message")
print("\n" + "-" * 70 + "\n")

try:
    auth = YouTubeAuthManager(
        credentials_path=os.getenv('YOUTUBE_CREDENTIALS_PATH'),
        token_path=os.getenv('YOUTUBE_TOKEN_PATH')
    )
    youtube_service = auth.authenticate()

    print("\n" + "=" * 70)
    print("✅ SUCCESS! OAuth2 Complete!")
    print("=" * 70)
    print(f"✓ Token saved: {os.getenv('YOUTUBE_TOKEN_PATH')}")
    print("✓ Ready to fetch captions!")
    print("\nNext: Run 'python test_phase1.py'")
    print("=" * 70 + "\n")

except Exception as e:
    print(f"\n❌ Error: {str(e)}\n")
    sys.exit(1)
