"""
Phase 2 Test: Database Setup & Operations

Tests:
1. Database initialization
2. Create video record
3. Create transcript record
4. Create motif coding record
5. Query operations
6. Statistics
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database import (
    init_database,
    create_video,
    get_video_by_id,
    create_transcript,
    get_transcript,
    create_motif_coding,
    get_motif_coding,
    get_database_stats,
    get_all_videos,
)

print("=" * 70)
print("PHASE 2 TEST: Database Setup & Operations")
print("=" * 70)

# Test 1: Initialize database
print("\n[1/6] Initializing database...")
print("-" * 70)
init_database()
print("✅ Database initialized successfully!")

# Test 2: Create video record
print("\n[2/6] Creating test video record...")
print("-" * 70)
video_data = {
    'video_id': 'dQw4w9WgXcQ',
    'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    'title': 'Rick Astley - Never Gonna Give You Up (Official Video)',
    'channel_name': 'Rick Astley',
    'channel_id': 'UCuAXFkgsw1L7xaCfnd5JJOw',
    'description': 'Official music video',
    'published_at': datetime(2009, 10, 25),
    'duration': 213,  # 3:33
    'language': 'en',
    'view_count': 1500000000,
    'like_count': 15000000,
    'comment_count': 2000000,
    'status': 'processing',
    'has_captions': False,
}

video = create_video(video_data)
print(f"✅ Created video: {video.title}")
print(f"   Video ID: {video.video_id}")
print(f"   Database PK: {video.id}")

# Test 3: Create transcript record
print("\n[3/6] Creating test transcript record...")
print("-" * 70)
transcript_data = {
    'language': 'en',
    'is_auto_generated': True,
    'raw_text': "We're no strangers to love. You know the rules and so do I. A full commitment's what I'm thinking of. You wouldn't get this from any other guy. I just wanna tell you how I'm feeling. Gotta make you understand. Never gonna give you up, never gonna let you down...",
    'word_count': 780,
}

transcript = create_transcript(video.id, transcript_data)
print(f"✅ Created transcript")
print(f"   Language: {transcript.language}")
print(f"   Word count: {transcript.word_count}")
print(f"   Auto-generated: {transcript.is_auto_generated}")

# Test 4: Create motif coding record
print("\n[4/6] Creating test motif coding record...")
print("-" * 70)
coding_data = {
    'coding_results': {
        'recovery_methods': [],
        'training_type': ['dance', 'performance'],
        'nutrition_focus': False,
        'supplements_mentioned': [],
        'cites_research': False,
        'expert_featured': True,
        'primary_topic': 'music',
        'target_audience': 'general',
        'content_quality': 'high',
        'key_quotes': [
            {
                'text': "Never gonna give you up, never gonna let you down",
                'context': "Main chorus and theme of commitment"
            }
        ],
        'main_claims': ['Commitment', 'Loyalty', 'Love'],
    },
    'model_used': 'gpt-4o-mini',
    'tokens_used': 1500,
    'processing_time': 3,
}

motif = create_motif_coding(video.id, transcript.id, coding_data)
print(f"✅ Created motif coding")
print(f"   Model: {motif.model_used}")
print(f"   Tokens used: {motif.tokens_used}")
print(f"   Primary topic: {motif.coding_results.get('primary_topic')}")

# Test 5: Query operations
print("\n[5/6] Testing query operations...")
print("-" * 70)

# Retrieve video
retrieved_video = get_video_by_id('dQw4w9WgXcQ')
print(f"✅ Retrieved video: {retrieved_video.title}")

# Retrieve transcript
retrieved_transcript = get_transcript(video.id)
print(f"✅ Retrieved transcript: {retrieved_transcript.word_count} words")

# Retrieve motif coding
retrieved_motif = get_motif_coding(video.id)
print(f"✅ Retrieved motif coding: {retrieved_motif.model_used}")

# Get all videos
all_videos = get_all_videos()
print(f"✅ Total videos in database: {len(all_videos)}")

# Test 6: Statistics
print("\n[6/6] Database statistics...")
print("-" * 70)
stats = get_database_stats()
print(f"✅ Statistics:")
for key, value in stats.items():
    print(f"   {key}: {value}")

# Summary
print("\n" + "=" * 70)
print("PHASE 2 TEST SUMMARY")
print("=" * 70)
print("✅ Database initialization: Working")
print("✅ Video CRUD operations: Working")
print("✅ Transcript operations: Working")
print("✅ Motif coding operations: Working")
print("✅ Query operations: Working")
print("✅ Statistics: Working")
print("\n🎉 Phase 2 Complete! Database ready for Phase 3 (OpenAI)")
print("=" * 70)
