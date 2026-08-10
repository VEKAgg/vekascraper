from pathlib import Path

from shared.models.job import JobState, JobType
from shared.storage.job_store import JobStore


def test_list_by_type_messages(tmp_path: Path) -> None:
    store = JobStore(tmp_path)
    store.create(JobType.MESSAGES, "g1")
    store.create(JobType.MEMBERS, "g1")
    result = store.list_by_type(JobType.MESSAGES)
    assert len(result) == 1
    assert result[0].type == JobType.MESSAGES


def test_list_by_type_members(tmp_path: Path) -> None:
    store = JobStore(tmp_path)
    store.create(JobType.MEMBERS, "g1")
    store.create(JobType.MEMBERS, "g2")
    result = store.list_by_type(JobType.MEMBERS)
    assert len(result) == 2


def test_list_by_type_empty(tmp_path: Path) -> None:
    store = JobStore(tmp_path)
    result = store.list_by_type(JobType.MESSAGES)
    assert result == []


def test_list_all_skips_corrupt_json(tmp_path: Path) -> None:
    store = JobStore(tmp_path)
    store.create(JobType.MESSAGES, "g1")
    corrupt = tmp_path / "jobs" / "CORRUPT.json"
    corrupt.write_text("not valid json{{{{", encoding="utf-8")
    result = store.list_all()
    assert len(result) == 1


def test_write_atomic_no_corruption(tmp_path: Path) -> None:
    store = JobStore(tmp_path)
    job1 = store.create(JobType.MESSAGES, "g1")
    job1.transition(JobState.QUEUED)
    store.save(job1)
    job2 = store.create(JobType.MESSAGES, "g2")
    store.save(job2)
    assert store.get(job1.job_id).state == JobState.QUEUED
    assert store.get(job2.job_id).state == JobState.CREATED
