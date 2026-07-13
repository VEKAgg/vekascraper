from __future__ import annotations

import json
import logging

from export_api.dependencies import verify_api_key
from fastapi import APIRouter, Depends, HTTPException, Request, status
from shared.models.job import Job, JobCreateRequest, JobState, JobType
from shared.models.status import CancelResponse, JobListResponse
from shared.storage.job_store import JobStore

logger = logging.getLogger(__name__)
router = APIRouter(dependencies=[Depends(verify_api_key)])


def _get_store(request: Request) -> JobStore:
    paths = request.app.state.paths
    return JobStore(paths.root)


@router.post("/messages", response_model=dict)
async def create_message_job(
    body: JobCreateRequest,
    request: Request,
) -> dict:
    store = _get_store(request)
    _reject_if_active(store, body.guild_id)
    job = store.create(JobType.MESSAGES, body.guild_id, body.params)
    _queue_job(job, store)
    return {"job_id": job.job_id, "type": job.type.value, "state": job.state.value}


@router.post("/members", response_model=dict)
async def create_member_job(
    body: JobCreateRequest,
    request: Request,
) -> dict:
    store = _get_store(request)
    _reject_if_active(store, body.guild_id)
    job = store.create(JobType.MEMBERS, body.guild_id, body.params)
    _queue_job(job, store)
    return {"job_id": job.job_id, "type": job.type.value, "state": job.state.value}


@router.post("/both", response_model=dict)
async def create_both_job(
    body: JobCreateRequest,
    request: Request,
) -> dict:
    store = _get_store(request)
    _reject_if_active(store, body.guild_id)

    first = store.create(JobType.MESSAGES, body.guild_id, body.params)
    _queue_job(first, store)

    second = store.create(
        JobType.MEMBERS, body.guild_id, body.params, chain_next=None
    )

    first.chain_next = second.job_id
    store.save(first)

    return {
        "job_id": first.job_id,
        "job_ids": [first.job_id, second.job_id],
        "type": "both",
        "state": first.state.value,
    }


@router.get("", response_model=JobListResponse)
async def list_jobs(request: Request) -> JobListResponse:
    store = _get_store(request)
    jobs = store.list_all()
    return JobListResponse(jobs=jobs, total=len(jobs))


@router.get("/{job_id}", response_model=Job)
async def get_job(job_id: str, request: Request) -> Job:
    store = _get_store(request)
    job = store.get(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.get("/{job_id}/logs")
async def get_job_logs(job_id: str, request: Request) -> list[dict]:
    from shared.storage.paths import DataPaths
    paths: DataPaths = request.app.state.paths
    log_path = paths.logs / f"{job_id}.log"
    if not log_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No logs found for this job",
        )
    entries: list[dict] = []
    with open(str(log_path), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


@router.post("/{job_id}/cancel", response_model=CancelResponse)
async def cancel_job(job_id: str, request: Request) -> CancelResponse:
    store = _get_store(request)
    job = store.get(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    if job.state in (JobState.COMPLETED, JobState.FAILED, JobState.CANCELLED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job in state {job.state.value}",
        )

    if job.state == JobState.QUEUED:
        job.transition(JobState.CANCELLED)
    elif job.state == JobState.RUNNING:
        job.transition(JobState.CANCELLING)
    else:
        job.transition(JobState.CANCELLED)

    store.save(job)
    return CancelResponse(
        job_id=job.job_id, state=job.state.value, message="Job cancelled"
    )


def _queue_job(job: Job, store: JobStore) -> None:
    job.transition(JobState.QUEUED)
    store.save(job)


def _reject_if_active(store: JobStore, guild_id: str) -> None:
    active = store.list_by_state(JobState.QUEUED, JobState.RUNNING, JobState.CANCELLING)
    for j in active:
        if j.guild_id == guild_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Active job {j.job_id} already exists for guild {guild_id}. "
                       "Cancel it first or wait for it to complete.",
            )
