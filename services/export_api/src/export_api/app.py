from __future__ import annotations

import logging
from pathlib import Path

from export_api.config import APIConfig
from export_api.routers import health, jobs
from fastapi import FastAPI
from shared.storage.paths import ensure_dirs

logger = logging.getLogger(__name__)


def create_app(config: APIConfig) -> FastAPI:
    app = FastAPI(
        title="vekascraper Export API",
        version="0.1.0",
        description="Internal API for job queue, state, and cancellation",
    )

    app.state.config = config
    app.state.paths = ensure_dirs(root=Path(config.data_root))

    app.include_router(health.router, tags=["health"])
    app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

    return app
