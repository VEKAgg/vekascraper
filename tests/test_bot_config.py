import pytest
from controller_bot.config import BotConfig


def test_from_env_requires_discord_token(monkeypatch: object) -> None:
    monkeypatch.delenv("DISCORD_BOT_TOKEN", raising=False)  # type: ignore[attr-defined]
    monkeypatch.setenv("API_KEY", "key")  # type: ignore[attr-defined]
    with pytest.raises(RuntimeError):
        BotConfig.from_env()


def test_from_env_requires_api_key(monkeypatch: object) -> None:
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "token")  # type: ignore[attr-defined]
    monkeypatch.delenv("API_KEY", raising=False)  # type: ignore[attr-defined]
    with pytest.raises(RuntimeError):
        BotConfig.from_env()


def test_from_env_parses_admin_ids(monkeypatch: object) -> None:
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "token")  # type: ignore[attr-defined]
    monkeypatch.setenv("API_KEY", "key")  # type: ignore[attr-defined]
    monkeypatch.setenv("ADMIN_DISCORD_USER_IDS", "111,222,333")  # type: ignore[attr-defined]
    config = BotConfig.from_env()
    assert config.admin_user_ids == ["111", "222", "333"]


def test_from_env_empty_admin_ids(monkeypatch: object) -> None:
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "token")  # type: ignore[attr-defined]
    monkeypatch.setenv("API_KEY", "key")  # type: ignore[attr-defined]
    monkeypatch.setenv("ADMIN_DISCORD_USER_IDS", "")  # type: ignore[attr-defined]
    config = BotConfig.from_env()
    assert config.admin_user_ids == []


def test_from_env_defaults(monkeypatch: object) -> None:
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "token")  # type: ignore[attr-defined]
    monkeypatch.setenv("API_KEY", "key")  # type: ignore[attr-defined]
    config = BotConfig.from_env()
    assert config.export_api_url == "http://export-api:8080"
