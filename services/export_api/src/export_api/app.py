from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from export_api.config import APIConfig
from export_api.routers import health, jobs
from shared.storage.paths import ensure_dirs

logger = logging.getLogger(__name__)


def create_app(config: APIConfig) -> FastAPI:
    app = FastAPI(
        title="vekascraper Export API",
        version="0.1.0",
        description="Internal API for job queue, state, and cancellation",
    )

    app.state.config = config
    app.state.paths = ensure_dirs()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[],
        allow_methods=["GET", "POST"],
        allow_headers=["X-API-Key", "Content-Type"],
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

    return app
