
import pytest
from shared.models.job import _VALID_TRANSITIONS, Job, JobCreateRequest, JobState, JobType


def _make_job(state: JobState = JobState.CREATED) -> Job:
    return Job(job_id="JOB-123", type=JobType.MESSAGES, guild_id="g1", state=state)


class TestTransitionValid:
    def test_created_to_queued(self) -> None:
        job = _make_job(JobState.CREATED)
        job.transition(JobState.QUEUED)
        assert job.state == JobState.QUEUED

    def test_queued_to_running(self) -> None:
        job = _make_job(JobState.QUEUED)
        job.transition(JobState.RUNNING)
        assert job.state == JobState.RUNNING

    def test_running_to_completed(self) -> None:
        job = _make_job(JobState.RUNNING)
        job.transition(JobState.COMPLETED)
        assert job.state == JobState.COMPLETED

    def test_running_to_failed(self) -> None:
        job = _make_job(JobState.RUNNING)
        job.transition(JobState.FAILED)
        assert job.state == JobState.FAILED

    def test_running_to_cancelling(self) -> None:
        job = _make_job(JobState.RUNNING)
        job.transition(JobState.CANCELLING)
        assert job.state == JobState.CANCELLING

    def test_cancelling_to_cancelled(self) -> None:
        job = _make_job(JobState.CANCELLING)
        job.transition(JobState.CANCELLED)
        assert job.state == JobState.CANCELLED

    def test_queued_to_cancelled(self) -> None:
        job = _make_job(JobState.QUEUED)
        job.transition(JobState.CANCELLED)
        assert job.state == JobState.CANCELLED

    def test_created_to_cancelled(self) -> None:
        job = _make_job(JobState.CREATED)
        job.transition(JobState.CANCELLED)
        assert job.state == JobState.CANCELLED


class TestTransitionInvalid:
    def test_created_to_running(self) -> None:
        job = _make_job(JobState.CREATED)
        with pytest.raises(ValueError, match="Cannot transition"):
            job.transition(JobState.RUNNING)

    def test_completed_to_queued(self) -> None:
        job = _make_job(JobState.COMPLETED)
        with pytest.raises(ValueError):
            job.transition(JobState.QUEUED)

    def test_cancelled_to_any(self) -> None:
        job = _make_job(JobState.CANCELLED)
        with pytest.raises(ValueError):
            job.transition(JobState.RUNNING)

    def test_failed_to_running(self) -> None:
        job = _make_job(JobState.FAILED)
        with pytest.raises(ValueError):
            job.transition(JobState.RUNNING)

    def test_running_to_queued(self) -> None:
        job = _make_job(JobState.RUNNING)
        with pytest.raises(ValueError):
            job.transition(JobState.QUEUED)


class TestTransitionUpdatesTimestamp:
    def test_transition_updates_updated_at(self) -> None:
        job = _make_job()
        old = job.updated_at
        job.transition(JobState.QUEUED)
        assert job.updated_at >= old

    def test_touch_updates_updated_at(self) -> None:
        job = _make_job()
        old = job.updated_at
        job.touch()
        assert job.updated_at >= old


class TestJobDefaults:
    def test_defaults(self) -> None:
        job = Job(job_id="j1", type=JobType.MESSAGES, guild_id="g1")
        assert job.state == JobState.CREATED
        assert job.error is None
        assert job.chain_next is None
        assert job.params == {}


class TestJobCreateRequest:
    def test_defaults(self) -> None:
        req = JobCreateRequest(guild_id="g1")
        assert req.type == JobType.MESSAGES
        assert req.params == {}
        assert req.chain_next is None


class TestValidTransitions:
    def test_all_valid_pairs_exist(self) -> None:
        expected = {
            (JobState.CREATED, JobState.QUEUED),
            (JobState.CREATED, JobState.CANCELLED),
            (JobState.QUEUED, JobState.RUNNING),
            (JobState.QUEUED, JobState.CANCELLED),
            (JobState.RUNNING, JobState.COMPLETED),
            (JobState.RUNNING, JobState.FAILED),
            (JobState.RUNNING, JobState.CANCELLING),
            (JobState.CANCELLING, JobState.CANCELLED),
        }
        assert _VALID_TRANSITIONS == expected
