"""
Analysis Viewer Page - Detailed AI coding results
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import get_all_videos, get_motif_coding, get_transcript


def render_analysis_viewer_page():
    """Render the Analysis Viewer page"""
    st.title("🔬 Analysis Viewer")
    st.markdown("Detailed AI motif coding results")

    st.divider()

    # Get videos with AI coding
    all_videos = get_all_videos(has_captions=True)
    analyzed_videos = [v for v in all_videos if get_motif_coding(v.id) is not None]

    if not analyzed_videos:
        st.info("No analyzed videos yet. Add videos with captions to see AI analysis results.")
        st.stop()

    st.markdown(f"**{len(analyzed_videos)} videos analyzed**")

    # Video selector
    video_ids = [v.video_id for v in analyzed_videos]
    selected_video_id = st.selectbox(
        "Select video:",
        video_ids,
        format_func=lambda vid: next((v.title for v in analyzed_videos if v.video_id == vid), vid)
    )

    if not selected_video_id:
        st.stop()

    video = next(v for v in analyzed_videos if v.video_id == selected_video_id)
    motif = get_motif_coding(video.id)
    transcript = get_transcript(video.id)

    if not motif:
        st.warning("No AI analysis found for this video.")
        st.stop()

    results = motif.coding_results

    # Video header
    st.markdown(f"## {video.title}")
    st.markdown(f"**Channel:** {video.channel_name} | **Views:** {video.view_count:,}" if video.view_count else video.channel_name)
    st.markdown(f"[Watch on YouTube]({video.url})")

    st.divider()

    # Analysis tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "🏋️ Training & Performance",
        "🥗 Nutrition",
        "📚 Research & Credibility",
        "📝 Transcript"
    ])

    with tab1:
        st.subheader("Content Overview")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Primary Analysis")
            st.markdown(f"**Topic:** {results.get('primary_topic', 'N/A')}")
            st.markdown(f"**Target Audience:** {results.get('target_audience', 'N/A')}")
            st.markdown(f"**Content Quality:** {results.get('content_quality', 'N/A')}")

            st.markdown("#### Focus Areas")
            st.markdown(f"**Nutrition Focus:** {'✅ Yes' if results.get('nutrition_focus') else '❌ No'}")
            st.markdown(f"**Training Focus:** {'✅ Yes' if results.get('training_type') else '❌ No'}")
            st.markdown(f"**Recovery Focus:** {'✅ Yes' if results.get('recovery_methods') else '❌ No'}")

        with col2:
            st.markdown("#### Credibility Indicators")
            st.markdown(f"**Cites Research:** {'✅ Yes' if results.get('cites_research') else '❌ No'}")
            st.markdown(f"**Expert Featured:** {'✅ Yes' if results.get('expert_featured') else '❌ No'}")

            if results.get('studies_mentioned'):
                st.markdown("**Studies Mentioned:**")
                for study in results['studies_mentioned'][:5]:
                    st.markdown(f"- {study}")

        st.divider()

        # Main claims
        if results.get('main_claims'):
            st.markdown("#### Main Claims")
            for i, claim in enumerate(results['main_claims'], 1):
                st.markdown(f"{i}. {claim}")

        st.divider()

        # Key quotes
        if results.get('key_quotes'):
            st.markdown("#### Key Quotes")
            for quote in results['key_quotes'][:5]:
                with st.expander(f'"{quote["text"][:80]}..."'):
                    st.markdown(f'**Quote:** "{quote["text"]}"')
                    st.markdown(f'**Context:** {quote["context"]}')

        # Processing metadata
        st.divider()
        st.markdown("#### Processing Metadata")
        col1, col2, col3 = st.columns(3)
        col1.metric("Model", motif.model_used)
        col2.metric("Tokens Used", f"{motif.tokens_used:,}")
        col3.metric("Processing Time", f"{motif.processing_time}s")

    with tab2:
        st.subheader("Training & Performance Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Training types
            if results.get('training_type'):
                st.markdown("#### Training Types")
                for training in results['training_type']:
                    st.markdown(f"- {training.title()}")
            else:
                st.info("No specific training types identified")

            # Equipment
            if results.get('equipment_mentioned'):
                st.markdown("#### Equipment Mentioned")
                for equipment in results['equipment_mentioned']:
                    st.markdown(f"- {equipment}")

        with col2:
            # Recovery methods
            if results.get('recovery_methods'):
                st.markdown("#### Recovery Methods")
                for method in results['recovery_methods']:
                    st.markdown(f"- {method.title()}")
            else:
                st.info("No specific recovery methods identified")

            # Performance metrics
            if results.get('performance_metrics'):
                st.markdown("#### Performance Metrics")
                for metric in results['performance_metrics']:
                    st.markdown(f"- {metric}")

        # Technical details
        st.divider()
        st.markdown("#### Technical Details")

        detail_cols = st.columns(3)
        detail_cols[0].markdown(f"**Injury Prevention:** {'✅' if results.get('injury_prevention_discussed') else '❌'}")
        detail_cols[1].markdown(f"**Form/Technique:** {'✅' if results.get('form_technique_emphasized') else '❌'}")
        detail_cols[2].markdown(f"**Periodization:** {'✅' if results.get('periodization_mentioned') else '❌'}")

    with tab3:
        st.subheader("Nutrition Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Overview")
            st.markdown(f"**Nutrition Focus:** {'✅ Strong focus' if results.get('nutrition_focus') else '❌ Not a focus'}")
            st.markdown(f"**Diet Type:** {results.get('diet_type') or 'Not specified'}")
            st.markdown(f"**Meal Timing:** {'✅ Discussed' if results.get('meal_timing_discussed') else '❌ Not discussed'}")

            # Macros
            if results.get('macros_discussed'):
                st.markdown("#### Macros Discussed")
                for macro in results['macros_discussed']:
                    st.markdown(f"- {macro.title()}")

        with col2:
            # Supplements
            if results.get('supplements_mentioned'):
                st.markdown("#### Supplements Mentioned")
                for supplement in results['supplements_mentioned']:
                    st.markdown(f"- {supplement.title()}")
            else:
                st.info("No supplements mentioned")

            # Hydration
            st.markdown("#### Hydration")
            st.markdown(f"{'✅ Discussed' if results.get('hydration_discussed') else '❌ Not discussed'}")

        # Nutrition claims
        if results.get('main_claims'):
            nutrition_claims = [claim for claim in results['main_claims'] if any(
                word in claim.lower() for word in ['nutrition', 'diet', 'food', 'eat', 'protein', 'carb', 'fat', 'supplement']
            )]
            if nutrition_claims:
                st.divider()
                st.markdown("#### Nutrition-Related Claims")
                for claim in nutrition_claims:
                    st.markdown(f"- {claim}")

    with tab4:
        st.subheader("Research & Credibility")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Scientific Rigor")
            st.markdown(f"**Cites Research:** {'✅ Yes' if results.get('cites_research') else '❌ No'}")
            st.markdown(f"**Expert Featured:** {'✅ Yes' if results.get('expert_featured') else '❌ No'}")
            st.markdown(f"**Anecdotal Evidence:** {'⚠️ Yes' if results.get('anecdotal_evidence') else '✅ No'}")

            st.markdown("#### Content Credibility")
            quality = results.get('content_quality', 'unknown')
            if quality == 'high':
                st.success("✅ High Quality")
            elif quality == 'medium':
                st.warning("⚠️ Medium Quality")
            else:
                st.error("❌ Low Quality")

        with col2:
            # Studies mentioned
            if results.get('studies_mentioned'):
                st.markdown("#### Studies/Sources Referenced")
                for study in results['studies_mentioned']:
                    st.markdown(f"- {study}")
            else:
                st.info("No specific studies referenced")

            # Expert info
            if results.get('expert_featured'):
                if results.get('expert_credentials'):
                    st.markdown("#### Expert Credentials")
                    st.markdown(results['expert_credentials'])

        st.divider()

        # Research-backed claims
        if results.get('main_claims'):
            st.markdown("#### Evidence-Based Claims")
            if results.get('cites_research'):
                research_claims = [claim for claim in results['main_claims'] if any(
                    word in claim.lower() for word in ['study', 'research', 'university', 'journal', 'published']
                )]
                if research_claims:
                    for claim in research_claims:
                        st.markdown(f"✅ {claim}")
                else:
                    st.info("Claims made but specific research citations not extracted")
            else:
                st.warning("Content does not cite specific research")

    with tab5:
        st.subheader("Video Transcript")

        if transcript:
            st.markdown(f"**Language:** {transcript.language} | **Word Count:** {transcript.word_count:,}")

            if transcript.is_auto_generated:
                st.info("⚠️ This is an auto-generated transcript. Some errors may be present.")

            st.divider()

            # Search in transcript
            search_query = st.text_input("🔍 Search in transcript:", placeholder="Enter keywords...")

            # Display transcript
            transcript_text = transcript.raw_text

            if search_query:
                # Highlight search results
                import re
                pattern = re.compile(f"({re.escape(search_query)})", re.IGNORECASE)
                highlighted_text = pattern.sub(r"**\1**", transcript_text)
                st.markdown(highlighted_text)

                # Count matches
                matches = len(pattern.findall(transcript_text))
                st.info(f"Found {matches} match(es) for '{search_query}'")
            else:
                st.text_area(
                    "Full Transcript",
                    transcript_text,
                    height=400,
                    label_visibility="collapsed"
                )

            # Export transcript
            st.download_button(
                label="📥 Download Transcript",
                data=transcript_text,
                file_name=f"{video.video_id}_transcript.txt",
                mime="text/plain"
            )
        else:
            st.warning("No transcript available for this video")

    # Export analysis
    st.divider()
    st.subheader("Export Analysis")

    col1, col2 = st.columns([1, 3])

    with col2:
        if st.button("📥 Export Full Analysis (JSON)", use_container_width=False):
            import json

            export_data = {
                'video': {
                    'video_id': video.video_id,
                    'title': video.title,
                    'channel': video.channel_name,
                    'url': video.url,
                    'duration': video.duration,
                    'views': video.view_count,
                },
                'analysis': results,
                'metadata': {
                    'model': motif.model_used,
                    'tokens': motif.tokens_used,
                    'analyzed_at': motif.created_at.isoformat() if motif.created_at else None,
                }
            }

            json_str = json.dumps(export_data, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"{video.video_id}_analysis.json",
                mime="application/json"
            )
