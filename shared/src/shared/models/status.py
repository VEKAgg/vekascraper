from pydantic import BaseModel

from shared.models.job import Job


class CancelResponse(BaseModel):
    job_id: str
    state: str
    message: str


class JobListResponse(BaseModel):
    jobs: list[Job]
    total: int
