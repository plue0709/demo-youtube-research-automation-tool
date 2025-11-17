"""
Database connection and helper functions
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Optional, List
import logging
from dotenv import load_dotenv

from models import Base, Video, Transcript, MotifCoding

load_dotenv()
logger = logging.getLogger(__name__)

# Database setup
DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/youtube_research.db')
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'

# Create engine
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_database():
    """Create all tables in the database"""
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)

    # Create all tables
    Base.metadata.create_all(engine)
    logger.info(f"✅ Database initialized at {DATABASE_PATH}")
    logger.info(f"   Tables: {list(Base.metadata.tables.keys())}")


@contextmanager
def get_db():
    """
    Context manager for database sessions

    Usage:
        with get_db() as db:
            video = db.query(Video).first()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        session.close()


# ============================================================================
# VIDEO OPERATIONS
# ============================================================================

def create_video(video_data: dict) -> Video:
    """Create a new video record"""
    with get_db() as db:
        video = Video(**video_data)
        db.add(video)
        db.commit()
        db.refresh(video)
        # Eagerly load attributes before session closes
        _ = (video.id, video.video_id, video.title)
        db.expunge(video)  # Detach from session
        logger.info(f"✅ Created video: {video.video_id}")
        return video


def get_video_by_id(video_id: str) -> Optional[Video]:
    """Get video by YouTube video_id"""
    with get_db() as db:
        video = db.query(Video).filter_by(video_id=video_id).first()
        if video:
            db.expunge(video)
        return video


def get_video_by_pk(pk: int) -> Optional[Video]:
    """Get video by primary key"""
    with get_db() as db:
        return db.query(Video).get(pk)


def update_video(video_id: str, updates: dict) -> Optional[Video]:
    """Update video record"""
    with get_db() as db:
        video = db.query(Video).filter_by(video_id=video_id).first()
        if video:
            for key, value in updates.items():
                setattr(video, key, value)
            db.commit()
            db.refresh(video)
            logger.info(f"✅ Updated video: {video_id}")
            return video
        return None


def get_all_videos(status: Optional[str] = None, has_captions: Optional[bool] = None) -> List[Video]:
    """Get all videos, optionally filtered"""
    with get_db() as db:
        query = db.query(Video)

        if status:
            query = query.filter_by(status=status)

        if has_captions is not None:
            query = query.filter_by(has_captions=has_captions)

        videos = query.order_by(Video.created_at.desc()).all()
        for video in videos:
            db.expunge(video)
        return videos


def delete_video(video_id: str) -> bool:
    """Delete video and related records (cascades to transcripts and motif_codings)"""
    with get_db() as db:
        video = db.query(Video).filter_by(video_id=video_id).first()
        if video:
            db.delete(video)
            db.commit()
            logger.info(f"✅ Deleted video: {video_id}")
            return True
        return False


# ============================================================================
# TRANSCRIPT OPERATIONS
# ============================================================================

def create_transcript(video_pk: int, transcript_data: dict) -> Transcript:
    """Create transcript for a video"""
    with get_db() as db:
        transcript = Transcript(video_id=video_pk, **transcript_data)
        db.add(transcript)

        # Update video status
        video = db.query(Video).get(video_pk)
        if video:
            video.has_captions = True
            video.status = 'completed'

        db.commit()
        db.refresh(transcript)
        # Eagerly load attributes
        _ = (transcript.id, transcript.language, transcript.word_count)
        db.expunge(transcript)
        logger.info(f"✅ Created transcript for video_id={video_pk}")
        return transcript


def get_transcript(video_pk: int) -> Optional[Transcript]:
    """Get transcript for a video"""
    with get_db() as db:
        transcript = db.query(Transcript).filter_by(video_id=video_pk).first()
        if transcript:
            db.expunge(transcript)
        return transcript


# ============================================================================
# MOTIF CODING OPERATIONS
# ============================================================================

def create_motif_coding(video_pk: int, transcript_pk: int, coding_data: dict) -> MotifCoding:
    """Create AI motif coding result"""
    with get_db() as db:
        motif = MotifCoding(
            video_id=video_pk,
            transcript_id=transcript_pk,
            **coding_data
        )
        db.add(motif)
        db.commit()
        db.refresh(motif)
        # Eagerly load attributes
        _ = (motif.id, motif.model_used, motif.tokens_used, motif.coding_results)
        db.expunge(motif)
        logger.info(f"✅ Created motif coding for video_id={video_pk}")
        return motif


def get_motif_coding(video_pk: int) -> Optional[MotifCoding]:
    """Get motif coding for a video"""
    with get_db() as db:
        motif = db.query(MotifCoding).filter_by(video_id=video_pk).first()
        if motif:
            db.expunge(motif)
        return motif


# ============================================================================
# STATISTICS
# ============================================================================

def get_database_stats() -> dict:
    """Get database statistics"""
    with get_db() as db:
        total_videos = db.query(Video).count()
        completed = db.query(Video).filter_by(status='completed').count()
        processing = db.query(Video).filter_by(status='processing').count()
        failed = db.query(Video).filter_by(status='failed').count()
        with_captions = db.query(Video).filter_by(has_captions=True).count()
        with_ai_coding = db.query(MotifCoding).count()

        return {
            'total_videos': total_videos,
            'completed': completed,
            'processing': processing,
            'failed': failed,
            'with_captions': with_captions,
            'with_ai_coding': with_ai_coding,
        }


if __name__ == "__main__":
    # Test database setup
    logging.basicConfig(level=logging.INFO)

    print("=" * 70)
    print("Initializing Database")
    print("=" * 70)

    init_database()

    print("\n" + "=" * 70)
    print("Database Statistics")
    print("=" * 70)

    stats = get_database_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n✅ Database setup complete!")
