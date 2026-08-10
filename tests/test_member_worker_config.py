import pytest
from member_worker.config import WorkerConfig


def test_from_env_requires_discord_user_token(monkeypatch: object) -> None:
    monkeypatch.delenv("DISCORD_USER_TOKEN", raising=False)  # type: ignore[attr-defined]
    monkeypatch.setenv("API_KEY", "key")  # type: ignore[attr-defined]
    with pytest.raises(RuntimeError):
        WorkerConfig.from_env()


def test_from_env_requires_api_key(monkeypatch: object) -> None:
    monkeypatch.setenv("DISCORD_USER_TOKEN", "token")  # type: ignore[attr-defined]
    monkeypatch.delenv("API_KEY", raising=False)  # type: ignore[attr-defined]
    with pytest.raises(RuntimeError):
        WorkerConfig.from_env()


def test_from_env_defaults(monkeypatch: object) -> None:
    monkeypatch.setenv("DISCORD_USER_TOKEN", "token")  # type: ignore[attr-defined]
    monkeypatch.setenv("API_KEY", "key")  # type: ignore[attr-defined]
    config = WorkerConfig.from_env()
    assert config.worker_type == "members"
    assert config.poll_interval == 10
    assert config.data_root == "/data"


def test_from_env_custom_values(monkeypatch: object) -> None:
    monkeypatch.setenv("DISCORD_USER_TOKEN", "token")  # type: ignore[attr-defined]
    monkeypatch.setenv("API_KEY", "key")  # type: ignore[attr-defined]
    monkeypatch.setenv("WORKER_TYPE", "custom")  # type: ignore[attr-defined]
    monkeypatch.setenv("POLL_INTERVAL", "30")  # type: ignore[attr-defined]
    monkeypatch.setenv("DATA_ROOT", "/custom")  # type: ignore[attr-defined]
    config = WorkerConfig.from_env()
    assert config.worker_type == "custom"
    assert config.poll_interval == 30
    assert config.data_root == "/custom"
