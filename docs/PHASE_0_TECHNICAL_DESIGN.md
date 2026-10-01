# Phase 0 Technical Design

## Assignment Overview

Build an automated system that discovers micro-influencers (5,000–100,000 followers), filters and classifies them, enriches profiles, generates personalized outreach messages (email + Instagram DM), and tracks sending status. Minimum 50 influencers for test run.

---

## Core Workflow

```
Discovery → Data Collection → Filtering → Enrichment → AI Personalization → Review → Sending/Simulation → Tracking
```

| Stage | Responsibility |
|-------|----------------|
| **Discovery** | Query platforms/directories via managed scrapers (Apify) for raw influencer candidates |
| **Data Collection** | Normalize, deduplicate, store in database |
| **Filtering** | Apply configurable rules (niche, followers, engagement, geography) → Qualified/Not Qualified with reasons |
| **Enrichment** | Fill mandatory fields: email (or "Not Found"), content themes, audience demographics |
| **AI Personalization** | LLM generates tailored email (60–90 words) + DM (15–30 words) per influencer |
| **Review** | Human-in-the-loop UI to approve/edit messages |
| **Sending** | Email via Gmail API; DM simulated (logged + displayed) |
| **Tracking** | Outreach log with status, deduplication via message hash |

---

## Technology Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.11+ | Rich ecosystem for scraping, data, LLM |
| API Framework | FastAPI | Async, OpenAPI docs, Pydantic integration |
| Database | SQLAlchemy + SQLite (dev) / PostgreSQL (prod) | Zero-config dev, production-ready |
| Validation | Pydantic + Pydantic Settings | Type-safe config, request/response models |
| Data Processing | Pandas | Enrichment pipelines, CSV export |
| Frontend | Streamlit | Rapid review dashboard |
| LLM | OpenAI/Anthropic API | Structured output via function calling |
| Discovery | Apify Actors | Managed scraping, no custom infrastructure |
| Email | Gmail API (OAuth2) | Reliable delivery, tracking |
| Testing | pytest + httpx | Unit + integration tests |

**Excluded:** n8n/Make/Zapier (external dependency), Selenium/Playwright (heavy), Redis/Celery (overkill for 50–500 scale).

---

## System Architecture

### Modular Package Structure
```
app/
├── api/              # FastAPI routes
├── database/         # SQLAlchemy models, session, CRUD
├── discovery/        # Apify client, source abstraction, collector
├── enrichment/       # Email finder, theme extractor, enricher
├── filtering/        # Rules engine, classifier
├── ai/               # Prompts, LLM client, generator
├── outreach/         # Gmail sender, DM simulator, tracker
└── services/         # End-to-end workflow orchestration
```

### Data Flow
1. **Discovery** → Raw JSON → `data/raw/`
2. **Collection** → Normalized → DB (Influencer table)
3. **Filtering** → Adds `qualified` flag + `reason` → DB
4. **Enrichment** → Updates mandatory/optional fields → DB
5. **AI** → Generates Message records (email + DM) → DB
6. **Review** → Human approval flag → DB
7. **Sending** → Creates OutreachLog entries → DB
8. **Export** → Pandas → CSV dataset for deliverable

---

## Discovery Strategy

