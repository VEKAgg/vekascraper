import pytest
from message_worker.config import WorkerConfig


def test_from_env_requires_discord_user_token(monkeypatch: object) -> None:
    monkeypatch.delenv("DISCORD_USER_TOKEN", raising=False)  # type: ignore[attr-defined]
    monkeypatch.setenv("API_KEY", "key")  # type: ignore[attr-defined]
    with pytest.raises(RuntimeError):
        WorkerConfig.from_env()


def test_from_env_defaults_worker_type_messages(monkeypatch: object) -> None:
    monkeypatch.setenv("DISCORD_USER_TOKEN", "token")  # type: ignore[attr-defined]
    monkeypatch.setenv("API_KEY", "key")  # type: ignore[attr-defined]
    config = WorkerConfig.from_env()
    assert config.worker_type == "messages"
