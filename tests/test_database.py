"""Database tests."""

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from app.database.base import Base
from app.database.models import (
    Influencer,
    Platform,
    Message,
    CollaborationAngle,
    OutreachLog,
    OutreachChannel,
    OutreachStatus,
)
from app.database.repositories import (
    InfluencerRepository,
    MessageRepository,
    OutreachRepository,
)


@pytest.fixture
def test_engine():
    """Create a test database engine using in-memory SQLite."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_session(test_engine):
    """Create a test database session."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def test_database_connection(test_session):
    """Test that database connection works."""
    result = test_session.execute(select(1)).scalar()
    assert result == 1


def test_influencer_crud(test_session):
    """Test influencer create, read operations."""
    repo = InfluencerRepository(test_session)

    # Create influencer
    influencer = Influencer(
        name="Test Influencer",
        platform=Platform.INSTAGRAM,
        profile_url="https://instagram.com/testuser",
        handle="testuser",
        follower_count=10000,
        engagement_rate=3.5,
        category="fashion",
        content_themes=["style", "outfits"],
        contact_email="test@example.com",
    )
    created = repo.create(influencer)
    assert created.id is not None
    assert created.name == "Test Influencer"

    # Get by ID
    retrieved = repo.get_by_id(created.id)
    assert retrieved is not None
    assert retrieved.name == "Test Influencer"

    # Get by profile URL
    retrieved = repo.get_by_profile_url(Platform.INSTAGRAM, "https://instagram.com/testuser")
    assert retrieved is not None
    assert retrieved.id == created.id

    # List influencers
    influencers = repo.list()
    assert len(influencers) >= 1


def test_influencer_unique_constraint(test_session):
    """Test that duplicate profile URL on same platform is prevented."""
    from sqlalchemy.exc import IntegrityError

    repo = InfluencerRepository(test_session)

    influencer1 = Influencer(
        name="Test Influencer 1",
        platform=Platform.INSTAGRAM,
        profile_url="https://instagram.com/duplicate",
        follower_count=10000,
        engagement_rate=3.5,
        category="fashion",
        content_themes=["style"],
        contact_email="test1@example.com",
    )
    repo.create(influencer1)

    influencer2 = Influencer(
        name="Test Influencer 2",
        platform=Platform.INSTAGRAM,
        profile_url="https://instagram.com/duplicate",
        follower_count=20000,
        engagement_rate=4.0,
        category="beauty",
        content_themes=["makeup"],
        contact_email="test2@example.com",
    )

    # This should raise an integrity error due to unique constraint
    with pytest.raises(IntegrityError):
        repo.create(influencer2)
        test_session.flush()


def test_message_crud(test_session):
    """Test message create, read operations."""
    # First create an influencer
    influencer_repo = InfluencerRepository(test_session)
    influencer = Influencer(
        name="Test Influencer",
        platform=Platform.INSTAGRAM,
        profile_url="https://instagram.com/message_test",
        follower_count=10000,
        engagement_rate=3.5,
        category="fashion",
        content_themes=["style"],
        contact_email="test@example.com",
    )
    influencer = influencer_repo.create(influencer)

    # Create message
    message_repo = MessageRepository(test_session)
    message = Message(
        influencer_id=influencer.id,
        email_subject="Collaboration Opportunity",
        email_body="Hello, we would like to collaborate with you...",
        instagram_dm="Hi, loved your content!",
        personalization_signals=["style", "fashion"],
        collaboration_angle=CollaborationAngle.UGC,
        ai_model="gpt-4",
        prompt_version="1.0",
    )
    created = message_repo.create(message)
    assert created.id is not None
    assert created.influencer_id == influencer.id

    # Get by ID
    retrieved = message_repo.get_by_id(created.id)
    assert retrieved is not None
    assert retrieved.email_subject == "Collaboration Opportunity"

    # List by influencer
    messages = message_repo.list_by_influencer(influencer.id)
    assert len(messages) == 1
    assert messages[0].id == created.id


