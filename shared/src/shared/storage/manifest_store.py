from __future__ import annotations

from pathlib import Path

from shared.models.manifest import Manifest
from shared.storage.paths import get_data_root


class ManifestStore:
    def __init__(self, data_root: Path | None = None) -> None:
        self._root = data_root or get_data_root()
        self._manifests_dir = self._root / "manifests"
        self._manifests_dir.mkdir(parents=True, exist_ok=True)

    def write(self, manifest: Manifest) -> Path:
        path = self._manifests_dir / f"{manifest.job_id}.json"
        path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
        return path

    def read(self, job_id: str) -> Manifest | None:
        path = self._manifests_dir / f"{job_id}.json"
        if not path.exists():
            return None
        return Manifest.model_validate_json(path.read_text(encoding="utf-8"))
