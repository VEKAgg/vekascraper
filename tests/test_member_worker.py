from pathlib import Path
from unittest.mock import MagicMock, patch

from member_worker.config import WorkerConfig
from member_worker.worker import (
    _check_cancelled,
    _execute_job,
    _finish_cancelled,
    _handle_chain,
)
from shared.models.job import Job, JobState, JobType
from shared.storage.job_store import JobStore
from shared.storage.log_writer import LogWriter
from shared.storage.manifest_store import ManifestStore


def _setup(tmp_path: Path) -> tuple[JobStore, ManifestStore, LogWriter, WorkerConfig]:
    store = JobStore(tmp_path)
    manifest_store = ManifestStore(tmp_path)
    log = LogWriter(tmp_path)
    config = WorkerConfig(
        worker_type="members",
        discord_user_token="token",
        export_api_url="http://localhost:8080",
        api_key="key",
        poll_interval=10,
        data_root=str(tmp_path),
    )
    return store, manifest_store, log, config


def _create_job(store: JobStore, state: JobState = JobState.RUNNING) -> Job:
    job = store.create(JobType.MEMBERS, "g1")
    if state != JobState.CREATED:
        job.transition(JobState.QUEUED)
    if state in (JobState.RUNNING, JobState.CANCELLING, JobState.COMPLETED, JobState.FAILED):
        job.transition(JobState.RUNNING)
    if state == JobState.CANCELLING:
        job.transition(JobState.CANCELLING)
    if state == JobState.COMPLETED:
        job.transition(JobState.COMPLETED)
    if state == JobState.FAILED:
        job.transition(JobState.FAILED)
    store.save(job)
    return job


class TestCheckCancelled:
    def test_true_when_cancelling(self, tmp_path: Path) -> None:
        store, _, _, _ = _setup(tmp_path)
        job = _create_job(store, JobState.CANCELLING)
        assert _check_cancelled(store, job.job_id) is True

    def test_false_when_running(self, tmp_path: Path) -> None:
        store, _, _, _ = _setup(tmp_path)
        job = _create_job(store, JobState.RUNNING)
        assert _check_cancelled(store, job.job_id) is False

    def test_false_when_missing(self, tmp_path: Path) -> None:
        store, _, _, _ = _setup(tmp_path)
        assert _check_cancelled(store, "NONEXISTENT") is False


class TestFinishCancelled:
    def test_transitions_to_cancelled(self, tmp_path: Path) -> None:
        store, _, log, _ = _setup(tmp_path)
        job = _create_job(store, JobState.CANCELLING)
        _finish_cancelled(job, store, log)
        updated = store.get(job.job_id)
        assert updated is not None
        assert updated.state == JobState.CANCELLED

    def test_noops_when_missing(self, tmp_path: Path) -> None:
        store, _, log, _ = _setup(tmp_path)
        job = Job(job_id="MISSING", type=JobType.MEMBERS, guild_id="g1", state=JobState.CANCELLING)
        _finish_cancelled(job, store, log)


class TestExecuteJob:
    @patch("member_worker.worker.scrape_members")
    def test_happy_path(self, mock_scrape: MagicMock, tmp_path: Path) -> None:
        mock_scrape.return_value = {"export_path": "/x", "member_count": 5, "duration_seconds": 2}
        store, manifest_store, log, config = _setup(tmp_path)
        job = _create_job(store, JobState.RUNNING)
        _execute_job(job, store, manifest_store, log, config)
        updated = store.get(job.job_id)
        assert updated is not None
        assert updated.state == JobState.COMPLETED

    @patch("member_worker.worker.scrape_members")
    def test_sets_error_on_exception(self, mock_scrape: MagicMock, tmp_path: Path) -> None:
        mock_scrape.side_effect = RuntimeError("scrape failed")
        store, manifest_store, log, config = _setup(tmp_path)
        job = _create_job(store, JobState.RUNNING)
        _execute_job(job, store, manifest_store, log, config)
        updated = store.get(job.job_id)
        assert updated is not None
        assert updated.state == JobState.FAILED
        assert "scrape failed" in (updated.error or "")

    def test_skips_when_already_cancelled(self, tmp_path: Path) -> None:
        store, manifest_store, log, config = _setup(tmp_path)
        job = _create_job(store, JobState.CANCELLING)
        with patch("member_worker.worker.scrape_members") as mock_scrape:
            _execute_job(job, store, manifest_store, log, config)
            mock_scrape.assert_not_called()
        updated = store.get(job.job_id)
        assert updated is not None
        assert updated.state == JobState.CANCELLED

    def test_skips_when_job_missing(self, tmp_path: Path) -> None:
        store, manifest_store, log, config = _setup(tmp_path)
        job = Job(job_id="MISSING", type=JobType.MEMBERS, guild_id="g1", state=JobState.RUNNING)
        _execute_job(job, store, manifest_store, log, config)


class TestHandleChain:
    def test_queues_next_job(self, tmp_path: Path) -> None:
        store, _, log, _ = _setup(tmp_path)
        next_job = store.create(JobType.MESSAGES, "g1")
        job = store.create(JobType.MEMBERS, "g1")
        job.chain_next = next_job.job_id
        store.save(job)
        _handle_chain(job, store, log)
        updated = store.get(next_job.job_id)
        assert updated is not None
        assert updated.state == JobState.QUEUED

    def test_noop_when_no_chain(self, tmp_path: Path) -> None:
        store, _, log, _ = _setup(tmp_path)
        job = store.create(JobType.MEMBERS, "g1")
        _handle_chain(job, store, log)

    def test_warns_when_target_missing(self, tmp_path: Path) -> None:
        store, _, log, _ = _setup(tmp_path)
        job = store.create(JobType.MEMBERS, "g1")
        job.chain_next = "NONEXISTENT"
        store.save(job)
        _handle_chain(job, store, log)
