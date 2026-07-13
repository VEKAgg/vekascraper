import re

from shared.utils.idgen import generate_job_id


def test_format() -> None:
    job_id = generate_job_id()
    assert re.match(r"^JOB-\d{8}-[a-hjkmnpqrstuvwxyz23456789]{5}$", job_id)


def test_unique() -> None:
    ids = {generate_job_id() for _ in range(100)}
    assert len(ids) == 100


def test_sortable() -> None:
    ids = sorted(generate_job_id() for _ in range(10))
    assert ids == sorted(ids)
