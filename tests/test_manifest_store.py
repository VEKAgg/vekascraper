from datetime import datetime, timezone
from pathlib import Path

from shared.models.manifest import Manifest
from shared.storage.manifest_store import ManifestStore


def _make_manifest(job_id: str = "JOB-123") -> Manifest:
    now = datetime.now(timezone.utc)
    return Manifest(
        job_id=job_id,
        type="messages",
        guild_id="g1",
        started_at=now,
        completed_at=now,
        duration_seconds=10,
        message_count=100,
        export_path="/data/exports/messages/JOB-123",
    )


def test_constructor_creates_manifests_dir(tmp_path: Path) -> None:
    ManifestStore(tmp_path)
    assert (tmp_path / "manifests").is_dir()


def test_write_returns_path(tmp_path: Path) -> None:
    store = ManifestStore(tmp_path)
    path = store.write(_make_manifest())
    assert path.name == "JOB-123.json"
    assert path.exists()


def test_write_creates_json_file(tmp_path: Path) -> None:
    store = ManifestStore(tmp_path)
    store.write(_make_manifest())
    content = (tmp_path / "manifests" / "JOB-123.json").read_text()
    assert '"job_id": "JOB-123"' in content


def test_read_roundtrip(tmp_path: Path) -> None:
    store = ManifestStore(tmp_path)
    m = _make_manifest()
    store.write(m)
    result = store.read("JOB-123")
    assert result is not None
    assert result.job_id == "JOB-123"
    assert result.message_count == 100
    assert result.guild_id == "g1"


def test_read_missing_returns_none(tmp_path: Path) -> None:
    store = ManifestStore(tmp_path)
    assert store.read("nonexistent") is None


def test_write_overwrites_existing(tmp_path: Path) -> None:
    store = ManifestStore(tmp_path)
    m1 = _make_manifest()
    m2 = _make_manifest()
    m2.message_count = 999
    store.write(m1)
    store.write(m2)
    result = store.read("JOB-123")
    assert result is not None
    assert result.message_count == 999
