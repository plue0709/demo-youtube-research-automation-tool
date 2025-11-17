"""
YouTube Research Automation Tool - Streamlit Demo

Portfolio demo for analyzing sports/fitness/nutrition YouTube videos
"""

import streamlit as st
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database import init_database, get_database_stats

# Page config
st.set_page_config(
    page_title="YouTube Research Tool",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FF0000;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stat-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
@st.cache_resource
def setup_database():
    """Initialize database on first run"""
    init_database()
    return True

setup_database()

# Sidebar
with st.sidebar:
    st.image("https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg", use_container_width=True)
    st.markdown("### YouTube Research Tool")
    st.markdown("Automated analysis of sports & fitness content")

    st.divider()

    # Navigation
    st.markdown("### Navigation")
    page = st.radio(
        "Go to:",
        ["🏠 Dashboard", "➕ Add Videos", "📊 Video Library", "🔬 Analysis Viewer"],
        label_visibility="collapsed"
    )

    st.divider()

    # Database stats
    stats = get_database_stats()
    st.markdown("### Database Stats")
    st.metric("Total Videos", stats['total_videos'])
    st.metric("With Captions", stats['with_captions'])
    st.metric("AI Analyzed", stats['with_ai_coding'])

    st.divider()
    st.markdown("**Tech Stack:**")
    st.markdown("Streamlit • OpenAI • YouTube API")

# Main content area
if page == "🏠 Dashboard":
    st.markdown('<div class="main-header">YouTube Research Automation Tool</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Analyze sports, fitness & nutrition content at scale</div>', unsafe_allow_html=True)

    # Overview stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <div class="stat-number">{stats['total_videos']}</div>
            <div class="stat-label">Total Videos</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="stat-number">{stats['completed']}</div>
            <div class="stat-label">Completed</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="stat-number">{stats['with_captions']}</div>
            <div class="stat-label">With Captions</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <div class="stat-number">{stats['with_ai_coding']}</div>
            <div class="stat-label">AI Analyzed</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Features
    st.subheader("Features")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Data Collection")
        st.markdown("""
        - YouTube Data API v3 for metadata
        - Automated caption fetching
        - Video statistics tracking
        - Multi-video batch processing
        """)

        st.markdown("#### AI Analysis")
        st.markdown("""
        - OpenAI GPT-4o-mini integration
        - Structured motif coding
        - Sports & nutrition focus
        - Scientific credibility scoring
        """)

    with col2:
        st.markdown("#### Research Insights")
        st.markdown("""
        - Training methods extraction
        - Recovery protocols
        - Supplement mentions
        - Research citations tracking
        """)

        st.markdown("#### Export & Analysis")
        st.markdown("""
        - CSV export for Excel/R
        - Filtered searches
        - Detailed video analysis
        - Quote extraction
        """)

    st.divider()

    # System info
    st.subheader("System Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Backend:**")
        st.markdown("- SQLAlchemy ORM")
        st.markdown("- SQLite database")
        st.markdown("- Pydantic validation")

    with col2:
        st.markdown("**APIs:**")
        st.markdown("- YouTube Data API v3")
        st.markdown("- OpenAI API")
        st.markdown("- youtube-transcript-api")

    with col3:
        st.markdown("**Cost:**")
        st.markdown("- ~$0.0006 per video")
        st.markdown("- YouTube: Free tier")
        st.markdown("- Streamlit: Free hosting")

    st.divider()

    st.info("""
    **Demo Note:** This portfolio demo showcases the core functionality. The YouTube caption API
    has IP restrictions that require residential proxies in production. Code is ready for deployment
    with Webshare proxies (~$3.50 per 1,000 videos).
    """)

elif page == "➕ Add Videos":
    from pages.add_videos import render_add_videos_page
    render_add_videos_page()

elif page == "📊 Video Library":
    from pages.video_library import render_video_library_page
    render_video_library_page()

elif page == "🔬 Analysis Viewer":
    from pages.analysis_viewer import render_analysis_viewer_page
    render_analysis_viewer_page()
