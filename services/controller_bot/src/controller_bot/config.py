from __future__ import annotations

from dataclasses import dataclass, field

from shared.utils.config import get_env, get_env_list


@dataclass(frozen=True)
class BotConfig:
    discord_token: str
    admin_user_ids: list[str] = field(default_factory=list)
    export_api_url: str = "http://localhost:8080"
    api_key: str = ""

    @classmethod
    def from_env(cls) -> BotConfig:
        return cls(
            discord_token=get_env("DISCORD_BOT_TOKEN"),
            admin_user_ids=get_env_list("ADMIN_DISCORD_USER_IDS"),
            export_api_url=get_env("EXPORT_API_URL", "http://export-api:8080"),
            api_key=get_env("API_KEY"),
        )
