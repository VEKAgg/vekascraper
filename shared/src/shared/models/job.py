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


class JobCreateRequest(BaseModel):
    type: JobType = JobType.MESSAGES
    guild_id: str
    params: dict[str, Any] = Field(default_factory=dict)
    chain_next: str | None = None


_VALID_TRANSITIONS: frozenset[tuple[JobState, JobState]] = frozenset({
    (JobState.CREATED, JobState.QUEUED),
    (JobState.CREATED, JobState.CANCELLED),
    (JobState.QUEUED, JobState.RUNNING),
    (JobState.QUEUED, JobState.CANCELLED),
    (JobState.RUNNING, JobState.COMPLETED),
    (JobState.RUNNING, JobState.FAILED),
    (JobState.RUNNING, JobState.CANCELLING),
    (JobState.CANCELLING, JobState.CANCELLED),
})


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
        if (self.state, new_state) not in _VALID_TRANSITIONS:
            raise ValueError(
                f"Cannot transition from {self.state.value} to {new_state.value}"
            )
        self.state = new_state
        self.updated_at = datetime.now(timezone.utc)
        return self

    def touch(self) -> Job:
        self.updated_at = datetime.now(timezone.utc)
        return self
