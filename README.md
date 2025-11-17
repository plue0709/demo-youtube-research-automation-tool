# YouTube Research Automation Tool

Automated tool for analyzing sports, fitness, and nutrition content from YouTube videos using AI-powered motif coding.

## Features

- **Automated Video Processing**: Extract metadata and captions from YouTube videos
- **AI Content Analysis**: OpenAI-powered motif coding for sports/fitness content
- **Web Interface**: Clean Streamlit dashboard for managing and viewing results
- **Data Export**: Export analysis results to CSV/JSON formats
- **Batch Processing**: Process multiple videos simultaneously

## Tech Stack

- **Frontend**: Streamlit
- **APIs**: YouTube Data API v3, OpenAI GPT-4o-mini
- **Database**: SQLite (easily upgradable to PostgreSQL)
- **Caption Extraction**: youtube-transcript-api
- **Authentication**: Google OAuth2

## Quick Start

### Prerequisites

- Python 3.12+
- Google Cloud Project with YouTube Data API v3 enabled
- OpenAI API key
- OAuth2 credentials from Google Cloud Console

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd youtube-research-demo

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Create `.env` file:
```bash
OPENAI_API_KEY=your_openai_api_key
DATABASE_PATH=data/youtube_research.db
YOUTUBE_CREDENTIALS_PATH=config/credentials.json
YOUTUBE_TOKEN_PATH=config/token.pickle
```

2. Place your Google OAuth2 credentials in `config/credentials.json`

3. Run OAuth2 setup:
```bash
python quick_oauth.py
```

### Running the Application

```bash
# Populate demo data (optional)
python populate_demo_data.py

# Start the web interface
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

## Project Structure

```
youtube-research-demo/
├── app.py                   # Main Streamlit application
├── pages/                   # Streamlit pages
│   ├── add_videos.py       # Video upload interface
│   ├── video_library.py    # Browse and manage videos
│   └── analysis_viewer.py  # Detailed AI analysis results
├── src/                     # Core backend modules
│   ├── youtube_auth.py     # OAuth2 authentication
│   ├── youtube_client.py   # YouTube API wrapper
│   ├── youtube_utils.py    # Utility functions
│   ├── models.py           # Database models
│   ├── database.py         # Database operations
│   ├── motif_schema.py     # Pydantic schemas
│   └── ai_coder.py         # OpenAI integration
├── config/                  # OAuth2 credentials
├── data/                    # SQLite database
└── requirements.txt         # Python dependencies
```

## Usage

### Adding Videos

1. Navigate to "Add Videos" page
2. Enter YouTube URL(s)
3. Click "Process Video" to run the full pipeline:
   - Extract video metadata
   - Download captions
   - Run AI analysis
   - Save to database

### Viewing Results

- **Video Library**: Browse all processed videos with filters
- **Analysis Viewer**: See detailed AI motif coding results in 5 categories:
  - Overview (topic, quality, main claims)
  - Training & Performance
  - Nutrition
  - Research & Credibility
  - Transcript

### Exporting Data

Export analysis results to CSV or JSON from the Video Library page.

## AI Motif Coding

The tool analyzes video transcripts for:

- **Training Methods**: Types, equipment, recovery protocols
- **Nutrition Content**: Supplements, diet types, meal timing
- **Scientific Credibility**: Research citations, expert credentials
- **Performance Metrics**: VO2 max, progressive overload, periodization
- **Key Insights**: Main claims, quotes, context

## API Costs

- **YouTube API**: Free (10,000 quota units/day)
- **OpenAI API**: ~$0.0006 per video (GPT-4o-mini)
- **Total**: <$1 per 1,000 videos

## Known Limitations

### YouTube Caption Access

YouTube's official caption API only works for videos you own. This tool uses `youtube-transcript-api` (unofficial) which may be blocked from certain IPs. Solutions:

- Deploy to cloud platforms (different IP range)
- Use residential proxies for production scale
- Implement rate limiting and delays

## Development

### Running Tests

```bash
# Test OAuth2 authentication
python test_phase1.py

# Test database operations
python test_phase2.py

# Test OpenAI integration
python test_phase3.py

# Test Streamlit imports
python test_streamlit_imports.py
```

### Database Schema

- **videos**: Video metadata from YouTube
- **transcripts**: Caption text and metadata
- **motif_codings**: AI analysis results (JSON)

## Deployment

The application can be deployed to:

- Streamlit Cloud (recommended for demos)
- Heroku / AWS / GCP
- Docker container

See deployment guide for detailed instructions.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Contact

For questions or issues, please open an issue on GitHub.

---

**Built with**: Streamlit, OpenAI, YouTube Data API v3
