from __future__ import annotations

import logging
from pathlib import Path

from message_worker.config import WorkerConfig
from shared.models.job import Job
from shared.storage.log_writer import LogWriter

logger = logging.getLogger(__name__)


def export_messages(job: Job, config: WorkerConfig, log: LogWriter) -> dict:
    export_dir = Path(config.data_root) / "exports" / "messages" / job.job_id
    export_dir.mkdir(parents=True, exist_ok=True)

    log.info(job.job_id, f"Starting message export for guild {job.guild_id}",
             extra={"export_path": str(export_dir)})

    # TODO(vekascraper): Replace with actual DiscordChatExporter CLI invocation.
    # The exporter expects:
    #   discorde chat export --channel <CHANNEL_ID> -t <USER_TOKEN> -o <DIR>
    # FIXME: Fix this typo when implementing. Should be "discord chat export" per
    #   https://github.com/Tyrrrz/DiscordChatExporter
    # We stub it here for v1 scaffolding.
    # TODO(vekascraper): Poll store.get(job.job_id).state periodically to
    # honour CANCELLING signal during long-running exporter execution.
    logger.info("STUB: Would run DiscordChatExporter for job %s", job.job_id)

    result_path = export_dir / "messages.json"
    result_path.write_text(
        '{"stub": true, "guild_id": "' + job.guild_id + '", "message_count": 0}',
        encoding="utf-8",
    )

    log.info(job.job_id, "Message export completed (stub)",
             extra={"message_count": 0, "export_path": str(export_dir)})

    return {
        "export_path": str(export_dir),
        "message_count": 0,
        "duration_seconds": 0,
    }
