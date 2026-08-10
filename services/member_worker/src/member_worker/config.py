from __future__ import annotations

from dataclasses import dataclass

from shared.utils.config import get_env, get_env_int


@dataclass(frozen=True)
class WorkerConfig:
    discord_user_token: str
    worker_type: str = "members"
    export_api_url: str = "http://export-api:8080"
    api_key: str = ""
    poll_interval: int = 10
    data_root: str = "/data"

    @classmethod
    def from_env(cls) -> WorkerConfig:
        return cls(
            discord_user_token=get_env("DISCORD_USER_TOKEN"),
            worker_type=get_env("WORKER_TYPE", "members"),
            export_api_url=get_env("EXPORT_API_URL", "http://export-api:8080"),
            api_key=get_env("API_KEY"),
            poll_interval=get_env_int("POLL_INTERVAL", 10),
            data_root=get_env("DATA_ROOT", "/data"),
        )
