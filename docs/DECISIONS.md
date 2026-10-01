# Architectural Decisions

## 1. Language & Framework: Python + FastAPI

**Decision:** Use Python 3.11+ with FastAPI for the backend API.

**Rationale:**
- FastAPI provides async support, automatic OpenAPI docs, and native Pydantic integration
- Python has the richest ecosystem for web scraping, data processing, and LLM integration
- Team familiarity and assignment expectations align with Python

**Alternatives considered:** Node.js/Express (less mature data/ML ecosystem), Go (steeper learning curve for ML integration)

---

## 2. Frontend: Streamlit

**Decision:** Use Streamlit for the review/dashboard UI.

**Rationale:**
- Rapid development for data-centric internal tools
- Built-in components for tables, forms, JSON display
- Direct Python integration — no API serialization layer needed
- Sufficient for review/approve/send workflow

**Alternatives considered:** React/Vue (overhead for internal dashboard), plain HTML/JS (more boilerplate)

---

## 3. Database: SQLAlchemy with SQLite (Dev) → PostgreSQL (Prod)

**Decision:** Use SQLAlchemy ORM with SQLite for local development, designed for PostgreSQL compatibility.

**Rationale:**
- SQLite requires zero infrastructure for Phase 1–3 development
- SQLAlchemy abstracts dialect differences; migration to PostgreSQL is configuration-only
- Alembic provides versioned migrations from the start
- Production-grade path without premature complexity

**Schema approach:** Declarative models in `app/database/models.py`, migrations via Alembic in `alembic/`

---

## 4. Discovery: Modular Source Abstraction

**Decision:** Abstract discovery behind a `Source` protocol with Apify as the primary implementation.

**Rationale:**
- Apify provides managed, maintained scrapers for Instagram/TikTok/YouTube
- Protocol allows swapping/adding sources (RapidAPI, manual CSV, marketplace APIs) without changing downstream code
- Raw responses stored for audit and re-processing

**Interface:**
```python
class Source(Protocol):
    async def search(self, query: DiscoveryQuery) -> list[RawProfile]: ...
    async def get_profile(self, url: str) -> RawProfile: ...
```

---

## 5. AI Personalization: Structured LLM Output

**Decision:** Use function calling / structured output (Pydantic models) for email and DM generation.

**Rationale:**
- Guarantees word-count compliance (email 60–90, DM 15–30)
- Enforces required fields (subject, body, collaboration_angle)
- Eliminates post-generation parsing/retry loops
- Single LLM call per influencer returns both messages

**Prompt strategy:**
- System prompt with brand context, style guidelines, few-shot examples
- User prompt with serialized influencer profile + collaboration angle
- Temperature 0.7 for variety; retry on validation failure

---

## 6. Sending: Abstraction with Real Email + Simulated DM

**Decision:** Implement `Sender` abstraction; Gmail API for email, simulation for Instagram DM.

**Rationale:**
- Gmail API provides real sending with delivery tracking (OAuth2, `messageId`)
- Instagram DM automation is blocked by Meta's platform restrictions (requires Business Verification + Advanced Access)
- Simulation = generate DM, display in UI with "Copy" button, log as `simulated` in OutreachLog
- Abstraction allows future DM providers without changing workflow

**Interface:**
```python
class Sender(Protocol):
    async def send(self, message: Message, influencer: Influencer) -> SendResult: ...
```

---

## 7. Deduplication: Message Hash in OutreachLog

**Decision:** Prevent duplicate outreach by storing SHA256(message_body) in OutreachLog.

**Rationale:**
- Simple, deterministic, no external dependencies
- Works across sessions (persisted in DB)
- Applies per-channel (email vs DM) and per-influencer
- Query before send: `WHERE influencer_id = ? AND message_hash = ? AND channel = ?`

---

## 8. Configuration: Pydantic Settings + .env

**Decision:** All configuration via `pydantic-settings` loading from `.env` with development defaults.

**Rationale:**
- Type-safe, validated configuration
- No hardcoded secrets
- Clear documentation via `.env.example`
- Works without `.env` file (safe defaults for Phase 1)

---

## 9. Logging: Structured Stdout

**Decision:** Standard Python `logging` with configurable level, timestamp, logger name, message.

**Rationale:**
- Zero dependencies
- Works with container log aggregation
- No PII/secrets in logs by default
- Level controlled by `LOG_LEVEL` env var

---

## 10. Testing: pytest + TestClient + Mocks

**Decision:** Unit tests with pytest; FastAPI `TestClient` for API tests; mock external services.

**Rationale:**
- FastAPI's `TestClient` runs in-process, no network needed
- Mock Apify, LLM, Gmail at unit level
- Integration tests hit real DB (SQLite) and real API routes
- No external API credentials required for CI

---

## 11. Project Structure: Modular by Domain

**Decision:** Organize `app/` by functional domain (discovery, filtering, enrichment, ai, outreach, database, api, services).

**Rationale:**
- Clear ownership boundaries
- Easy to locate related code
- Supports incremental implementation (Phase 2 = database/, Phase 3 = discovery/, etc.)
- Avoids "god modules" and circular imports

---

## 12. Data Export: Pandas to CSV

**Decision:** Use Pandas for final dataset export (deliverable requirement).

**Rationale:**
- Handles nested JSON fields (content_themes, audience_gender_split) cleanly
- One-line export: `df.to_csv("influencers.csv", index=False)`
- Consistent with enrichment pipeline which already uses Pandas

---

## Summary Table

| Area | Decision | Key Benefit |
|------|----------|-------------|
| Backend | Python + FastAPI | Async, typed, OpenAPI |
| Frontend | Streamlit | Rapid data UI |
| Database | SQLAlchemy + SQLite → PostgreSQL | Zero-config dev, prod-ready |
| Discovery | Apify + Source protocol | Maintained scrapers, swappable |
| AI | Structured LLM output | Guaranteed format, word counts |
| Sending | Gmail API + DM simulation | Real email, honest DM handling |
| Deduplication | SHA256 hash in DB | Simple, persistent, per-channel |
| Config | Pydantic Settings | Type-safe, documented |
| Testing | pytest + mocks | Fast, isolated, no external deps |
| Structure | Domain-modular | Incremental, maintainable |