from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from shared.storage.paths import get_data_root


class LogWriter:
    def __init__(self, data_root: Path | None = None) -> None:
        self._root = data_root or get_data_root()
        self._logs_dir = self._root / "logs"
        self._logs_dir.mkdir(parents=True, exist_ok=True)

    def write(self, job_id: str, severity: str, message: str,
              extra: dict | None = None) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "job_id": job_id,
            "severity": severity,
            "message": message,
        }
        if extra:
            entry["extra"] = extra
        path = self._logs_dir / f"{job_id}.log"
        with open(str(path), "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def info(self, job_id: str, message: str, extra: dict | None = None) -> None:
        self.write(job_id, "info", message, extra)

    def error(self, job_id: str, message: str, extra: dict | None = None) -> None:
        self.write(job_id, "error", message, extra)

    def warning(self, job_id: str, message: str, extra: dict | None = None) -> None:
        self.write(job_id, "warning", message, extra)
