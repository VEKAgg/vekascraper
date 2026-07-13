from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from member_worker.config import WorkerConfig
from member_worker.scraper import scrape_members
from shared.models.job import JobState
from shared.models.manifest import Manifest
from shared.storage.job_store import JobStore
from shared.storage.log_writer import LogWriter
from shared.storage.manifest_store import ManifestStore
from shared.storage.paths import ensure_dirs

logger = logging.getLogger(__name__)


def run_worker(config: WorkerConfig) -> None:
    logger.info("Starting %s worker (poll every %ds)", config.worker_type, config.poll_interval)

    paths = ensure_dirs()
    store = JobStore(paths.root)
    manifest_store = ManifestStore(paths.root)
    log_writer = LogWriter(paths.root)

    while True:
        try:
            job = store.claim_next(config.worker_type)
            if job is not None:
                log_writer.info(job.job_id, f"Worker claimed job {job.job_id}",
                                extra={"type": job.type.value})
                _execute_job(job, store, manifest_store, log_writer, config)
            else:
                time.sleep(config.poll_interval)
        except Exception:
            logger.exception("Worker loop error")
            time.sleep(config.poll_interval)


def _execute_job(
    job: object,
    store: JobStore,
    manifest_store: ManifestStore,
    log_writer: LogWriter,
    config: WorkerConfig,
) -> None:
    from shared.models.job import Job as JobModel

    job_obj = store.get(job.job_id) if isinstance(job, JobModel) else job
    if job_obj is None:
        return

    started_at = datetime.now(timezone.utc)
    log_writer.info(job_obj.job_id, "Execution started")

    try:
        result = scrape_members(job_obj, config, log_writer)
        completed_at = datetime.now(timezone.utc)
        duration = int((completed_at - started_at).total_seconds())

        manifest = Manifest(
            job_id=job_obj.job_id,
            type=job_obj.type.value,
            guild_id=job_obj.guild_id,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration,
            member_count=result.get("member_count"),
            export_path=result.get("export_path", ""),
        )
        manifest_store.write(manifest)

        job_obj.transition(JobState.COMPLETED)
        store.save(job_obj)
        log_writer.info(job_obj.job_id, "Job completed successfully",
                        extra={"duration_seconds": duration})

        _handle_chain(job_obj, store, log_writer)

    except Exception as exc:
        completed_at = datetime.now(timezone.utc)
        duration = int((completed_at - started_at).total_seconds())
        job_obj.transition(JobState.FAILED)
        job_obj.error = str(exc)
        store.save(job_obj)
        log_writer.error(job_obj.job_id, f"Job failed: {exc}",
                         extra={"duration_seconds": duration})


def _handle_chain(job: object, store: JobStore, log_writer: LogWriter) -> None:
    from shared.models.job import Job as JobModel

    job_obj = store.get(job.job_id) if isinstance(job, JobModel) else job
    if job_obj is None or not job_obj.chain_next:
        return

    next_job = store.get(job_obj.chain_next)
    if next_job is None:
        log_writer.warning(job_obj.job_id,
                           f"Chain target {job_obj.chain_next} not found")
        return

    next_job.transition(JobState.QUEUED)
    store.save(next_job)
    log_writer.info(job_obj.job_id,
                    f"Queued chained job {next_job.job_id}")
