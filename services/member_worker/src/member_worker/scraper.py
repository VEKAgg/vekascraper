from __future__ import annotations

import logging
from pathlib import Path

from member_worker.config import WorkerConfig
from shared.models.job import Job
from shared.storage.log_writer import LogWriter

logger = logging.getLogger(__name__)


def scrape_members(job: Job, config: WorkerConfig, log: LogWriter) -> dict:
    export_dir = Path(config.data_root) / "exports" / "members" / job.job_id
    export_dir.mkdir(parents=True, exist_ok=True)

    log.info(job.job_id, f"Starting member scrape for guild {job.guild_id}",
             extra={"export_path": str(export_dir)})

    # TODO(vekascraper): Replace with actual pixelatedxp/discord-member-scraper invocation.
    # The scraper CLI expects:
    #   discord-member-scraper --token <USER_TOKEN> --guild-id <GUILD_ID> --output <DIR>
    # We stub it here for v1 scaffolding.
    logger.info("STUB: Would run member scraper for job %s", job.job_id)

    result_path = export_dir / "members.json"
    result_path.write_text(
        '{"stub": true, "guild_id": "' + job.guild_id + '", "member_count": 0}',
        encoding="utf-8",
    )

    log.info(job.job_id, "Member scrape completed (stub)",
             extra={"member_count": 0, "export_path": str(export_dir)})

    return {
        "export_path": str(export_dir),
        "member_count": 0,
        "duration_seconds": 0,
    }
