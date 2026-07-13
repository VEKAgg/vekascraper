from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DataPaths:
    root: Path
    jobs: Path
    logs: Path
    manifests: Path
    exports_messages: Path
    exports_members: Path
    temp: Path


def get_data_root() -> Path:
    return Path(os.environ.get("DATA_ROOT", "/data")).resolve()


def ensure_dirs() -> DataPaths:
    root = get_data_root()
    paths = DataPaths(
        root=root,
        jobs=root / "jobs",
        logs=root / "logs",
        manifests=root / "manifests",
        exports_messages=root / "exports" / "messages",
        exports_members=root / "exports" / "members",
        temp=root / "temp",
    )
    for dir_path in [paths.jobs, paths.logs, paths.manifests,
                     paths.exports_messages, paths.exports_members, paths.temp]:
        dir_path.mkdir(parents=True, exist_ok=True)
    return paths
