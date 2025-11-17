"""
Database models for YouTube Research Tool

Tables:
- videos: Video metadata from YouTube Data API v3
- transcripts: Caption text from youtube-transcript-api
- motif_codings: AI analysis results from OpenAI
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Video(Base):
    """
    Stores video metadata from YouTube Data API v3

    Source: videos.list endpoint (1 quota unit per call)
    """
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True)
    video_id = Column(String(20), unique=True, nullable=False, index=True)
    url = Column(Text, nullable=False)

    # Metadata from YouTube Data API v3
    title = Column(Text)
    channel_name = Column(Text)
    channel_id = Column(String(30))
    description = Column(Text)
    published_at = Column(DateTime)
    duration = Column(Integer)  # seconds
    language = Column(String(10))

    # Statistics
    view_count = Column(Integer)
    like_count = Column(Integer)
    comment_count = Column(Integer)

    # Status tracking
    status = Column(String(20), default='pending', index=True)
    # Status values: pending, processing, completed, failed, no_captions

    has_captions = Column(Boolean, default=False, index=True)
    error_message = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transcripts = relationship('Transcript', back_populates='video', cascade='all, delete-orphan')
    motif_codings = relationship('MotifCoding', back_populates='video', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Video(video_id='{self.video_id}', title='{self.title[:50]}...')>"

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'video_id': self.video_id,
            'url': self.url,
            'title': self.title,
            'channel_name': self.channel_name,
            'duration': self.duration,
            'view_count': self.view_count,
            'status': self.status,
            'has_captions': self.has_captions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Transcript(Base):
    """
    Stores transcript text from youtube-transcript-api

    Source: youtube-transcript-api (unofficial, requires proxy)
    """
    __tablename__ = 'transcripts'

    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey('videos.id'), nullable=False)

    # Transcript data
    language = Column(String(10))
    is_auto_generated = Column(Boolean)
    raw_text = Column(Text)  # Full transcript text
    word_count = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    video = relationship('Video', back_populates='transcripts')
    motif_codings = relationship('MotifCoding', back_populates='transcript')

    def __repr__(self):
        return f"<Transcript(video_id={self.video_id}, language='{self.language}', words={self.word_count})>"

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'video_id': self.video_id,
            'language': self.language,
            'is_auto_generated': self.is_auto_generated,
            'word_count': self.word_count,
            'transcript_preview': self.raw_text[:200] if self.raw_text else None,
        }


class MotifCoding(Base):
    """
    Stores AI analysis results from OpenAI

    Source: OpenAI API (gpt-4o-mini with structured outputs)
    """
    __tablename__ = 'motif_codings'

    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey('videos.id'), nullable=False)
    transcript_id = Column(Integer, ForeignKey('transcripts.id'))

    # AI analysis results (structured JSON from OpenAI)
    coding_results = Column(JSON)
    # Example structure:
    # {
    #   "recovery_methods": ["ice bath", "massage"],
    #   "nutrition_focus": true,
    #   "supplements_mentioned": ["protein", "creatine"],
    #   "cites_research": true,
    #   "primary_topic": "training",
    #   "content_quality": "high",
    #   "key_quotes": [{"text": "...", "context": "..."}]
    # }

    # Metadata
    model_used = Column(String(50))  # e.g., "gpt-4o-mini"
    tokens_used = Column(Integer)
    processing_time = Column(Integer)  # seconds

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    video = relationship('Video', back_populates='motif_codings')
    transcript = relationship('Transcript', back_populates='motif_codings')

    def __repr__(self):
        return f"<MotifCoding(video_id={self.video_id}, model='{self.model_used}')>"

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'video_id': self.video_id,
            'coding_results': self.coding_results,
            'model_used': self.model_used,
            'tokens_used': self.tokens_used,
        }


if __name__ == "__main__":
    print("Database models defined successfully!")
    print(f"Tables: {Base.metadata.tables.keys()}")
