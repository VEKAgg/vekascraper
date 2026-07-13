from __future__ import annotations

from dataclasses import dataclass

from shared.utils.config import get_env, get_env_int


@dataclass(frozen=True)
class APIConfig:
    api_key: str
    host: str = "0.0.0.0"
    port: int = 8080
    data_root: str = "/data"

    @classmethod
    def from_env(cls) -> APIConfig:
        return cls(
            api_key=get_env("API_KEY"),
            host=get_env("API_HOST", "0.0.0.0"),
            port=get_env_int("API_PORT", 8080),
            data_root=get_env("DATA_ROOT", "/data"),
        )
