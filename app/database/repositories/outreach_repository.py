"""OutreachLog repository for database operations."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.models import OutreachLog, OutreachChannel


class OutreachRepository:
    """Repository for OutreachLog database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, outreach_log: OutreachLog) -> OutreachLog:
        """Create a new outreach log record."""
        self.db.add(outreach_log)
        self.db.flush()
        self.db.refresh(outreach_log)
        return outreach_log

    def list_by_influencer(
        self,
        influencer_id: int,
        skip: int = 0,
        limit: int = 100,
        channel: Optional[OutreachChannel] = None,
    ) -> List[OutreachLog]:
        """List outreach logs for a specific influencer."""
        stmt = select(OutreachLog).where(OutreachLog.influencer_id == influencer_id)
        if channel:
            stmt = stmt.where(OutreachLog.channel == channel)
        stmt = stmt.offset(skip).limit(limit).order_by(OutreachLog.created_at.desc())
        return list(self.db.execute(stmt).scalars().all())

    def list_by_message(
        self,
        message_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[OutreachLog]:
        """List outreach logs for a specific message."""
        stmt = (
            select(OutreachLog)
            .where(OutreachLog.message_id == message_id)
            .offset(skip)
            .limit(limit)
            .order_by(OutreachLog.created_at.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def exists_for_influencer_channel(
        self,
        influencer_id: int,
        channel: OutreachChannel,
        message_hash: str,
    ) -> bool:
        """Check if outreach already exists for influencer, channel, and message hash."""
        stmt = select(OutreachLog).where(
            OutreachLog.influencer_id == influencer_id,
            OutreachLog.channel == channel,
            OutreachLog.message_hash == message_hash,
        )
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def get_by_id(self, outreach_id: int) -> Optional[OutreachLog]:
        """Get outreach log by ID."""
        return self.db.get(OutreachLog, outreach_id)

    def update_status(
        self,
        outreach_id: int,
        status: str,
        sent_at: Optional[datetime] = None,
        error: Optional[str] = None,
    ) -> Optional[OutreachLog]:
        """Update outreach log status."""
        outreach = self.get_by_id(outreach_id)
        if outreach:
            outreach.status = status
            if sent_at:
                outreach.sent_at = sent_at
            if error:
                outreach.error = error
            self.db.add(outreach)
            self.db.flush()
            self.db.refresh(outreach)
        return outreach