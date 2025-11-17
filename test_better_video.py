"""
Test with videos that have downloadable captions
"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from youtube_auth import YouTubeAuthManager
from youtube_client import YouTubeClient

load_dotenv()

print("=" * 70)
print("Testing YouTube Caption Download with Different Videos")
print("=" * 70)

auth = YouTubeAuthManager()
client = YouTubeClient(auth)

# Test with educational/tech videos (usually have open captions)
test_videos = [
    ("9M_QK4stCJU", "Tech talk video"),
    ("jNQXAC9IVRw", "Me at the zoo (first YouTube video)"),
    ("dQw4w9WgXcQ", "Rick Astley (might be protected)"),
]

for video_id, description in test_videos:
    print(f"\n{'=' * 70}")
    print(f"Testing: {description}")
    print(f"Video ID: {video_id}")
    print("-" * 70)

    result = client.get_video_captions(video_id)

    if result['success']:
        print(f"✅ SUCCESS!")
        print(f"   Title: {result['metadata']['title']}")
        print(f"   Language: {result['language']}")
        print(f"   Words: {result['word_count']}")
        print(f"   Preview: {result['transcript'][:150]}...")
        print(f"\n✅ This video works! Use it for demo.")
        break
    else:
        print(f"❌ Failed: {result['error']}")
        print(f"   Quota used: {client.quota_used}")

print(f"\n{'=' * 70}")
print(f"Total quota used: {client.quota_used} units")
print("=" * 70)
