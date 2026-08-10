import json
from pathlib import Path

from member_worker.config import WorkerConfig
from member_worker.scraper import scrape_members
from shared.models.job import Job, JobType
from shared.storage.log_writer import LogWriter


def _make_job(job_id: str = "JOB-TEST") -> Job:
    return Job(job_id=job_id, type=JobType.MEMBERS, guild_id="g1")


def _make_config(tmp_path: Path) -> WorkerConfig:
    return WorkerConfig(
        worker_type="members",
        discord_user_token="token",
        export_api_url="http://localhost:8080",
        api_key="key",
        poll_interval=10,
        data_root=str(tmp_path),
    )


def test_creates_export_dir(tmp_path: Path) -> None:
    job = _make_job()
    config = _make_config(tmp_path)
    log = LogWriter(tmp_path)
    scrape_members(job, config, log)
    assert (tmp_path / "exports" / "members" / "JOB-TEST").is_dir()


def test_writes_stub_json(tmp_path: Path) -> None:
    job = _make_job()
    config = _make_config(tmp_path)
    log = LogWriter(tmp_path)
    scrape_members(job, config, log)
    content = (tmp_path / "exports" / "members" / "JOB-TEST" / "members.json").read_text()
    data = json.loads(content)
    assert data["stub"] is True
    assert data["guild_id"] == "g1"


def test_returns_correct_dict(tmp_path: Path) -> None:
    job = _make_job()
    config = _make_config(tmp_path)
    log = LogWriter(tmp_path)
    result = scrape_members(job, config, log)
    assert result["member_count"] == 0
    assert result["duration_seconds"] == 0
    assert "export_path" in result


def test_export_path_matches(tmp_path: Path) -> None:
    job = _make_job()
    config = _make_config(tmp_path)
    log = LogWriter(tmp_path)
    result = scrape_members(job, config, log)
    assert result["export_path"] == str(tmp_path / "exports" / "members" / "JOB-TEST")
