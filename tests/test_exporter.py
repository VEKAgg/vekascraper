import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest
from message_worker.config import WorkerConfig
from message_worker.exporter import export_messages
from shared.models.job import Job, JobType
from shared.storage.log_writer import LogWriter


def _make_job(job_id: str = "JOB-TEST") -> Job:
    return Job(job_id=job_id, type=JobType.MESSAGES, guild_id="g1")


def _make_config(tmp_path: Path) -> WorkerConfig:
    return WorkerConfig(
        discord_user_token="token",
        worker_type="messages",
        export_api_url="http://localhost:8080",
        api_key="key",
        poll_interval=10,
        data_root=str(tmp_path),
    )


def _mock_channels() -> list[dict]:
    return [
        {"id": "100", "name": "general", "type": 0, "parent_id": "cat1", "topic": "General chat"},
        {"id": "101", "name": "off-topic", "type": 0, "parent_id": "cat1", "topic": None},
    ]


def _mock_messages(count: int = 2) -> list[dict]:
    return [
        {
            "id": str(i),
            "type": 0,
            "content": f"Hello {i}",
            "timestamp": "2026-01-01T00:00:00Z",
            "edited_timestamp": None,
            "author": {"id": "u1", "username": "user1", "bot": False},
            "pinned": False,
            "attachments": [],
            "embeds": [],
            "mentions": [],
        }
        for i in range(count)
    ]


def _make_mock_client(responses: list) -> MagicMock:
    """Create a mock httpx.Client that returns responses in order."""
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)

    mocked_responses = []
    for data in responses:
        r = MagicMock()
        r.status_code = 200
        r.json.return_value = data
        r.raise_for_status = MagicMock()
        mocked_responses.append(r)

    mock_client.get.side_effect = mocked_responses
    return mock_client


class TestExportMessages:
    @patch("message_worker.exporter.httpx.Client")
    def test_creates_export_dir(self, mock_client_cls: MagicMock, tmp_path: Path) -> None:
        mock_client_cls.return_value = _make_mock_client([
            _mock_channels(),
            _mock_messages(0),
            _mock_messages(0),
        ])

        job = _make_job()
        config = _make_config(tmp_path)
        log = LogWriter(tmp_path)
        export_messages(job, config, log)
        assert (tmp_path / "exports" / "messages" / "JOB-TEST").is_dir()

    @patch("message_worker.exporter.httpx.Client")
    def test_writes_channel_files(self, mock_client_cls: MagicMock, tmp_path: Path) -> None:
        mock_client_cls.return_value = _make_mock_client([
            _mock_channels(),
            _mock_messages(3),
            _mock_messages(1),
        ])

        job = _make_job()
        config = _make_config(tmp_path)
        log = LogWriter(tmp_path)
        export_messages(job, config, log)

        export_dir = tmp_path / "exports" / "messages" / "JOB-TEST"
        assert (export_dir / "general.json").exists()
        assert (export_dir / "off-topic.json").exists()

    @patch("message_worker.exporter.httpx.Client")
    def test_channel_file_content(self, mock_client_cls: MagicMock, tmp_path: Path) -> None:
        mock_client_cls.return_value = _make_mock_client([
            _mock_channels(),
            _mock_messages(2),
            _mock_messages(0),
        ])

        job = _make_job()
        config = _make_config(tmp_path)
        log = LogWriter(tmp_path)
        export_messages(job, config, log)

        ch_file = tmp_path / "exports" / "messages" / "JOB-TEST" / "general.json"
        data = json.loads(ch_file.read_text())
        assert data["channel_id"] == "100"
        assert data["channel_name"] == "general"
        assert data["message_count"] == 2
        assert len(data["messages"]) == 2
        assert data["messages"][0]["content"] == "Hello 0"

    @patch("message_worker.exporter.httpx.Client")
    def test_returns_total_message_count(self, mock_client_cls: MagicMock, tmp_path: Path) -> None:
        mock_client_cls.return_value = _make_mock_client([
            _mock_channels(),
            _mock_messages(5),
            _mock_messages(3),
        ])

        job = _make_job()
        config = _make_config(tmp_path)
        log = LogWriter(tmp_path)
        result = export_messages(job, config, log)
        assert result["message_count"] == 8
        assert "export_path" in result

    @patch("message_worker.exporter.httpx.Client")
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
            export_messages(job, config, log)

    @patch("message_worker.exporter.httpx.Client")
    def test_handles_no_channels(self, mock_client_cls: MagicMock, tmp_path: Path) -> None:
        mock_client_cls.return_value = _make_mock_client([[]])

        job = _make_job()
        config = _make_config(tmp_path)
        log = LogWriter(tmp_path)
        result = export_messages(job, config, log)
        assert result["message_count"] == 0
