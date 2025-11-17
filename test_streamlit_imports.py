"""
Quick test to verify all Streamlit page imports work
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 70)
print("Testing Streamlit Page Imports")
print("=" * 70)

# Test main app imports
print("\n[1/4] Testing main app imports...")
try:
    from database import init_database, get_database_stats
    print("✅ Main app imports successful")
except Exception as e:
    print(f"❌ Main app import error: {e}")
    sys.exit(1)

# Test add_videos page
print("\n[2/4] Testing add_videos page...")
try:
    from pages.add_videos import render_add_videos_page
    print("✅ Add videos page imports successful")
except Exception as e:
    print(f"❌ Add videos page import error: {e}")
    sys.exit(1)

# Test video_library page
print("\n[3/4] Testing video_library page...")
try:
    from pages.video_library import render_video_library_page
    print("✅ Video library page imports successful")
except Exception as e:
    print(f"❌ Video library page import error: {e}")
    sys.exit(1)

# Test analysis_viewer page
print("\n[4/4] Testing analysis_viewer page...")
try:
    from pages.analysis_viewer import render_analysis_viewer_page
    print("✅ Analysis viewer page imports successful")
except Exception as e:
    print(f"❌ Analysis viewer page import error: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ All Streamlit page imports successful!")
print("=" * 70)
print("\nReady to run: streamlit run app.py")
