from __future__ import annotations

from pydantic import AwareDatetime, BaseModel


class Manifest(BaseModel):
    job_id: str
    type: str
    guild_id: str
    started_at: AwareDatetime
    completed_at: AwareDatetime
    duration_seconds: int
    member_count: int | None = None
    message_count: int | None = None
    channel_count: int | None = None
    export_path: str
    checksum: str | None = None
