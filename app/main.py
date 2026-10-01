"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.logging_config import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    setup_logging()
    logging.getLogger(__name__).info("Application starting up...")
    yield
    logging.getLogger(__name__).info("Application shutting down...")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Automated Micro-Influencer Outreach System API",
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}