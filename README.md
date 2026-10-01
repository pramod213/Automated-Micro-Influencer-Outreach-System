# Automated Micro-Influencer Outreach System

An AI-powered system for discovering, filtering, enriching, and reaching out to micro-influencers across social media platforms.

## Current Phase

**Phase 1 — Project Setup**

## Requirements

- Python 3.11+
- pip (Python package manager)

## Setup

### 1. Create Virtual Environment

```bash
# Windows
python -m venv .venv

# Linux/macOS
python3 -m venv .venv
```

### 2. Activate Virtual Environment

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (cmd)
.venv\Scripts\activate.bat

# Linux/macOS
source .venv/bin/activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit .env as needed (optional for Phase 1)
```

## Run Backend

Start the FastAPI application:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API:** http://localhost:8000
- **Health Check:** http://localhost:8000/health
- **Interactive Docs:** http://localhost:8000/docs

## Run Frontend

Start the Streamlit application (in a separate terminal):

```bash
streamlit run frontend/streamlit_app.py
```

The frontend will be available at:
- **UI:** http://localhost:8501

## Run Tests

```bash
pytest
```

Or with verbose output:

```bash
pytest -v
```

## Current Scope

This repository currently implements **only Phase 1 — Project Setup**:

- ✅ FastAPI backend with `/health` endpoint
- ✅ Configuration management via Pydantic Settings
- ✅ Structured logging
- ✅ Streamlit frontend skeleton with backend status display
- ✅ Basic test suite (health endpoint tests)
- ✅ Development environment configuration

**Not yet implemented (future phases):**
- Database models and migrations
- Influencer discovery (Apify, social media APIs)
- Filtering and classification logic
- Profile enrichment
- AI/LLM-based message personalization
- Email sending (Gmail API) or Instagram DM simulation
- Outreach tracking and analytics
- Full dashboard UI
- Real or synthetic influencer datasets

## Future Phases

1. **Phase 2** — Database Models & Migrations (SQLAlchemy, Alembic)
2. **Phase 3** — Influencer Discovery (Apify integration, 50+ profiles)
3. **Phase 4** — Filtering & Classification (configurable rules engine)
4. **Phase 5** — Profile Enrichment (email extraction, theme analysis)
5. **Phase 6** — AI Personalization (LLM prompts, structured output)
6. **Phase 7** — Outreach & Sending Layer (Gmail API, DM simulation)
7. **Phase 8** — Full Dashboard UI (review, approve, send, track)
8. **Phase 9** — Testing & Quality Assurance (coverage, integration tests)
9. **Phase 10** — Final Demo & Documentation