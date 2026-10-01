"""Streamlit frontend application."""

import streamlit as st
import requests


st.set_page_config(
    page_title="Automated Micro-Influencer Outreach System",
    page_icon="🤖",
    layout="wide",
)


def check_backend_health() -> dict:
    """Check if the backend is reachable."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            return {"status": "connected", "data": response.json()}
        return {"status": "error", "data": f"HTTP {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"status": "disconnected", "data": "Backend not running"}
    except requests.exceptions.Timeout:
        return {"status": "timeout", "data": "Backend request timed out"}
    except Exception as e:
        return {"status": "error", "data": str(e)}


def main():
    """Main Streamlit application."""
    st.title("🤖 Automated Micro-Influencer Outreach System")
    st.caption("Phase 1 — Project Setup")

    st.divider()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Project Status")
        st.info(
            """
            **Current Phase:** Phase 1 — Project Setup

            This is the foundation phase. The following components are implemented:
            - ✅ FastAPI backend with health endpoint
            - ✅ Configuration management
            - ✅ Logging setup
            - ✅ Streamlit frontend skeleton
            - ✅ Basic test suite
            """
        )

    with col2:
        st.subheader("Backend Status")
        backend_status = check_backend_health()

        if backend_status["status"] == "connected":
            st.success("🟢 Backend Connected")
            st.json(backend_status["data"])
        elif backend_status["status"] == "disconnected":
            st.warning("🟡 Backend Disconnected")
            st.caption("Start the backend with: `uvicorn app.main:app --reload`")
        else:
            st.error(f"🔴 Backend Error: {backend_status['data']}")

    st.divider()

    st.subheader("Upcoming Phases")
    phases = [
        "Phase 2 — Database Models & Migrations",
        "Phase 3 — Influencer Discovery (Apify integration)",
        "Phase 4 — Filtering & Classification",
        "Phase 5 — Profile Enrichment",
        "Phase 6 — AI Personalization (LLM integration)",
        "Phase 7 — Outreach & Sending Layer",
        "Phase 8 — Full Dashboard UI",
        "Phase 9 — Testing & Quality Assurance",
        "Phase 10 — Final Demo & Documentation",
    ]
    for i, phase in enumerate(phases, 2):
        st.write(f"{i}. {phase}")


if __name__ == "__main__":
    main()