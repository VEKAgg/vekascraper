from __future__ import annotations

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from shared.models.job import Job, JobState, JobType
from shared.storage.paths import get_data_root
from shared.utils.idgen import generate_job_id


class JobStore:
    def __init__(self, data_root: Path | None = None) -> None:
        self._root = data_root or get_data_root()
        self._jobs_dir = self._root / "jobs"
        self._jobs_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, job_id: str) -> Path:
        return self._jobs_dir / f"{job_id}.json"

    def create(self, type: JobType, guild_id: str, params: dict | None = None,
               chain_next: str | None = None) -> Job:
        job = Job(
            job_id=generate_job_id(),
            type=type,
            state=JobState.CREATED,
            guild_id=guild_id,
            params=params or {},
            chain_next=chain_next,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._write(job)
        return job

    def get(self, job_id: str) -> Job | None:
        path = self._path(job_id)
        if not path.exists():
            return None
        return Job.model_validate_json(path.read_text(encoding="utf-8"))

    def save(self, job: Job) -> None:
        self._write(job)

    def _write(self, job: Job) -> None:
        path = self._path(job.job_id)
        data = job.model_dump_json(indent=2, default=str)
        fd, tmp = tempfile.mkstemp(dir=str(self._jobs_dir), suffix=".tmp")
        try:
            with open(fd, "w", encoding="utf-8") as f:
                f.write(data)
            Path(tmp).rename(path)
        except Exception:
            Path(tmp).unlink(missing_ok=True)
            raise

    def list_all(self) -> List[Job]:
        jobs: list[Job] = []
        for p in sorted(self._jobs_dir.glob("*.json")):
            try:
                jobs.append(Job.model_validate_json(p.read_text(encoding="utf-8")))
            except Exception:
                continue
        return jobs

    def list_by_state(self, *states: JobState) -> List[Job]:
        return [j for j in self.list_all() if j.state in states]

    def list_by_type(self, type: JobType) -> List[Job]:
        return [j for j in self.list_all() if j.type == type]

    def claim_next(self, worker_type: str) -> Job | None:
        jobs = self.list_by_state(JobState.QUEUED)
        for job in jobs:
            if job.type.value == worker_type or (job.type == JobType.BOTH and worker_type in ("messages", "members")):
                job.transition(JobState.RUNNING)
                self._write(job)
                return job
        return None
