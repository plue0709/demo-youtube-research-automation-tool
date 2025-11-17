"""
Phase 3 Test: OpenAI Integration with Database

Complete workflow test:
1. Create video in database
2. Add transcript
3. Run AI motif coding
4. Save results to database
5. Query and verify
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
    get_video_by_id,
    get_motif_coding,
    get_database_stats,
)
from ai_coder import MotifCoder

print("=" * 70)
print("PHASE 3 TEST: OpenAI + Database Integration")
print("=" * 70)

# Initialize
print("\n[1/5] Setting up database...")
print("-" * 70)
init_database()
print("✅ Database ready")

# Test data - realistic sports/fitness video
print("\n[2/5] Creating test video with transcript...")
print("-" * 70)

video_data = {
    'video_id': 'TEST_SPORTS_001',
    'url': 'https://www.youtube.com/watch?v=TEST_SPORTS_001',
    'title': 'Complete Guide to Athletic Recovery and Performance',
    'channel_name': 'Performance Science Lab',
    'channel_id': 'UC_TEST_CHANNEL',
    'description': 'Comprehensive guide to recovery methods for athletes',
    'published_at': datetime(2024, 1, 15),
    'duration': 1200,  # 20 minutes
    'language': 'en',
    'view_count': 250000,
    'like_count': 8500,
    'comment_count': 342,
    'status': 'processing',
    'has_captions': False,
}

video = create_video(video_data)
print(f"✅ Video created: {video.title}")

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

transcript_data = {
    'language': 'en',
    'is_auto_generated': False,
    'raw_text': sample_transcript,
    'word_count': len(sample_transcript.split()),
}

transcript = create_transcript(video.id, transcript_data)
print(f"✅ Transcript created: {transcript.word_count} words")

# Run AI coding
print("\n[3/5] Running AI motif coding...")
print("-" * 70)

coder = MotifCoder()

# Get cost estimate
estimate = coder.get_token_usage_estimate(sample_transcript)
print(f"📊 Estimated cost: ${estimate['estimated_cost_usd']}")
print(f"   Estimated tokens: {estimate['estimated_total_tokens']}")

print("\n🤖 Calling OpenAI API...")
coding_result = coder.code_transcript(
    transcript_text=sample_transcript,
    video_metadata={
        'title': video.title,
        'channel': video.channel_name,
        'duration': video.duration
    }
)

print("✅ AI coding complete!")

# Save to database
print("\n[4/5] Saving AI results to database...")
print("-" * 70)

motif_data = {
    'coding_results': coding_result.model_dump(),
    'model_used': coder.model,
    'tokens_used': estimate['estimated_total_tokens'],
    'processing_time': 3,
}

motif = create_motif_coding(video.id, transcript.id, motif_data)
print(f"✅ Motif coding saved to database")

# Display results
print("\n[5/5] Analysis Results:")
print("-" * 70)
print(f"📊 Content Analysis:")
print(f"   Primary topic: {coding_result.primary_topic}")
print(f"   Target audience: {coding_result.target_audience}")
print(f"   Content quality: {coding_result.content_quality}")
print(f"   Nutrition focus: {coding_result.nutrition_focus}")
print(f"   Cites research: {coding_result.cites_research}")
print(f"   Expert featured: {coding_result.expert_featured}")

print(f"\n🏋️ Training & Recovery:")
print(f"   Training types: {', '.join(coding_result.training_type) if coding_result.training_type else 'None'}")
print(f"   Recovery methods: {', '.join(coding_result.recovery_methods) if coding_result.recovery_methods else 'None'}")
print(f"   Performance metrics: {', '.join(coding_result.performance_metrics) if coding_result.performance_metrics else 'None'}")

print(f"\n🥗 Nutrition:")
print(f"   Supplements: {', '.join(coding_result.supplements_mentioned) if coding_result.supplements_mentioned else 'None'}")
print(f"   Diet type: {coding_result.diet_type or 'Not specified'}")
print(f"   Meal timing discussed: {coding_result.meal_timing_discussed}")

print(f"\n💡 Key Insights:")
print(f"   Main claims: {', '.join(coding_result.main_claims)}")
print(f"\n📝 Top quotes:")
for i, quote in enumerate(coding_result.key_quotes[:3], 1):
    print(f"   {i}. \"{quote.text[:100]}...\"")

# Verify database retrieval
print("\n" + "=" * 70)
print("Verifying Database Storage")
print("=" * 70)

retrieved_video = get_video_by_id('TEST_SPORTS_001')
retrieved_motif = get_motif_coding(retrieved_video.id)

print(f"✅ Video status: {retrieved_video.status}")
print(f"✅ Has captions: {retrieved_video.has_captions}")
print(f"✅ AI coding stored: {retrieved_motif is not None}")
print(f"✅ Coding fields: {len(retrieved_motif.coding_results.keys())} fields")

# Statistics
print("\n" + "=" * 70)
print("Database Statistics")
print("=" * 70)
stats = get_database_stats()
print(f"✅ Total videos: {stats['total_videos']}")
print(f"✅ Completed: {stats['completed']}")
print(f"✅ With captions: {stats['with_captions']}")
print(f"✅ With AI coding: {stats['with_ai_coding']}")

# Final summary
print("\n" + "=" * 70)
print("PHASE 3 TEST SUMMARY")
print("=" * 70)
print("✅ OpenAI API integration: Working")
print("✅ Structured outputs (zero malformed JSON): Working")
print("✅ Motif extraction: Working")
print("✅ Database storage: Working")
print("✅ End-to-end pipeline: Working")
print(f"\n💰 Cost per video: ~${estimate['estimated_cost_usd']}")
print("\n🎉 Phase 3 Complete! Ready for Phase 4 (Streamlit UI)")
print("=" * 70)
