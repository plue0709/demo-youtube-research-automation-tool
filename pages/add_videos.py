"""
Add Videos Page - Upload interface for YouTube video URLs
"""

import streamlit as st
import sys
import os
from datetime import datetime
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from youtube_utils import extract_video_id, get_video_captions
from youtube_client import YouTubeClient
from youtube_auth import YouTubeAuthManager
from database import create_video, create_transcript, get_video_by_id
from ai_coder import MotifCoder
from database import create_motif_coding


def process_video_url(url: str, youtube_client: YouTubeClient, progress_container) -> dict:
    """Process a single video URL through the complete pipeline"""
    try:
        # Extract video ID
        video_id = extract_video_id(url)
        if not video_id:
            return {"success": False, "error": "Invalid YouTube URL"}

        progress_container.write(f"📹 Processing: {video_id}")

        # Check if already exists
        existing = get_video_by_id(video_id)
        if existing:
            return {"success": False, "error": "Video already in database"}

        # Get metadata from YouTube API
        progress_container.write("⏳ Fetching metadata...")
        metadata = youtube_client.get_video_metadata(video_id)
        if not metadata:
            return {"success": False, "error": "Failed to fetch metadata"}

        # Create video record
        video_data = {
            'video_id': video_id,
            'url': url,
            'title': metadata.get('title'),
            'channel_name': metadata.get('channel_name'),
            'channel_id': metadata.get('channel_id'),
            'description': metadata.get('description'),
            'published_at': datetime.fromisoformat(metadata['published_at'].replace('Z', '+00:00')) if metadata.get('published_at') else None,
            'duration': metadata.get('duration_seconds'),
            'language': metadata.get('language'),
            'view_count': metadata.get('view_count'),
            'like_count': metadata.get('like_count'),
            'comment_count': metadata.get('comment_count'),
            'status': 'processing',
            'has_captions': False,
        }

        video = create_video(video_data)
        progress_container.write(f"✅ Video created: {video.title[:50]}...")

        # Get captions (unofficial API)
        progress_container.write("⏳ Fetching captions...")
        caption_result = get_video_captions(video_id)

        if not caption_result['success']:
            # Update video as failed
            from database import update_video
            update_video(video_id, {'status': 'no_captions', 'error_message': caption_result['error']})
            return {
                "success": False,
                "error": f"No captions available: {caption_result['error']}",
                "video_created": True
            }

        # Create transcript
        transcript_data = {
            'language': caption_result['language'],
            'is_auto_generated': caption_result.get('is_auto_generated', False),
            'raw_text': caption_result['transcript'],
            'word_count': caption_result['word_count'],
        }

        transcript = create_transcript(video.id, transcript_data)
        progress_container.write(f"✅ Transcript saved: {transcript.word_count} words")

        # Run AI coding
        progress_container.write("⏳ Running AI analysis...")
        coder = MotifCoder()

        coding_result = coder.code_transcript(
            transcript_text=caption_result['transcript'],
            video_metadata={
                'title': video.title,
                'channel': video.channel_name,
                'duration': video.duration
            }
        )

        # Get token estimate
        estimate = coder.get_token_usage_estimate(caption_result['transcript'])

        # Save motif coding
        motif_data = {
            'coding_results': coding_result.model_dump(),
            'model_used': coder.model,
            'tokens_used': estimate['estimated_total_tokens'],
            'processing_time': 3,
        }

        create_motif_coding(video.id, transcript.id, motif_data)
        progress_container.write(f"✅ AI analysis complete! (${estimate['estimated_cost_usd']:.4f})")

        return {
            "success": True,
            "video_id": video_id,
            "title": video.title,
            "cost": estimate['estimated_cost_usd']
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def render_add_videos_page():
    """Render the Add Videos page"""
    st.title("➕ Add Videos")
    st.markdown("Add YouTube videos for analysis")

    # Check if OAuth2 credentials are available
    import os
    credentials_path = os.getenv('YOUTUBE_CREDENTIALS_PATH', 'config/credentials.json')

    if not os.path.exists(credentials_path):
        st.warning("⚠️ **Cloud Deployment Mode**: Video upload requires OAuth2 credentials which are not available in cloud deployments.")
        st.info("""
        **This feature works locally only.**

        On Streamlit Cloud, OAuth2 credentials cannot be used (requires browser interaction).

        **Options:**
        1. **View Demo Data**: Check the "📊 Video Library" to see pre-populated sample videos
        2. **Run Locally**: Clone the repo and run locally with your OAuth2 credentials
        3. **GitHub**: View source code to see the full implementation

        [View on GitHub](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME)
        """)
        st.stop()

    st.divider()

    # Input method tabs
    tab1, tab2 = st.tabs(["Single URL", "Batch Upload"])

    with tab1:
        st.subheader("Add Single Video")

        url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Paste a YouTube video URL"
        )

        col1, col2 = st.columns([1, 3])

        with col1:
            process_button = st.button("Process Video", type="primary", use_container_width=True)

        if process_button and url:
            with st.spinner("Processing video..."):
                progress_container = st.container()

                # Initialize YouTube client
                try:
                    auth_manager = YouTubeAuthManager()
                    youtube_client = YouTubeClient(auth_manager)
                except Exception as e:
                    st.error(f"Failed to initialize YouTube client: {e}")
                    st.info("Make sure OAuth2 credentials are set up correctly.")
                    st.stop()

                result = process_video_url(url, youtube_client, progress_container)

                if result['success']:
                    st.success(f"✅ Video processed successfully!")
                    st.markdown(f"**Title:** {result['title']}")
                    st.markdown(f"**Video ID:** {result['video_id']}")
                    st.markdown(f"**Cost:** ${result['cost']:.4f}")
                    st.balloons()
                else:
                    if result.get('video_created'):
                        st.warning(f"⚠️ Video added but captions unavailable: {result['error']}")
                        st.info("The video metadata has been saved. You can try again later or use manual transcription.")
                    else:
                        st.error(f"❌ Error: {result['error']}")

    with tab2:
        st.subheader("Batch Upload")

        st.markdown("""
        Upload multiple videos at once. Paste one URL per line:
        """)

        urls_text = st.text_area(
            "Video URLs (one per line)",
            height=200,
            placeholder="https://www.youtube.com/watch?v=...\nhttps://www.youtube.com/watch?v=...\nhttps://www.youtube.com/watch?v=..."
        )

        batch_button = st.button("Process Batch", type="primary", use_container_width=False)

        if batch_button and urls_text:
            urls = [url.strip() for url in urls_text.split('\n') if url.strip()]

            st.info(f"Processing {len(urls)} videos...")

            # Initialize YouTube client
            try:
                auth_manager = YouTubeAuthManager()
                youtube_client = YouTubeClient(auth_manager)
            except Exception as e:
                st.error(f"Failed to initialize YouTube client: {e}")
                st.stop()

            # Process each video
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, url in enumerate(urls):
                status_text.text(f"Processing {i+1}/{len(urls)}: {url[:50]}...")
                progress_container = st.expander(f"Video {i+1}: {url[:50]}...", expanded=False)

                result = process_video_url(url, youtube_client, progress_container)
                results.append(result)

                progress_bar.progress((i + 1) / len(urls))

            # Summary
            st.divider()
            st.subheader("Batch Processing Summary")

            success_count = sum(1 for r in results if r['success'])
            total_cost = sum(r.get('cost', 0) for r in results if r['success'])

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Processed", len(urls))
            col2.metric("Successful", success_count)
            col3.metric("Total Cost", f"${total_cost:.4f}")

            # Details table
            if results:
                st.markdown("#### Details")
                for i, (url, result) in enumerate(zip(urls, results), 1):
                    if result['success']:
                        st.success(f"{i}. ✅ {result['title'][:60]}... (${result['cost']:.4f})")
                    else:
                        st.error(f"{i}. ❌ {url[:60]}... - {result['error']}")

    st.divider()

    # Demo note
    st.info("""
    **Demo Limitation:** The unofficial YouTube caption API may be blocked from certain IPs.
    This demo showcases the complete code pipeline. In production, residential proxies
    (Webshare, ~$3.50 per 1,000 videos) would be used to ensure reliable caption access.
    """)

    # Quick test data
    with st.expander("🧪 For Testing: Sample Video URLs"):
        st.markdown("""
        These videos typically have captions available:

        - `https://www.youtube.com/watch?v=dQw4w9WgXcQ` (Music video)
        - `https://www.youtube.com/watch?v=jNQXAC9IVRw` (First YouTube video)
        - `https://www.youtube.com/watch?v=9M_QK4stCJU` (Tech/education)

        **Note:** Caption availability depends on IP blocks. Use these to test the metadata
        fetching and database insertion, even if captions are blocked.
        """)
