from pydantic import BaseModel

from shared.models.job import Job


class StatusResponse(BaseModel):
    active_jobs: list[Job]
    queued_jobs: list[Job]
    completed_today: int


class CancelResponse(BaseModel):
    job_id: str
    state: str
    message: str


class JobListResponse(BaseModel):
    jobs: list[Job]
    total: int
