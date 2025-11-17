"""
YouTube OAuth2 Authentication Manager

CRITICAL: YouTube captions.download endpoint REQUIRES OAuth2
API key alone will NOT work!
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import logging

logger = logging.getLogger(__name__)

# CRITICAL: Scopes determine what API can access
# youtube.force-ssl allows read/write access to captions
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']


class YouTubeAuthManager:
    """
    Manages YouTube API OAuth2 authentication

    CRITICAL NOTES:
    - OAuth2 is REQUIRED for captions.download endpoint
    - API key alone will NOT work
    - Token must be refreshed when expired
    - credentials.json from GCP Console required
    """

    def __init__(self, credentials_path='config/credentials.json',
                 token_path='config/token.pickle'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.credentials = None
        self.service = None

    def authenticate(self):
        """
        Main authentication flow

        Flow:
        1. Check if token.pickle exists and is valid
        2. If expired, refresh it
        3. If no token, run OAuth2 consent flow
        4. Save token for future use

        Returns:
            YouTube API service object
        """
        # Load existing credentials if available
        if os.path.exists(self.token_path):
            logger.info(f"Loading existing token from {self.token_path}")
            with open(self.token_path, 'rb') as token:
                self.credentials = pickle.load(token)

        # Check if credentials are valid
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                # Refresh expired token
                try:
                    logger.info("Refreshing expired token...")
                    self.credentials.refresh(Request())
                    logger.info("✅ Token refreshed successfully")
                except Exception as e:
                    logger.error(f"❌ Token refresh failed: {e}")
                    # Force re-authentication
                    self.credentials = None

            # If still no valid credentials, run OAuth flow
            if not self.credentials:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"credentials.json not found at {self.credentials_path}\n"
                        "Download from GCP Console: APIs & Services > Credentials"
                    )

                logger.info("Starting OAuth2 consent flow...")
                # Run local OAuth2 consent flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path,
                    SCOPES
                )

                # This will open browser for user consent
                self.credentials = flow.run_local_server(
                    port=8080,
                    authorization_prompt_message='Please visit this URL: {url}',
                    success_message='✅ Authentication successful! You may close this window.',
                    open_browser=True
                )

                logger.info("✅ New credentials obtained")

            # Save credentials for next time
            with open(self.token_path, 'wb') as token:
                pickle.dump(self.credentials, token)
                logger.info(f"✅ Credentials saved to {self.token_path}")

        # Build YouTube service
        self.service = build('youtube', 'v3', credentials=self.credentials)
        logger.info("✅ YouTube service ready!")
        return self.service

    def get_service(self):
        """Get authenticated YouTube service object"""
        if not self.service:
            return self.authenticate()
        return self.service


if __name__ == "__main__":
    # Test authentication
    logging.basicConfig(level=logging.INFO)

    print("Testing YouTube OAuth2 Authentication...")
    print("=" * 60)

    auth_manager = YouTubeAuthManager()
    youtube = auth_manager.get_service()

    print("✅ YouTube service ready!")
    print("\nYou can now use this service to access YouTube API")
