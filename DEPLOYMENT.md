# Deployment Guide - Streamlit Cloud

Step-by-step guide for deploying the YouTube Research Automation Tool to Streamlit Cloud.

## Prerequisites

- GitHub account
- Streamlit Cloud account (free at share.streamlit.io)
- OpenAI API key
- Code cleaned and ready (no sensitive data in repo)

## Step 1: Prepare Repository

### 1.1 Create GitHub Repository

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: YouTube Research Automation Tool"

# Create repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### 1.2 Verify .gitignore

Make sure these are in `.gitignore`:
- `config/credentials.json` (OAuth2 credentials)
- `config/token.pickle` (OAuth2 token)
- `.env` (environment variables)
- `data/*.db` (database files)

### 1.3 Check Repository

Visit your GitHub repo and verify:
- ✅ No OAuth2 credentials visible
- ✅ No .env file visible
- ✅ No API keys in code
- ✅ README.md looks professional
- ✅ All Python files present

## Step 2: Configure Streamlit Secrets

### 2.1 Create secrets.toml Template

Streamlit Cloud uses secrets instead of .env files. Create `.streamlit/secrets.toml`:

```toml
# OpenAI API Configuration
OPENAI_API_KEY = "your_openai_api_key_here"

# Database Configuration
DATABASE_PATH = "data/youtube_research.db"

# YouTube API Configuration
# Note: OAuth2 won't work on Streamlit Cloud (requires browser)
# Use API key mode or pre-populated database for demo
YOUTUBE_API_KEY = "your_youtube_api_key_here"
YOUTUBE_CREDENTIALS_PATH = "config/credentials.json"
YOUTUBE_TOKEN_PATH = "config/token.pickle"
```

**IMPORTANT**: Do NOT commit `secrets.toml` to git! It's in `.gitignore`.

### 2.2 Get Your API Keys

**OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Create new key
3. Copy the key

**YouTube API Key** (optional for cloud):
1. Go to Google Cloud Console
2. APIs & Services → Credentials
3. Create API Key
4. Copy the key

## Step 3: Deploy to Streamlit Cloud

### 3.1 Sign Up / Login

1. Go to https://share.streamlit.io/
2. Sign in with GitHub account
3. Authorize Streamlit to access your repositories

### 3.2 Create New App

1. Click "New app" button
2. Select your repository
3. Configure deployment:
   - **Repository**: `YOUR_USERNAME/YOUR_REPO_NAME`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: Choose a custom URL (e.g., `youtube-research-tool`)

### 3.3 Configure Secrets

1. Click "Advanced settings"
2. Paste your secrets in TOML format:

```toml
OPENAI_API_KEY = "sk-proj-your-key-here"
DATABASE_PATH = "data/youtube_research.db"
```

### 3.4 Deploy

1. Click "Deploy!"
2. Wait for deployment (2-5 minutes)
3. Watch the logs for any errors

### 3.5 Verify Deployment

Once deployed, your app will be at:
```
https://YOUR_APP_NAME.streamlit.app
```

Test:
- ✅ Dashboard loads
- ✅ Database stats show demo data
- ✅ Video Library displays videos
- ✅ Analysis Viewer shows AI results
- ✅ No errors in console

## Step 4: OAuth2 Limitation Workaround

**Problem**: OAuth2 requires browser interaction, which doesn't work on cloud deployments.

**Solutions**:

### Option A: Use Pre-Populated Database (Recommended for Demo)

1. Populate database locally with demo data:
```bash
python populate_demo_data.py
```

2. Commit the populated database:
```bash
git add data/youtube_research.db
git commit -m "Add demo data for deployment"
git push
```

3. Streamlit Cloud will use the committed database.

### Option B: Disable Add Videos Feature

Comment out the "Add Videos" page in `app.py`:

```python
# Temporarily disable for cloud deployment
page_options = ["🏠 Dashboard", "📊 Video Library", "🔬 Analysis Viewer"]
# Removed: "➕ Add Videos"
```

### Option C: Use API Key Mode (Advanced)

Modify `youtube_client.py` to support API key mode without OAuth2:

```python
def __init__(self, auth_manager=None, api_key=None):
    if api_key:
        # API key mode (limited features)
        self.service = build('youtube', 'v3', developerKey=api_key)
    else:
        # OAuth2 mode (full features)
        self.auth_manager = auth_manager
        self.service = auth_manager.get_service()
```

## Step 5: Update App for Production

### 5.1 Add Deployment Note

Add a banner to `app.py`:

```python
# In dashboard section
st.info("""
📢 **Demo Mode**: This deployment uses pre-populated data.
OAuth2 video upload requires local deployment.
[View on GitHub](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME)
""")
```

### 5.2 Optimize for Cloud

