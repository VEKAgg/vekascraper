from __future__ import annotations

import os
from typing import List


def get_env(key: str, default: str | None = None) -> str:
    value = os.environ.get(key)
    if value is None:
        if default is not None:
            return default
        raise RuntimeError(f"Required environment variable {key} is not set")
    return value


def get_env_int(key: str, default: int | None = None) -> int:
    value = os.environ.get(key)
    if value is None:
        if default is not None:
            return default
        raise RuntimeError(f"Required environment variable {key} is not set")
    return int(value)


def get_env_list(key: str, separator: str = ",", default: str | None = None) -> list[str]:
    value = os.environ.get(key)
    if value is None:
        if default is not None:
            return [s.strip() for s in default.split(separator) if s.strip()]
        return []
    return [s.strip() for s in value.split(separator) if s.strip()]
