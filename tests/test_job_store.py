from pathlib import Path

from shared.models.job import JobState, JobType
from shared.storage.job_store import JobStore


def test_create_and_get(tmp_path: Path) -> None:
    store = JobStore(tmp_path)
    job = store.create(JobType.MESSAGES, "guild_123", {"channel": "general"})
    assert job.job_id.startswith("JOB-")
    assert job.type == JobType.MESSAGES
    assert job.guild_id == "guild_123"
    assert job.state == JobState.CREATED

    retrieved = store.get(job.job_id)
    assert retrieved is not None
    assert retrieved.job_id == job.job_id
    assert retrieved.type == job.type
    assert retrieved.params == {"channel": "general"}


def test_get_missing(tmp_path: Path) -> None:
    store = JobStore(tmp_path)
    assert store.get("JOB-20991231-nonexistent") is None


def test_save(tmp_path: Path) -> None:
    store = JobStore(tmp_path)
    job = store.create(JobType.MEMBERS, "guild_456")
    job.transition(JobState.QUEUED)
    store.save(job)

    retrieved = store.get(job.job_id)
    assert retrieved is not None
    assert retrieved.state == JobState.QUEUED


def test_list_all(tmp_path: Path) -> None:
    store = JobStore(tmp_path)
    j1 = store.create(JobType.MESSAGES, "guild_a")
    j2 = store.create(JobType.MEMBERS, "guild_b")

    all_jobs = store.list_all()
    ids = {j.job_id for j in all_jobs}
    assert j1.job_id in ids
    assert j2.job_id in ids


def test_list_by_state(tmp_path: Path) -> None:
    store = JobStore(tmp_path)
    j1 = store.create(JobType.MESSAGES, "guild_a")
    j2 = store.create(JobType.MEMBERS, "guild_b")
    j2.transition(JobState.QUEUED)
    store.save(j2)

    queued = store.list_by_state(JobState.QUEUED)
    assert len(queued) == 1
    assert queued[0].job_id == j2.job_id

    created = store.list_by_state(JobState.CREATED)
    assert len(created) == 1
    assert created[0].job_id == j1.job_id


def test_claim_next(tmp_path: Path) -> None:
    store = JobStore(tmp_path)
    job = store.create(JobType.MEMBERS, "guild_x")
    job.transition(JobState.QUEUED)
    store.save(job)

    claimed = store.claim_next("members")
    assert claimed is not None
    assert claimed.job_id == job.job_id
    assert claimed.state == JobState.RUNNING


def test_claim_next_ignores_wrong_type(tmp_path: Path) -> None:
    store = JobStore(tmp_path)
    job = store.create(JobType.MESSAGES, "guild_x")
    job.transition(JobState.QUEUED)
    store.save(job)

    claimed = store.claim_next("members")
    assert claimed is None


def test_claim_next_none_available(tmp_path: Path) -> None:
    store = JobStore(tmp_path)
    store.create(JobType.MEMBERS, "guild_x")
    claimed = store.claim_next("members")
    assert claimed is None
