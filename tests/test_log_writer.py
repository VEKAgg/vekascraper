import json
from pathlib import Path

from shared.storage.log_writer import LogWriter


def test_constructor_creates_logs_dir(tmp_path: Path) -> None:
    LogWriter(tmp_path)
    assert (tmp_path / "logs").is_dir()


def test_write_creates_log_file(tmp_path: Path) -> None:
    writer = LogWriter(tmp_path)
    writer.write("JOB-123", "info", "hello")
    assert (tmp_path / "logs" / "JOB-123.log").exists()


def test_write_json_format(tmp_path: Path) -> None:
    writer = LogWriter(tmp_path)
    writer.write("JOB-123", "info", "test message")
    line = (tmp_path / "logs" / "JOB-123.log").read_text().strip()
    entry = json.loads(line)
    assert entry["job_id"] == "JOB-123"
    assert entry["severity"] == "info"
    assert entry["message"] == "test message"
    assert "timestamp" in entry


def test_write_includes_extra(tmp_path: Path) -> None:
    writer = LogWriter(tmp_path)
    writer.write("JOB-123", "info", "msg", extra={"key": "val"})
    line = (tmp_path / "logs" / "JOB-123.log").read_text().strip()
    entry = json.loads(line)
    assert entry["extra"] == {"key": "val"}


def test_write_omits_extra_when_none(tmp_path: Path) -> None:
    writer = LogWriter(tmp_path)
    writer.write("JOB-123", "info", "msg")
    line = (tmp_path / "logs" / "JOB-123.log").read_text().strip()
    entry = json.loads(line)
    assert "extra" not in entry


def test_write_appends_multiple_lines(tmp_path: Path) -> None:
    writer = LogWriter(tmp_path)
    writer.write("JOB-123", "info", "first")
    writer.write("JOB-123", "info", "second")
    lines = (tmp_path / "logs" / "JOB-123.log").read_text().strip().split("\n")
    assert len(lines) == 2


def test_write_separates_files_per_job(tmp_path: Path) -> None:
    writer = LogWriter(tmp_path)
    writer.write("JOB-111", "info", "a")
    writer.write("JOB-222", "info", "b")
    assert (tmp_path / "logs" / "JOB-111.log").exists()
    assert (tmp_path / "logs" / "JOB-222.log").exists()


def test_info_severity(tmp_path: Path) -> None:
    writer = LogWriter(tmp_path)
    writer.info("JOB-1", "msg")
    line = (tmp_path / "logs" / "JOB-1.log").read_text().strip()
    assert json.loads(line)["severity"] == "info"


def test_error_severity(tmp_path: Path) -> None:
    writer = LogWriter(tmp_path)
    writer.error("JOB-1", "msg")
    line = (tmp_path / "logs" / "JOB-1.log").read_text().strip()
    assert json.loads(line)["severity"] == "error"


def test_warning_severity(tmp_path: Path) -> None:
    writer = LogWriter(tmp_path)
    writer.warning("JOB-1", "msg")
    line = (tmp_path / "logs" / "JOB-1.log").read_text().strip()
    assert json.loads(line)["severity"] == "warning"
