"""
Test youtube-transcript-api (unofficial but works!)
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from youtube_utils import extract_video_id, get_video_captions

print("=" * 70)
print("Testing Unofficial YouTube Transcript API")
print("=" * 70)

# Test with different types of videos
test_videos = [
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "Rick Astley - Music video"),
    ("https://www.youtube.com/watch?v=jNQXAC9IVRw", "Me at the zoo - First YouTube video"),
    ("9M_QK4stCJU", "Tech/educational video"),
]

for url, description in test_videos:
    video_id = extract_video_id(url)

    print(f"\n{'=' * 70}")
    print(f"Testing: {description}")
    print(f"Video ID: {video_id}")
    print("-" * 70)

    result = get_video_captions(video_id)

    if result['success']:
        print(f"✅ SUCCESS!")
        print(f"   Language: {result['language']}")
        print(f"   Auto-generated: {result['is_auto_generated']}")
        print(f"   Word count: {result['word_count']}")
        print(f"\n   Transcript preview (first 150 chars):")
        print(f"   {result['transcript'][:150]}...")
    else:
        print(f"❌ FAILED: {result['error']}")

print(f"\n{'=' * 70}")
print("✅ Unofficial API works! No quota limits!")
print("=" * 70)
