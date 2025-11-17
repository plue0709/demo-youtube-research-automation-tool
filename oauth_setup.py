"""
OAuth2 Setup Helper for WSL

This script helps you authorize the YouTube API in WSL
where browsers don't auto-open.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from youtube_auth import YouTubeAuthManager

# Load environment variables
load_dotenv()

print("=" * 70)
print("YouTube OAuth2 Setup Helper")
print("=" * 70)
print()
print("This will authorize YouTube Data API access for caption downloading.")
print()
print("📋 INSTRUCTIONS FOR WSL USERS:")
print("1. A URL will be displayed below")
print("2. Copy the ENTIRE URL")
print("3. Open it in your Windows browser")
print("4. Sign in and authorize the app")
print("5. You'll be redirected to localhost:8080")
print("6. The script will automatically complete")
print()
print("=" * 70)
print()

input("Press ENTER when ready to continue...")

print("\n🔄 Starting OAuth2 flow...")
print("-" * 70)

try:
    auth = YouTubeAuthManager(
        credentials_path=os.getenv('YOUTUBE_CREDENTIALS_PATH'),
        token_path=os.getenv('YOUTUBE_TOKEN_PATH')
    )

    youtube_service = auth.authenticate()

    print("\n" + "=" * 70)
    print("✅ SUCCESS! OAuth2 authentication complete!")
    print("=" * 70)
    print(f"\n✓ Token saved to: {os.getenv('YOUTUBE_TOKEN_PATH')}")
    print("✓ You can now use YouTube API with full caption access")
    print("\nNext step: Run 'python test_phase1.py' to test caption fetching")
    print("=" * 70)

except KeyboardInterrupt:
    print("\n\n⚠️  Setup cancelled by user")
    sys.exit(1)
except Exception as e:
    print(f"\n\n❌ Error during OAuth setup:")
    print(f"   {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
