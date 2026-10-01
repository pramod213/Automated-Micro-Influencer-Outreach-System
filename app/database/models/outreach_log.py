"""OutreachLog model."""

import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, Enum, Index, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin


class OutreachChannel(enum.Enum):
    """Outreach channel enumeration."""

    EMAIL = "email"
    INSTAGRAM = "instagram"


class OutreachStatus(enum.Enum):
    """Outreach status enumeration."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    SIMULATED = "simulated"
    SKIPPED = "skipped"


class OutreachLog(Base, TimestampMixin):
    """OutreachLog model tracking outreach attempts."""

    __tablename__ = "outreach_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    influencer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("influencers.id", ondelete="CASCADE"), nullable=False
    )
    message_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False
    )
    channel: Mapped[OutreachChannel] = mapped_column(Enum(OutreachChannel), nullable=False)
    status: Mapped[OutreachStatus] = mapped_column(Enum(OutreachStatus), default=OutreachStatus.PENDING, nullable=False)
    provider: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    message_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    # Relationships
    influencer: Mapped["Influencer"] = relationship("Influencer", back_populates="outreach_logs")
    message: Mapped["Message"] = relationship("Message", back_populates="outreach_logs")

    # Table constraints and indexes
    __table_args__ = (
        UniqueConstraint("influencer_id", "channel", "message_hash", name="uq_outreach_influencer_channel_hash"),
        Index("ix_outreach_influencer_id", "influencer_id"),
        Index("ix_outreach_message_id", "message_id"),
        Index("ix_outreach_channel", "channel"),
        Index("ix_outreach_status", "status"),
        Index("ix_outreach_sent_at", "sent_at"),
        Index("ix_outreach_message_hash", "message_hash"),
    )

    def __repr__(self) -> str:
        return f"<OutreachLog(id={self.id}, influencer_id={self.influencer_id}, channel={self.channel.value}, status={self.status.value})>"