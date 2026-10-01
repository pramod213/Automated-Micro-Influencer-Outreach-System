"""Influencer model."""

import enum
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Enum, UniqueConstraint, Index, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin


class Platform(enum.Enum):
    """Social media platform enumeration."""

    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"


class Influencer(Base, TimestampMixin):
    """Influencer model representing a discovered micro-influencer."""

    __tablename__ = "influencers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    platform: Mapped[Platform] = mapped_column(Enum(Platform), nullable=False)
    profile_url: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    handle: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    follower_count: Mapped[int] = mapped_column(Integer, nullable=False)
    engagement_rate: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    content_themes: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False, default="Not Found")
    instagram_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    youtube_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    tiktok_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    audience_age: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    audience_gender: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    audience_geography: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="influencer",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    outreach_logs: Mapped[List["OutreachLog"]] = relationship(
        "OutreachLog",
        back_populates="influencer",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Table constraints and indexes
    __table_args__ = (
        UniqueConstraint("platform", "profile_url", name="uq_influencer_platform_profile"),
        Index("ix_influencer_platform", "platform"),
        Index("ix_influencer_category", "category"),
        Index("ix_influencer_follower_count", "follower_count"),
        Index("ix_influencer_contact_email", "contact_email"),
        Index("ix_influencer_source", "source"),
        Index("ix_influencer_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Influencer(id={self.id}, name='{self.name}', platform={self.platform.value})>"