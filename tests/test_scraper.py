import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest
from member_worker.config import WorkerConfig
from member_worker.scraper import scrape_members
from shared.models.job import Job, JobType
from shared.storage.log_writer import LogWriter


def _make_job(job_id: str = "JOB-TEST") -> Job:
    return Job(job_id=job_id, type=JobType.MEMBERS, guild_id="g1")


def _make_config(tmp_path: Path) -> WorkerConfig:
    return WorkerConfig(
        discord_user_token="token",
        worker_type="members",
        export_api_url="http://localhost:8080",
        api_key="key",
        poll_interval=10,
        data_root=str(tmp_path),
    )


def _mock_members_response(count: int = 3) -> MagicMock:
    members = [
        {"user": {"id": str(i), "username": f"user{i}"}, "roles": [], "joined_at": "2026-01-01"}
        for i in range(count)
    ]
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = members
    resp.raise_for_status = MagicMock()
    return resp


class TestScrapeMembers:
    @patch("member_worker.scraper.httpx.Client")
    def test_creates_export_dir(self, mock_client_cls: MagicMock, tmp_path: Path) -> None:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = _mock_members_response(0)
        mock_client_cls.return_value = mock_client

        job = _make_job()
        config = _make_config(tmp_path)
        log = LogWriter(tmp_path)
        scrape_members(job, config, log)
        assert (tmp_path / "exports" / "members" / "JOB-TEST").is_dir()

    @patch("member_worker.scraper.httpx.Client")
    def test_writes_members_json(self, mock_client_cls: MagicMock, tmp_path: Path) -> None:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = _mock_members_response(2)
        mock_client_cls.return_value = mock_client

        job = _make_job()
        config = _make_config(tmp_path)
        log = LogWriter(tmp_path)
        scrape_members(job, config, log)

        result_file = tmp_path / "exports" / "members" / "JOB-TEST" / "members.json"
        assert result_file.exists()
        data = json.loads(result_file.read_text())
        assert data["guild_id"] == "g1"
        assert len(data["members"]) == 2
        assert data["members"][0]["id"] == "0"
        assert data["members"][0]["username"] == "user0"

    @patch("member_worker.scraper.httpx.Client")
    def test_returns_correct_dict(self, mock_client_cls: MagicMock, tmp_path: Path) -> None:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = _mock_members_response(5)
        mock_client_cls.return_value = mock_client

        job = _make_job()
        config = _make_config(tmp_path)
        log = LogWriter(tmp_path)
        result = scrape_members(job, config, log)
        assert result["member_count"] == 5
        assert "export_path" in result

    @patch("member_worker.scraper.httpx.Client")
    def test_handles_empty_guild(self, mock_client_cls: MagicMock, tmp_path: Path) -> None:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = _mock_members_response(0)
        mock_client_cls.return_value = mock_client

        job = _make_job()
        config = _make_config(tmp_path)
        log = LogWriter(tmp_path)
        result = scrape_members(job, config, log)
        assert result["member_count"] == 0

    @patch("member_worker.scraper.httpx.Client")
    def test_raises_on_http_error(self, mock_client_cls: MagicMock, tmp_path: Path) -> None:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        error_resp = MagicMock()
        error_resp.status_code = 403
        error_resp.text = "Forbidden"
        mock_client.get.side_effect = httpx.HTTPStatusError(
            "403 Forbidden", request=MagicMock(), response=error_resp,
        )
        mock_client_cls.return_value = mock_client

        job = _make_job()
        config = _make_config(tmp_path)
        log = LogWriter(tmp_path)
        with pytest.raises(RuntimeError, match="403"):
            scrape_members(job, config, log)
