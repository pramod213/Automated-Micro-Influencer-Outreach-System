"""Message model."""

import enum
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, ForeignKey, Enum, Index, Text, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin


class CollaborationAngle(enum.Enum):
    """Collaboration angle enumeration."""

    SPONSORSHIP = "sponsorship"
    AFFILIATE = "affiliate"
    UGC = "ugc"
    AMBASSADOR = "ambassador"
    PLACEMENT = "placement"
    BARTER = "barter"


class Message(Base, TimestampMixin):
    """Message model representing AI-generated outreach messages."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    influencer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("influencers.id", ondelete="CASCADE"), nullable=False
    )
    email_subject: Mapped[str] = mapped_column(String(500), nullable=False)
    email_body: Mapped[str] = mapped_column(Text, nullable=False)
    instagram_dm: Mapped[str] = mapped_column(Text, nullable=False)
    personalization_signals: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    collaboration_angle: Mapped[CollaborationAngle] = mapped_column(Enum(CollaborationAngle), nullable=False)
    ai_model: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    influencer: Mapped["Influencer"] = relationship("Influencer", back_populates="messages")
    outreach_logs: Mapped[List["OutreachLog"]] = relationship(
        "OutreachLog",
        back_populates="message",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Table constraints and indexes
    __table_args__ = (
        Index("ix_message_influencer_id", "influencer_id"),
        Index("ix_message_generated_at", "generated_at"),
        Index("ix_message_prompt_version", "prompt_version"),
    )

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, influencer_id={self.influencer_id}, angle={self.collaboration_angle.value})>"