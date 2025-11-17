"""
Populate database with demo data for Streamlit testing
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database import (
    init_database,
    create_video,
    create_transcript,
    create_motif_coding,
    get_database_stats,
)
from ai_coder import MotifCoder

print("=" * 70)
print("Populating Demo Data")
print("=" * 70)

# Initialize
print("\n[1/3] Initializing database...")
init_database()
print("✅ Database ready")

# Sample transcript - sports/fitness focused
sample_transcript = """
Welcome to our comprehensive guide on athletic recovery and performance optimization.

Today I want to talk about the most effective recovery methods backed by scientific research.
Ice baths, also known as cold water immersion, have been used by professional athletes
for decades. Research from Stanford University and the Journal of Sports Medicine shows
that cold exposure between 10-15 minutes can significantly reduce inflammation and
speed up recovery time after intense training sessions.

Let's discuss nutrition next. Protein intake is absolutely crucial for muscle recovery
and growth. Based on multiple studies, I recommend 1.6 to 2.2 grams of protein per
kilogram of body weight for athletes doing regular strength training. Timing matters too -
consuming protein within 2 hours post-workout maximizes muscle protein synthesis.

Regarding supplements, creatine monohydrate has the strongest research backing of any
supplement. Five grams per day has been shown to improve strength, power output, and
recovery. Whey protein is another evidence-based option, especially convenient for
hitting your daily protein targets.

Now, let's talk about training principles. Progressive overload is the foundation of any
strength training program. You need to gradually increase weight, reps, or sets over time
to see continued progress. This isn't optional - it's the fundamental driver of adaptation.

For endurance athletes, VO2 max training through high-intensity intervals can significantly
improve cardiovascular performance. Research shows intervals at 90-95% max heart rate
for 3-5 minutes are most effective.

Recovery isn't just about ice baths. Sleep is arguably the most important recovery tool.
Dr. Matthew Walker's research demonstrates that athletes need 8-10 hours of quality sleep
for optimal performance. During deep sleep, human growth hormone is released, which is
essential for muscle repair and adaptation.

Massage and foam rolling can help with muscle soreness, though the mechanisms are more
about pain modulation than actual tissue repair. Still, if it helps you feel better and
train more consistently, it's valuable.

Remember, consistency beats intensity. It's better to train at 80% effort six days a week
than 100% effort three days. Sustainable progress comes from showing up regularly, not
from occasional heroic efforts.

In conclusion, combine proper training with evidence-based recovery methods, adequate
protein nutrition, quality sleep, and you'll optimize your athletic performance.
"""

# Demo videos
demo_videos = [
    {
        'video_id': 'DEMO_SPORTS_001',
        'url': 'https://www.youtube.com/watch?v=DEMO_SPORTS_001',
        'title': 'Complete Guide to Athletic Recovery and Performance',
        'channel_name': 'Performance Science Lab',
        'channel_id': 'UC_DEMO_CHANNEL_1',
        'description': 'Comprehensive guide to recovery methods for athletes',
        'published_at': datetime(2024, 1, 15),
        'duration': 1200,  # 20 minutes
        'language': 'en',
        'view_count': 250000,
        'like_count': 8500,
        'comment_count': 342,
        'status': 'processing',
        'has_captions': False,
    },
    {
        'video_id': 'DEMO_SPORTS_002',
        'url': 'https://www.youtube.com/watch?v=DEMO_SPORTS_002',
        'title': 'Science-Based Training for Maximum Hypertrophy',
        'channel_name': 'Muscle Science Academy',
        'channel_id': 'UC_DEMO_CHANNEL_2',
        'description': 'Evidence-based approach to building muscle mass',
        'published_at': datetime(2024, 2, 1),
        'duration': 1580,  # 26 minutes
        'language': 'en',
        'view_count': 180000,
        'like_count': 6200,
        'comment_count': 198,
        'status': 'processing',
        'has_captions': False,
    },
    {
        'video_id': 'DEMO_SPORTS_003',
        'url': 'https://www.youtube.com/watch?v=DEMO_SPORTS_003',
        'title': 'Optimal Nutrition for Endurance Athletes',
        'channel_name': 'Endurance Nutrition Hub',
        'channel_id': 'UC_DEMO_CHANNEL_3',
        'description': 'Complete nutrition guide for runners, cyclists, and triathletes',
        'published_at': datetime(2024, 3, 10),
        'duration': 960,  # 16 minutes
        'language': 'en',
        'view_count': 95000,
        'like_count': 3100,
        'comment_count': 87,
        'status': 'no_captions',
        'has_captions': False,
    },
]

print("\n[2/3] Creating demo videos with AI analysis...")

coder = MotifCoder()

for i, video_data in enumerate(demo_videos, 1):
    print(f"\nProcessing video {i}/{len(demo_videos)}: {video_data['title'][:50]}...")

    # Create video
    video = create_video(video_data)
    print(f"  ✅ Video created: {video.video_id}")

    # Only add transcript and AI coding for first two videos
    if i <= 2:
        # Create transcript
        transcript_data = {
            'language': 'en',
            'is_auto_generated': False,
            'raw_text': sample_transcript,
            'word_count': len(sample_transcript.split()),
        }

        transcript = create_transcript(video.id, transcript_data)
        print(f"  ✅ Transcript created: {transcript.word_count} words")

        # Run AI coding
        coding_result = coder.code_transcript(
            transcript_text=sample_transcript,
            video_metadata={
                'title': video.title,
                'channel': video.channel_name,
                'duration': video.duration
            }
        )

        estimate = coder.get_token_usage_estimate(sample_transcript)

        # Save motif coding
        motif_data = {
            'coding_results': coding_result.model_dump(),
            'model_used': coder.model,
            'tokens_used': estimate['estimated_total_tokens'],
            'processing_time': 3,
        }

        create_motif_coding(video.id, transcript.id, motif_data)
        print(f"  ✅ AI analysis complete (${estimate['estimated_cost_usd']:.4f})")

print("\n[3/3] Database populated successfully!")

# Show stats
print("\n" + "=" * 70)
print("Database Statistics")
print("=" * 70)
stats = get_database_stats()
print(f"✅ Total videos: {stats['total_videos']}")
print(f"✅ Completed: {stats['completed']}")
print(f"✅ With captions: {stats['with_captions']}")
print(f"✅ With AI coding: {stats['with_ai_coding']}")

print("\n" + "=" * 70)
print("Demo Data Ready!")
print("=" * 70)
print("\nRun the Streamlit app:")
print("  streamlit run app.py")
print("\n" + "=" * 70)
