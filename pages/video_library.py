"""
Video Library Page - Browse and manage all videos
"""

import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import get_all_videos, get_database_stats, delete_video, get_motif_coding


def render_video_library_page():
    """Render the Video Library page"""
    st.title("📊 Video Library")
    st.markdown("Browse and manage your video collection")

    st.divider()

    # Stats overview
    stats = get_database_stats()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Videos", stats['total_videos'])
    col2.metric("Completed", stats['completed'], delta=None)
    col3.metric("Processing", stats['processing'], delta=None)
    col4.metric("AI Analyzed", stats['with_ai_coding'])

    st.divider()

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Status Filter",
            ["All", "completed", "processing", "failed", "no_captions"],
            index=0
        )

    with col2:
        caption_filter = st.selectbox(
            "Caption Filter",
            ["All", "With Captions", "No Captions"],
            index=0
        )

    with col3:
        sort_by = st.selectbox(
            "Sort By",
            ["Newest First", "Oldest First", "Most Views", "Title A-Z"],
            index=0
        )

    # Get videos
    status_param = None if status_filter == "All" else status_filter
    caption_param = None if caption_filter == "All" else (caption_filter == "With Captions")

    videos = get_all_videos(status=status_param, has_captions=caption_param)

    # Sort videos
    if sort_by == "Newest First":
        videos = sorted(videos, key=lambda v: v.created_at, reverse=True)
    elif sort_by == "Oldest First":
        videos = sorted(videos, key=lambda v: v.created_at)
    elif sort_by == "Most Views":
        videos = sorted(videos, key=lambda v: v.view_count or 0, reverse=True)
    elif sort_by == "Title A-Z":
        videos = sorted(videos, key=lambda v: v.title or "")

    st.markdown(f"**Showing {len(videos)} videos**")

    if not videos:
        st.info("No videos found. Add some videos using the '➕ Add Videos' page!")
        st.stop()

    # Video table
    st.divider()

    # Convert to DataFrame for display
    video_data = []
    for video in videos:
        video_data.append({
            'Video ID': video.video_id,
            'Title': video.title[:60] + "..." if video.title and len(video.title) > 60 else video.title,
            'Channel': video.channel_name,
            'Duration': f"{video.duration // 60}:{video.duration % 60:02d}" if video.duration else "N/A",
            'Views': f"{video.view_count:,}" if video.view_count else "N/A",
            'Status': video.status,
            'Captions': "✅" if video.has_captions else "❌",
            'Created': video.created_at.strftime("%Y-%m-%d") if video.created_at else "N/A"
        })

    df = pd.DataFrame(video_data)

    # Display dataframe with selection
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Video ID": st.column_config.TextColumn("Video ID", width="small"),
            "Title": st.column_config.TextColumn("Title", width="large"),
            "Channel": st.column_config.TextColumn("Channel", width="medium"),
            "Duration": st.column_config.TextColumn("Duration", width="small"),
            "Views": st.column_config.TextColumn("Views", width="small"),
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Captions": st.column_config.TextColumn("Captions", width="small"),
            "Created": st.column_config.TextColumn("Created", width="small"),
        }
    )

    st.divider()

    # Video details section
    st.subheader("Video Details")

    video_ids = [v.video_id for v in videos]
    selected_video_id = st.selectbox(
        "Select a video to view details:",
        video_ids,
        format_func=lambda vid: next((v.title for v in videos if v.video_id == vid), vid)
    )

    if selected_video_id:
        video = next(v for v in videos if v.video_id == selected_video_id)

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"### {video.title}")
            st.markdown(f"**Channel:** {video.channel_name}")
            st.markdown(f"**URL:** [Watch on YouTube]({video.url})")

            if video.description:
                with st.expander("Description"):
                    st.write(video.description)

        with col2:
            st.markdown("#### Statistics")
            st.metric("Views", f"{video.view_count:,}" if video.view_count else "N/A")
            st.metric("Likes", f"{video.like_count:,}" if video.like_count else "N/A")
            st.metric("Comments", f"{video.comment_count:,}" if video.comment_count else "N/A")

        # Status info
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"**Status:** {video.status}")
        col2.markdown(f"**Captions:** {'✅ Yes' if video.has_captions else '❌ No'}")
        col3.markdown(f"**Duration:** {video.duration // 60}:{video.duration % 60:02d}" if video.duration else "N/A")

        # AI Analysis preview
        if video.has_captions:
            motif = get_motif_coding(video.id)
            if motif:
                st.divider()
                st.markdown("#### AI Analysis Preview")

                results = motif.coding_results

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Content:**")
                    st.markdown(f"- Topic: {results.get('primary_topic', 'N/A')}")
                    st.markdown(f"- Quality: {results.get('content_quality', 'N/A')}")
                    st.markdown(f"- Cites Research: {'✅' if results.get('cites_research') else '❌'}")

                with col2:
                    st.markdown("**Focus Areas:**")
                    st.markdown(f"- Nutrition: {'✅' if results.get('nutrition_focus') else '❌'}")
                    st.markdown(f"- Training: {len(results.get('training_type', [])) > 0 and '✅' or '❌'}")
                    st.markdown(f"- Recovery: {len(results.get('recovery_methods', [])) > 0 and '✅' or '❌'}")

                if results.get('supplements_mentioned'):
                    st.markdown(f"**Supplements:** {', '.join(results['supplements_mentioned'][:5])}")

                st.info("View full analysis in the '🔬 Analysis Viewer' page")

        # Actions
        st.divider()
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button("🗑️ Delete Video", use_container_width=True):
                if delete_video(video.video_id):
                    st.success("Video deleted!")
                    st.rerun()
                else:
                    st.error("Failed to delete video")

        with col2:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()

    st.divider()

    # Export section
    st.subheader("Export Data")

    col1, col2 = st.columns([1, 3])

    with col1:
        export_format = st.selectbox("Format", ["CSV", "JSON"])

    with col2:
        if st.button("📥 Export All Videos", use_container_width=False):
            # Prepare export data
            export_data = []
            for video in videos:
                motif = get_motif_coding(video.id) if video.has_captions else None

                row = {
                    'video_id': video.video_id,
                    'title': video.title,
                    'channel': video.channel_name,
                    'url': video.url,
                    'duration': video.duration,
                    'views': video.view_count,
                    'likes': video.like_count,
                    'status': video.status,
                    'has_captions': video.has_captions,
                    'created_at': video.created_at.isoformat() if video.created_at else None,
                }

                if motif:
                    results = motif.coding_results
                    row.update({
                        'primary_topic': results.get('primary_topic'),
                        'content_quality': results.get('content_quality'),
                        'cites_research': results.get('cites_research'),
                        'nutrition_focus': results.get('nutrition_focus'),
                        'supplements': ', '.join(results.get('supplements_mentioned', [])),
                        'training_types': ', '.join(results.get('training_type', [])),
                        'recovery_methods': ', '.join(results.get('recovery_methods', [])),
                    })

                export_data.append(row)

            if export_format == "CSV":
                df_export = pd.DataFrame(export_data)
                csv = df_export.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"youtube_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                import json
                json_str = json.dumps(export_data, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"youtube_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