**Primary Source: Apify Actors**
- Instagram Scraper, TikTok Scraper, YouTube Scraper
- Query by niche hashtags (#fitness, #fintech, #beauty, etc.)
- Filter by follower range (5k–100k) at collection time
- Extracts: profile URL, handle, bio, follower count, recent posts, engagement

**Secondary Sources (supplementary)**
- RapidAPI social media aggregators
- UGC marketplaces (Collabstr, Aspire) — manual/verified emails
- Creator newsletters — seed list only

**Constraints**
- Never fabricate data; mark missing emails as "Not Found"
- Respect rate limits and ToS
- Store raw API responses for audit

---

## Initial Niche Approach

**Primary: Fashion & Beauty** (fulfills "at least one complete filtering category" requirement)
- Clear visual content themes
- High micro-influencer density
- Well-defined audience demographics
- Straightforward brand-fit criteria (skincare, makeup, style, routine)

**Expandable to:** Fitness, Fintech, Crypto, Parenting, Gaming, Lifestyle, Technology

---

## Data Model

### Influencer
| Field | Type | Required |
|-------|------|----------|
| id | UUID | PK |
| name | str | Yes |
| platform | Enum(Instagram, YouTube, TikTok) | Yes |
| profile_url | str | Yes, unique |
| handle | str | No |
| follower_count | int | Yes |
| engagement_rate | float | Yes |
| category | str | Yes |
| content_themes | List[str] | Yes |
| email | str | Yes ("Not Found" if unavailable) |
| website | str | No |
| audience_age_range | str | No |
| audience_gender_split | JSON | No |
| audience_geography | List[str] | No |
| raw_data | JSON | Audit |
| created_at / updated_at | datetime | Auto |

### Message
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| influencer_id | UUID | FK |
| channel | Enum(Email, Instagram_DM) | |
| subject | str | Email only |
| body | str | Generated content |
| word_count | int | Validation: email 60–90, DM 15–30 |
| collaboration_angle | Enum | sponsorship, affiliate, ugc, ambassador, placement, barter |
| generated_at | datetime | Auto |
| reviewed | bool | Human approval |
| reviewer_notes | str | Optional edits |

### OutreachLog
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| influencer_id | UUID | FK |
| message_id | UUID | FK |
| channel | Enum(Email, Instagram_DM) | |
| status | Enum(pending, sent, failed, simulated, skipped) | |
| sent_at | datetime | Nullable |
| error_message | str | Nullable |
| message_hash | str | SHA256 for deduplication |
| created_at | datetime | Auto |

---

## Filtering & Classification

### Rule Configuration (YAML)
```yaml
fashion_beauty:
  category_match: [fashion, beauty, skincare, makeup, style]
  follower_range: [5000, 100000]
  min_engagement_rate: 1.5
  allowed_geographies: [US, CA, UK, AU, IN]
  required_content_themes: 1
```

### Classification Logic
- **Qualified:** Passes ALL mandatory rules
- **Not Qualified:** Fails any mandatory rule
- **Output:** Record with `status`, `failed_rules[]`, `reason` string

---

## Profile Enrichment

| Step | Method |
|------|--------|
| **Email** | Extract from bio (regex), website contact page, UGC marketplace data; mark "Not Found" if absent |
| **Content Themes** | LLM analysis of recent post captions/hashtags → structured list |
| **Audience Demographics** | Platform insights (where public), third-party estimates, or "Unknown" |
| **Engagement Rate** | Calculate from recent posts: (likes + comments) / followers × 100 |

**Principle:** Prefer "Unknown" over guessed data.

---

## AI Personalization

### Input Context (per influencer)
```json
{
  "influencer": {
    "name": "Sarah",
    "niche": "beauty/skincare",
    "content_themes": ["routine", "reviews", "sensitive skin"],
    "recent_post_summary": "Posted 3-day skincare routine for sensitive skin",
    "audience": "Women 18–30, US/CA, interested in clean beauty",
    "engagement_rate": 3.2
  },
  "brand": {
    "name": "GlowLab",
    "product": "Ceramide Repair Cream",
    "value_prop": "Dermatologist-tested, fragrance-free, 48hr hydration"
  },
  "collaboration_angle": "ugc"
}
```

### Output Schema (Pydantic)
```python
class EmailPitch(BaseModel):
    subject: str
    body: str      # 60-90 words
    word_count: int

class InstagramDM(BaseModel):
    body: str      # 15-30 words
    word_count: int
```

### Generation
- Single LLM call per influencer (structured output via function calling)
- Temperature 0.7 for variety
- Retry on word-count violation
- No fixed templates — dynamic per influencer

---

## Sending & Simulation

### Email (Gmail API)
- OAuth2 authorization flow
- `users.messages.send` with plain text + HTML
- Track `messageId` for delivery confirmation
- Daily quota awareness (100/day unverified)

### Instagram DM
- Meta Graph API requires Business Verification + Advanced Access → **not feasible**
- **Simulated:** Generate DM, display in Review UI with "Copy" button, log as `simulated` in OutreachLog

### Duplicate Prevention
- SHA256 hash of message body
- Query `OutreachLog` for same `influencer_id` + `message_hash` + `channel`
- Skip if exists

---

## Tracking

**OutreachLog fields:**
- Influencer, Email, Message, Generated, Sent Date, Status
- Statuses: `pending`, `sent`, `failed`, `simulated`, `skipped`
- Full audit trail for compliance

---

## Error Handling

| Scenario | Strategy |
|----------|----------|
| Missing email | Mark "Not Found", skip email send, still generate DM |
| API rate limit | Exponential backoff, retry queue, alert in logs |
| LLM hallucination | Strict system prompt, few-shot examples, post-validation against influencer data |
| Scraping failure | Log error, continue with other sources, partial results acceptable |
| Invalid data | Pydantic validation at ingestion, graceful degradation |
| Duplicate outreach | Hash-based deduplication at send time |

---

## Scalability Considerations

| Dimension | Current (50) | Target (500+) | Approach |
|-----------|--------------|---------------|----------|
| Discovery | Sequential Apify runs | Parallel actor runs | Async collector, batch processing |
| Enrichment | Sync per influencer | Worker pool | Task queue (future: Celery/Redis) |
| AI Generation | Sequential | Batched LLM calls | Async client, rate-limit aware |
| Database | SQLite | PostgreSQL | SQLAlchemy abstraction, connection pooling |
| Storage | Local JSON/CSV | S3/Blob | Abstract storage layer |

---

## Testing Strategy

| Layer | Tool | Coverage Target |
|-------|------|-----------------|
| Unit | pytest | Filtering rules, enrichment logic, prompt formatting |
| Integration | pytest + httpx | API endpoints, DB operations, workflow orchestration |
| Contract | pytest | Pydantic schemas, LLM output validation |
| E2E | Manual / scripted | Full pipeline: discovery → send → log |

**No external APIs in unit tests** — mock Apify, LLM, Gmail.

---

## Implementation Roadmap

| Phase | Goal | Deliverable |
|-------|------|-------------|
| 0 | Analysis | This document |
| 1 | Project Setup | FastAPI + Streamlit + tests (✅ Done) |
| 2 | Database | SQLAlchemy models, Alembic migrations |
| 3 | Discovery | Apify integration, 50+ raw profiles |
| 4 | Filtering | Rule engine, Fashion & Beauty classifier |
| 5 | Enrichment | Email finder, theme extraction, CSV export |
| 6 | AI Personalization | LLM prompts, structured output, message storage |
| 7 | Outreach | Gmail API send, DM simulation, dedup, log |
| 8 | UI | Streamlit review dashboard |
| 9 | Testing | Coverage >80%, integration tests |
| 10 | Final Demo | Repo, README, dataset, sample messages, video |

---

## Risks & Open Questions

1. **50+ real influencers with emails** — Most micro-influencers hide emails; fallback: UGC marketplaces, accept "Not Found"
2. **Engagement rate accuracy** — Public APIs often omit; calculate from recent posts (noisy)
3. **Platform scraping restrictions** — Instagram/TikTok aggressive blocking; Apify mitigates
4. **LLM hallucination** — May invent fake details; strict prompts + validation
5. **Gmail API quota** — 100/day unverified; simulate for demo, document limits
6. **Duplicate outreach** — Hash-based dedup works per-session; persist `message_hash`
7. **API costs** — Apify per-run + LLM per-call; budget ~50 runs + 50 calls
8. **Data freshness** — Metrics change; timestamp enrichment, allow re-enrichment