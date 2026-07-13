from __future__ import annotations

import secrets
from datetime import datetime, timezone


def generate_job_id() -> str:
    now = datetime.now(timezone.utc)
    date_part = now.strftime("%Y%m%d")
    random_part = "".join(secrets.choice("abcdefghjkmnpqrstuvwxyz23456789") for _ in range(5))
    return f"JOB-{date_part}-{random_part}"
