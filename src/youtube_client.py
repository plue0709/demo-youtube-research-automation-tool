"""
YouTube API Client with error handling

CRITICAL: API Quota Management
- videos.list: 1 unit
- captions.list: 50 units
- captions.download: 200 units (expensive!)
- Default quota: 10,000 units/day
"""

from googleapiclient.errors import HttpError
from typing import Optional, List, Dict
import logging
from youtube_utils import parse_iso_duration, srt_to_plain_text

logger = logging.getLogger(__name__)


class YouTubeClient:
    """
    Wrapper for YouTube Data API v3
    Handles metadata fetching, caption listing, and caption downloading
    """

    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.service = auth_manager.get_service()
        self.quota_used = 0

    def get_video_metadata(self, video_id: str) -> Optional[Dict]:
        """
        Fetch video metadata
        Cost: 1 unit

        Returns dict with:
            video_id, title, channel_id, channel_name, published_at,
            duration, language, view_count, like_count, description
        """
        try:
            request = self.service.videos().list(
                part='snippet,contentDetails,statistics',
                id=video_id
            )
            response = request.execute()

            self.quota_used += 1

            if not response.get('items'):
                logger.warning(f"Video not found: {video_id}")
                return None

            item = response['items'][0]
            snippet = item['snippet']
            content_details = item['contentDetails']
            statistics = item.get('statistics', {})

            # Parse ISO 8601 duration to seconds
            duration_seconds = parse_iso_duration(content_details['duration'])

            metadata = {
                'video_id': video_id,
                'title': snippet['title'],
                'channel_id': snippet['channelId'],
                'channel_name': snippet['channelTitle'],
                'published_at': snippet['publishedAt'],
                'duration': duration_seconds,
                'language': snippet.get('defaultAudioLanguage',
                                       snippet.get('defaultLanguage', 'unknown')),
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'description': snippet.get('description', '')[:500]  # Truncate
            }

            logger.info(f"✅ Metadata fetched: {metadata['title']}")
            return metadata

        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            if e.resp.status == 403:
                logger.error("⚠️ QUOTA EXCEEDED or API not enabled")
            return None

    def list_captions(self, video_id: str) -> List[Dict]:
        """
        List available caption tracks
        Cost: 50 units (!!)

        CRITICAL: This is expensive! Only call when necessary.

        Returns list of dicts with:
            id, language, name, is_auto_generated
        """
        try:
            request = self.service.captions().list(
                part='snippet',
                videoId=video_id
            )
            response = request.execute()

            self.quota_used += 50
            logger.info(f"Quota used: {self.quota_used}")

            captions = []
            for item in response.get('items', []):
                snippet = item['snippet']
                captions.append({
                    'id': item['id'],
                    'language': snippet['language'],
                    'name': snippet.get('name', ''),
                    'is_auto_generated': snippet['trackKind'] == 'asr'
                })

            logger.info(f"Found {len(captions)} caption tracks for {video_id}")
            return captions

        except HttpError as e:
            if e.resp.status == 403:
                logger.warning(f"Cannot access captions for {video_id}")
            return []

    def download_caption(self, caption_id: str) -> Optional[str]:
        """
        Download caption content
        Cost: 200 units (!!!)

        CRITICAL: Most expensive operation!

        Returns: Plain text transcript
        """
        try:
            request = self.service.captions().download(
                id=caption_id,
                tfmt='srt'  # or 'vtt', 'sbv'
            )

            # Execute returns raw bytes
            caption_content = request.execute()

            self.quota_used += 200
            logger.info(f"⚠️ Quota used: {self.quota_used} (expensive download)")

            # Decode to text
            text_content = caption_content.decode('utf-8')

            # Convert SRT to plain text (remove timestamps)
            plain_text = srt_to_plain_text(text_content)

            logger.info(f"✅ Caption downloaded: {len(plain_text)} characters")
            return plain_text

        except HttpError as e:
            logger.error(f"Failed to download caption {caption_id}: {e}")
            return None

    def get_best_caption_track(self, video_id: str) -> Optional[Dict]:
        """
        Get the best available caption track for a video

        Priority:
        1. Manual captions in English
        2. Manual captions in any language
        3. Auto-generated in English
        4. Auto-generated in any language

        Returns caption info or None
        """
        captions = self.list_captions(video_id)

        if not captions:
            return None

        # Separate manual and auto-generated
        manual = [c for c in captions if not c['is_auto_generated']]
        auto = [c for c in captions if c['is_auto_generated']]

        # Try manual English first
        for caption in manual:
            if caption['language'].startswith('en'):
                return caption

        # Try any manual
        if manual:
            return manual[0]

        # Try auto English
        for caption in auto:
            if caption['language'].startswith('en'):
                return caption

        # Any auto-generated
        if auto:
            return auto[0]

        return None

    def get_video_captions(self, video_id: str) -> Dict:
        """
        Complete workflow: Get metadata and transcript for a video

        Returns dict with:
            success, metadata, transcript, language, word_count, error
        """
        result = {
            'success': False,
            'metadata': None,
            'transcript': None,
            'language': None,
            'is_auto_generated': None,
            'word_count': 0,
            'error': None
        }

        # Step 1: Get metadata
        metadata = self.get_video_metadata(video_id)
        if not metadata:
            result['error'] = "Video not found or inaccessible"
            return result

        result['metadata'] = metadata

        # Step 2: Get best caption track
        caption_track = self.get_best_caption_track(video_id)
        if not caption_track:
            result['error'] = "No captions available"
            return result

        result['language'] = caption_track['language']
        result['is_auto_generated'] = caption_track['is_auto_generated']

        # Step 3: Download caption
        transcript = self.download_caption(caption_track['id'])
        if not transcript:
            result['error'] = "Failed to download caption"
            return result

        result['transcript'] = transcript
        result['word_count'] = len(transcript.split())
        result['success'] = True

        logger.info(f"✅ Complete! Words: {result['word_count']}, Quota: {self.quota_used}")
        return result


if __name__ == "__main__":
    # Test the client
    import os
    import sys
    sys.path.insert(0, os.path.dirname(__file__))

    from youtube_auth import YouTubeAuthManager

    logging.basicConfig(level=logging.INFO)

    print("Testing YouTube Client...")
    print("=" * 60)

    # Initialize
    auth = YouTubeAuthManager()
    client = YouTubeClient(auth)

    # Test with a known video (replace with any public video with captions)
    test_video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up

    print(f"\nTesting with video: {test_video_id}")
    print("-" * 60)

    result = client.get_video_captions(test_video_id)

    if result['success']:
        print(f"\n✅ SUCCESS!")
        print(f"Title: {result['metadata']['title']}")
        print(f"Channel: {result['metadata']['channel_name']}")
        print(f"Language: {result['language']}")
        print(f"Auto-generated: {result['is_auto_generated']}")
        print(f"Word count: {result['word_count']}")
        print(f"\nTranscript preview (first 200 chars):")
        print(result['transcript'][:200] + "...")
    else:
        print(f"\n❌ FAILED: {result['error']}")

    print(f"\nTotal quota used: {client.quota_used} units")