def test_outreach_log_crud(test_session):
    """Test outreach log create, read operations."""
    # First create an influencer
    influencer_repo = InfluencerRepository(test_session)
    influencer = Influencer(
        name="Test Influencer",
        platform=Platform.INSTAGRAM,
        profile_url="https://instagram.com/outreach_test",
        follower_count=10000,
        engagement_rate=3.5,
        category="fashion",
        content_themes=["style"],
        contact_email="test@example.com",
    )
    influencer = influencer_repo.create(influencer)

    # Create message
    message_repo = MessageRepository(test_session)
    message = Message(
        influencer_id=influencer.id,
        email_subject="Collaboration",
        email_body="Body",
        instagram_dm="DM",
        personalization_signals=[],
        collaboration_angle=CollaborationAngle.UGC,
        ai_model="gpt-4",
        prompt_version="1.0",
    )
    message = message_repo.create(message)

    # Create outreach log
    outreach_repo = OutreachRepository(test_session)
    outreach = OutreachLog(
        influencer_id=influencer.id,
        message_id=message.id,
        channel=OutreachChannel.EMAIL,
        status=OutreachStatus.PENDING,
        message_hash="abc123",
    )
    created = outreach_repo.create(outreach)
    assert created.id is not None
    assert created.influencer_id == influencer.id
    assert created.message_id == message.id
    assert created.channel == OutreachChannel.EMAIL
    assert created.status == OutreachStatus.PENDING

    # List by influencer
    logs = outreach_repo.list_by_influencer(influencer.id)
    assert len(logs) == 1

    # Check duplicate prevention
    exists = outreach_repo.exists_for_influencer_channel(
        influencer.id, OutreachChannel.EMAIL, "abc123"
    )
    assert exists is True

    # Different hash should not exist
    exists = outreach_repo.exists_for_influencer_channel(
        influencer.id, OutreachChannel.EMAIL, "different_hash"
    )
    assert exists is False


def test_relationships(test_session):
    """Test that relationships work correctly."""
    influencer_repo = InfluencerRepository(test_session)
    message_repo = MessageRepository(test_session)
    outreach_repo = OutreachRepository(test_session)

    # Create influencer
    influencer = Influencer(
        name="Relationship Test",
        platform=Platform.YOUTUBE,
        profile_url="https://youtube.com/rel_test",
        follower_count=50000,
        engagement_rate=2.5,
        category="tech",
        content_themes=["coding", "reviews"],
        contact_email="rel@example.com",
    )
    influencer = influencer_repo.create(influencer)

    # Create message
    message = Message(
        influencer_id=influencer.id,
        email_subject="Subject",
        email_body="Body",
        instagram_dm="DM",
        personalization_signals=["tech"],
        collaboration_angle=CollaborationAngle.SPONSORSHIP,
        ai_model="gpt-4",
        prompt_version="1.0",
    )
    message = message_repo.create(message)

    # Create outreach log
    outreach = OutreachLog(
        influencer_id=influencer.id,
        message_id=message.id,
        channel=OutreachChannel.EMAIL,
        status=OutreachStatus.SENT,
        message_hash="hash123",
    )
    outreach_repo.create(outreach)

    # Commit to ensure all objects are persisted
    test_session.commit()

    # Test relationships - refresh to load relationships
    test_session.refresh(influencer)
    assert len(influencer.messages) == 1
    assert influencer.messages[0].id == message.id
    assert len(influencer.outreach_logs) == 1
    assert influencer.outreach_logs[0].id == outreach.id

    # Test message -> influencer relationship
    test_session.refresh(message)
    assert message.influencer.id == influencer.id
    assert len(message.outreach_logs) == 1

    # Test outreach -> influencer/message relationships
    test_session.refresh(outreach)
    assert outreach.influencer.id == influencer.id
    assert outreach.message.id == message.id


def test_default_values(test_session):
    """Test that default values work correctly."""
    repo = InfluencerRepository(test_session)

    influencer = Influencer(
        name="Default Test",
        platform=Platform.TIKTOK,
        profile_url="https://tiktok.com/default_test",
        follower_count=15000,
        engagement_rate=4.0,
        category="lifestyle",
        content_themes=["daily"],
        # contact_email not provided - should default to "Not Found"
    )
    created = repo.create(influencer)

    assert created.contact_email == "Not Found"
    assert created.content_themes == ["daily"]
    assert created.created_at is not None
    assert created.updated_at is not None