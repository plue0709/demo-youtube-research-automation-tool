"""
YouTube utility functions
"""

import re
from urllib.parse import urlparse, parse_qs
from typing import Optional


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from various URL formats

    Supported formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID
    - VIDEO_ID (raw ID)

    Returns:
        Video ID if valid, None otherwise
    """
    if not url:
        return None

    url = url.strip()

    # If it's already a video ID (11 characters, alphanumeric + - and _)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url

    # Parse URL
    try:
        parsed = urlparse(url)

        # youtube.com/watch?v=...
        if 'youtube.com' in parsed.netloc:
            if parsed.path == '/watch':
                query_params = parse_qs(parsed.query)
                return query_params.get('v', [None])[0]

            # youtube.com/embed/... or /v/...
            match = re.search(r'/(embed|v)/([a-zA-Z0-9_-]{11})', parsed.path)
            if match:
                return match.group(2)

        # youtu.be/...
        if 'youtu.be' in parsed.netloc:
            video_id = parsed.path.lstrip('/')
            # Remove any query params
            video_id = video_id.split('?')[0]
            if re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                return video_id

    except Exception:
        pass

    return None


def validate_url(url: str) -> bool:
    """Check if URL is valid YouTube URL"""
    return extract_video_id(url) is not None


def parse_iso_duration(iso_duration: str) -> int:
    """
    Parse ISO 8601 duration to seconds
    Example: PT1H2M10S -> 3730 seconds
    """
    pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
    match = pattern.match(iso_duration)

    if not match:
        return 0

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)

    return hours * 3600 + minutes * 60 + seconds


def srt_to_plain_text(srt_content: str) -> str:
    """
    Convert SRT subtitle format to plain text
    Remove timestamps and sequence numbers
    """
    # Remove sequence numbers
    text = re.sub(r'^\d+\n', '', srt_content, flags=re.MULTILINE)

    # Remove timestamps (00:00:00,000 --> 00:00:00,000)
    text = re.sub(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', text)

    # Remove extra blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def get_video_captions(video_id: str, cookies_txt: Optional[str] = None) -> dict:
    """
    Get video captions using youtube-transcript-api (unofficial but works!)

    This is a hybrid approach:
    - Uses unofficial API (works for public videos with captions)
    - No OAuth2 needed for captions
    - Fallback for when official API fails

    Args:
        video_id: YouTube video ID
        cookies_txt: Optional path to cookies.txt file for age-restricted videos

    Returns:
        dict with: success, transcript, language, is_auto_generated, word_count, error
    """
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable
    )

    result = {
        'success': False,
        'transcript': None,
        'language': None,
        'is_auto_generated': None,
        'word_count': 0,
        'error': None
    }

    try:
        # Try to get transcript list
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try to get manual transcripts first (better quality)
        try:
            transcript_data = transcript_list.find_manually_created_transcript(['en'])
            result['is_auto_generated'] = False
        except:
            # Fall back to auto-generated
            try:
                transcript_data = transcript_list.find_generated_transcript(['en'])
                result['is_auto_generated'] = True
            except:
                # Try any available language
                available = list(transcript_list)
                if available:
                    transcript_data = available[0]
                    result['is_auto_generated'] = transcript_data.is_generated
                else:
                    result['error'] = "No transcripts available"
                    return result

        # Fetch the actual transcript
        transcript_entries = transcript_data.fetch()

        # Convert to plain text
        text_parts = [entry['text'] for entry in transcript_entries]
        full_transcript = ' '.join(text_parts)

        # Clean up extra whitespace
        full_transcript = re.sub(r'\s+', ' ', full_transcript).strip()

        result['success'] = True
        result['transcript'] = full_transcript
        result['language'] = transcript_data.language_code
        result['word_count'] = len(full_transcript.split())

    except TranscriptsDisabled:
        result['error'] = "Transcripts are disabled for this video"
    except NoTranscriptFound:
        result['error'] = "No transcript found in any language"
    except VideoUnavailable:
        result['error'] = "Video is unavailable"
    except Exception as e:
        result['error'] = f"Unexpected error: {str(e)}"

    return result


if __name__ == "__main__":
    # Test video ID extraction
    test_urls = [
        'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'https://youtu.be/dQw4w9WgXcQ',
        'dQw4w9WgXcQ',
        'https://www.youtube.com/embed/dQw4w9WgXcQ',
        'https://invalid.com/video'
    ]

    print("Testing video ID extraction:")
    for url in test_urls:
        video_id = extract_video_id(url)
        status = "✅" if video_id else "❌"
        print(f"{status} {url} → {video_id}")
