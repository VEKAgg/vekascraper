from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class JobState(str, enum.Enum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"


class JobType(str, enum.Enum):
    MESSAGES = "messages"
    MEMBERS = "members"
    BOTH = "both"

    def to_worker_type(self) -> str:
        if self == JobType.MESSAGES:
            return "messages"
        if self == JobType.MEMBERS:
            return "members"
        return "both"


class JobCreateRequest(BaseModel):
    type: JobType
    guild_id: str
    params: dict[str, Any] = Field(default_factory=dict)
    chain_next: str | None = None


class Job(BaseModel):
    job_id: str
    type: JobType
    state: JobState = JobState.CREATED
    guild_id: str
    params: dict[str, Any] = Field(default_factory=dict)
    chain_next: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error: str | None = None

    def transition(self, new_state: JobState) -> Job:
        valid = _valid_transitions.get((self.state, new_state), False)
        if not valid:
            raise ValueError(
                f"Cannot transition from {self.state.value} to {new_state.value}"
            )
        self.state = new_state
        self.updated_at = datetime.now(timezone.utc)
        return self

    def touch(self) -> Job:
        self.updated_at = datetime.now(timezone.utc)
        return self


_valid_transitions: dict[tuple[JobState, JobState], bool] = {
    (JobState.CREATED, JobState.QUEUED): True,
    (JobState.CREATED, JobState.CANCELLED): True,
    (JobState.QUEUED, JobState.RUNNING): True,
    (JobState.QUEUED, JobState.CANCELLED): True,
    (JobState.RUNNING, JobState.COMPLETED): True,
    (JobState.RUNNING, JobState.FAILED): True,
    (JobState.RUNNING, JobState.CANCELLING): True,
    (JobState.CANCELLING, JobState.CANCELLED): True,
}
