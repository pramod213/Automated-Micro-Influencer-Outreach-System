"""Influencer repository for database operations."""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.models import Influencer, Platform


class InfluencerRepository:
    """Repository for Influencer database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, influencer: Influencer) -> Influencer:
        """Create a new influencer record."""
        self.db.add(influencer)
        self.db.flush()
        self.db.refresh(influencer)
        return influencer

    def get_by_id(self, influencer_id: int) -> Optional[Influencer]:
        """Get influencer by ID."""
        return self.db.get(Influencer, influencer_id)

    def get_by_profile_url(self, platform: Platform, profile_url: str) -> Optional[Influencer]:
        """Get influencer by platform and profile URL (unique identity)."""
        stmt = select(Influencer).where(
            Influencer.platform == platform,
            Influencer.profile_url == profile_url,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        platform: Optional[Platform] = None,
        category: Optional[str] = None,
    ) -> List[Influencer]:
        """List influencers with optional filters."""
        stmt = select(Influencer)
        if platform:
            stmt = stmt.where(Influencer.platform == platform)
        if category:
            stmt = stmt.where(Influencer.category == category)
        stmt = stmt.offset(skip).limit(limit).order_by(Influencer.created_at.desc())
        return list(self.db.execute(stmt).scalars().all())

    def update(self, influencer: Influencer) -> Influencer:
        """Update an existing influencer record."""
        self.db.add(influencer)
        self.db.flush()
        self.db.refresh(influencer)
        return influencer

    def delete(self, influencer_id: int) -> bool:
        """Delete an influencer by ID."""
        influencer = self.get_by_id(influencer_id)
        if influencer:
            self.db.delete(influencer)
            self.db.flush()
            return True
        return False