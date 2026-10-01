"""Message repository for database operations."""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.models import Message


class MessageRepository:
    """Repository for Message database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, message: Message) -> Message:
        """Create a new message record."""
        self.db.add(message)
        self.db.flush()
        self.db.refresh(message)
        return message

    def get_by_id(self, message_id: int) -> Optional[Message]:
        """Get message by ID."""
        return self.db.get(Message, message_id)

    def list_by_influencer(
        self,
        influencer_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Message]:
        """List messages for a specific influencer."""
        stmt = (
            select(Message)
            .where(Message.influencer_id == influencer_id)
            .offset(skip)
            .limit(limit)
            .order_by(Message.generated_at.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_latest_by_influencer(self, influencer_id: int) -> Optional[Message]:
        """Get the most recent message for an influencer."""
        stmt = (
            select(Message)
            .where(Message.influencer_id == influencer_id)
            .order_by(Message.generated_at.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()