```python
# Add @st.cache_data for expensive operations
@st.cache_data(ttl=3600)
def get_all_videos_cached():
    return get_all_videos()
```

### 5.3 Handle Missing Config

```python
# Gracefully handle missing OAuth2 credentials
try:
    auth_manager = YouTubeAuthManager()
    youtube_client = YouTubeClient(auth_manager)
except FileNotFoundError:
    st.warning("OAuth2 not configured. Using demo mode.")
    youtube_client = None
```

## Step 6: Monitor and Maintain

### 6.1 View Logs

In Streamlit Cloud dashboard:
- Click your app
- View logs in real-time
- Check for errors

### 6.2 Update App

To update the deployed app:
```bash
git add .
git commit -m "Update: description of changes"
git push
```

Streamlit Cloud will automatically redeploy.

### 6.3 Manage Secrets

To update secrets:
1. Go to Streamlit Cloud dashboard
2. Click app → Settings → Secrets
3. Edit and save
4. App will restart automatically

## Step 7: Custom Domain (Optional)

### 7.1 Free Subdomain

Streamlit provides:
```
https://your-app-name.streamlit.app
```

### 7.2 Custom Domain (Paid Plans)

For custom domains like `research.yourdomain.com`:
1. Upgrade to Streamlit Cloud paid plan
2. Add CNAME record in DNS
3. Configure in Streamlit settings

## Troubleshooting

### "Module not found" Error

**Problem**: Missing dependency in requirements.txt

**Solution**:
1. Check local venv: `pip freeze > requirements.txt`
2. Commit and push
3. Redeploy

### "File not found" Error

**Problem**: File paths are wrong for cloud deployment

**Solution**:
- Use relative paths: `./data/file.db` not `/home/user/data/file.db`
- Check file is committed to git
- Verify path in code

### OAuth2 Errors

**Problem**: Can't authenticate on cloud

**Solution**:
- Use pre-populated database (Option A above)
- Or disable Add Videos feature
- Or implement API key mode

### Database Not Persisting

**Problem**: Data resets on each deployment

**Solution**:
- Commit database to git (for demo data)
- Use external database (PostgreSQL on Heroku/Supabase) for production
- Streamlit Cloud has no persistent storage

### Out of Memory

**Problem**: App crashes with memory error

**Solution**:
- Reduce demo data size
- Add caching: `@st.cache_data`
- Optimize database queries
- Upgrade to larger Streamlit Cloud instance

## Cost Considerations

### Streamlit Cloud Free Tier

- **Deployment**: Free
- **Apps**: 1 public app
- **Resources**: Limited (512MB RAM, 1 CPU core)
- **Bandwidth**: Unlimited
- **Uptime**: Best effort

### Paid Plans

- **Starter**: $20/month (more resources, private apps)
- **Team**: $250/month (team features, more apps)
- **Enterprise**: Custom pricing

### API Costs (from your account)

- **OpenAI**: ~$0.60 per 1,000 videos
- **YouTube**: Free (quota-based)

## Security Best Practices

### ✅ DO:
- Store secrets in Streamlit secrets
- Use .gitignore for sensitive files
- Implement rate limiting
- Validate user inputs
- Use HTTPS (provided by Streamlit)

### ❌ DON'T:
- Commit API keys to git
- Hardcode credentials in code
- Expose internal file paths
- Allow unlimited API calls
- Store sensitive data in public repo

## Production Checklist

Before going live:

- [ ] README.md is professional
- [ ] No AI/development signatures
- [ ] .gitignore excludes sensitive files
- [ ] Secrets configured in Streamlit Cloud
- [ ] Demo data populated
- [ ] OAuth2 limitation handled
- [ ] Error handling implemented
- [ ] App tested on staging URL
- [ ] Logs checked for errors
- [ ] Custom URL configured (optional)
- [ ] Analytics added (optional)

## Alternative Deployment Options

If Streamlit Cloud doesn't meet your needs:

### Heroku
```bash
# Create Procfile
echo "web: streamlit run app.py --server.port $PORT" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

### AWS / GCP / Azure
- Use Docker container
- Deploy to container service (ECS, Cloud Run, etc.)
- Configure environment variables
- Set up domain and SSL

### Self-Hosted
```bash
# Install Streamlit on server
pip install streamlit

# Run with nohup
nohup streamlit run app.py --server.port 8501 &

# Use nginx as reverse proxy
# Configure domain and SSL (Let's Encrypt)
```

## Support

- **Streamlit Docs**: https://docs.streamlit.io
- **Streamlit Forums**: https://discuss.streamlit.io
- **GitHub Issues**: Create issues in your repo

---

**Ready to deploy?** Follow steps 1-3 to get your app live in under 10 minutes!
