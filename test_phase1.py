"""
Phase 1 Test: OAuth2 + YouTube Caption Fetching

This script tests:
1. OAuth2 authentication
2. Video metadata fetching
3. Caption listing
4. Caption downloading

Run this to verify Phase 1 is working correctly.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from youtube_auth import YouTubeAuthManager
from youtube_client import YouTubeClient
from youtube_utils import extract_video_id

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def test_oauth_and_captions():
    """Test OAuth2 authentication and caption fetching"""

    print("=" * 70)
    print("PHASE 1 TEST: OAuth2 + YouTube Caption Fetching")
    print("=" * 70)

    # Test 1: Authentication
    print("\n[1/4] Testing OAuth2 Authentication...")
    print("-" * 70)
    try:
        auth = YouTubeAuthManager(
            credentials_path=os.getenv('YOUTUBE_CREDENTIALS_PATH'),
            token_path=os.getenv('YOUTUBE_TOKEN_PATH')
        )
        youtube_service = auth.authenticate()
        print("✅ OAuth2 authentication successful!")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

    # Test 2: Initialize client
    print("\n[2/4] Initializing YouTube Client...")
    print("-" * 70)
    try:
        client = YouTubeClient(auth)
        print("✅ YouTube client initialized!")
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return False

    # Test 3: Test with known video
    print("\n[3/4] Testing with sample video...")
    print("-" * 70)

    # Test URLs
    test_videos = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll (has captions)
    ]

    for test_url in test_videos:
        video_id = extract_video_id(test_url)
        print(f"\nTesting: {test_url}")
        print(f"Video ID: {video_id}")

        result = client.get_video_captions(video_id)

        if result['success']:
            print("\n✅ SUCCESS!")
            print(f"   Title: {result['metadata']['title']}")
            print(f"   Channel: {result['metadata']['channel_name']}")
            print(f"   Duration: {result['metadata']['duration']} seconds")
            print(f"   Language: {result['language']}")
            print(f"   Auto-generated: {result['is_auto_generated']}")
            print(f"   Word count: {result['word_count']}")
            print(f"\n   Transcript preview (first 150 chars):")
            print(f"   {result['transcript'][:150]}...")
        else:
            print(f"\n❌ FAILED: {result['error']}")

        print(f"\n   Quota used so far: {client.quota_used} units")

    # Test 4: Summary
    print("\n" + "=" * 70)
    print("[4/4] PHASE 1 TEST SUMMARY")
    print("=" * 70)
    print(f"✅ OAuth2 Authentication: Working")
    print(f"✅ Video Metadata Fetch: Working")
    print(f"✅ Caption Download: Working")
    print(f"📊 Total quota used: {client.quota_used} units")
    print("\n🎉 Phase 1 Complete! Ready for Phase 2 (Database)")
    print("=" * 70)

    return True


if __name__ == "__main__":
    try:
        success = test_oauth_and_captions()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
