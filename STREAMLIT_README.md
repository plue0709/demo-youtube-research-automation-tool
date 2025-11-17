# Streamlit UI - User Guide

## Running the App Locally

### 1. Prerequisites
Make sure you have completed the setup:
- Virtual environment activated
- Dependencies installed (`pip install -r requirements.txt`)
- OAuth2 credentials configured
- OpenAI API key in `.env`

### 2. Populate Demo Data (Optional)
If you want to see the UI with sample data:
```bash
python populate_demo_data.py
```

This will create 3 demo videos with AI analysis.

### 3. Start Streamlit App
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Features

### 🏠 Dashboard
- Overview statistics
- System information
- Feature highlights

### ➕ Add Videos
- **Single URL Upload**: Process one video at a time
- **Batch Upload**: Process multiple videos (paste URLs, one per line)
- Complete pipeline: Metadata → Captions → AI Analysis → Database

### 📊 Video Library
- View all videos in a table
- Filter by status and captions
- Sort by date, views, or title
- Video details with quick analysis preview
- Export to CSV/JSON
- Delete videos

### 🔬 Analysis Viewer
- Detailed AI motif coding results
- 5 tabs:
  - **Overview**: Topic, quality, credibility, main claims
  - **Training & Performance**: Training types, recovery methods, equipment
  - **Nutrition**: Diet, supplements, macros, meal timing
  - **Research & Credibility**: Studies cited, expert credentials
  - **Transcript**: Full transcript with search functionality
- Export analysis to JSON
- Download transcript

## Tips

### For Testing
Use the demo data script to populate the database with sample videos:
```bash
python populate_demo_data.py
```

### Clearing Database
If you want to start fresh:
```bash
rm data/youtube_research.db
python populate_demo_data.py
```

### Adding Real Videos
1. Make sure OAuth2 is set up correctly
2. Use the "➕ Add Videos" page
3. Paste YouTube URL
4. Wait for processing (metadata → captions → AI analysis)

**Note**: Caption fetching may fail due to IP blocks. This is expected in the demo. See main README for production solution (residential proxies).

### Keyboard Shortcuts
- `R`: Refresh the page
- `Ctrl+K`: Focus on search (in transcript viewer)

## Known Limitations

### YouTube Caption API
- Official API only works for videos you own
- Unofficial API blocked from cloud IPs
- **Solution for production**: Residential proxies (Webshare, ~$3.50 per 1,000 videos)

### Demo Data
- Sample transcript is reused for multiple videos
- Some metadata is synthetic
- Real videos may have "no_captions" status if blocked

## Troubleshooting

### Import Errors
Test all imports work:
```bash
python test_streamlit_imports.py
```

### Database Errors
Reinitialize the database:
```bash
rm data/youtube_research.db
python -c "from database import init_database; init_database()"
```

### OAuth Errors
Make sure credentials are set up:
```bash
python quick_oauth.py
```

### Port Already in Use
If port 8501 is in use:
```bash
streamlit run app.py --server.port 8502
```

## Performance Notes

- **Database**: SQLite is sufficient for demo (1,000s of videos)
- **AI Analysis**: ~$0.0006 per video (gpt-4o-mini)
- **YouTube API**: Free tier (10,000 units/day = ~40 videos/day max)
- **Memory**: Minimal (<200MB for typical usage)

## Deployment

See main README for Streamlit Cloud deployment instructions (Phase 5).

---

**Demo by Duy N.**
Portfolio project for Upwork job application
