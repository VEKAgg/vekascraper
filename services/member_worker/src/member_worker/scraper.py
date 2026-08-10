from __future__ import annotations

import json
import logging
import time
from pathlib import Path

import httpx
from member_worker.config import WorkerConfig
from shared.models.job import Job
from shared.storage.log_writer import LogWriter

logger = logging.getLogger(__name__)

DISCORD_API = "https://discord.com/api/v10"
MEMBERS_PER_PAGE = 1000


def _fetch_members_http(
    token: str, guild_id: str, log: LogWriter, job_id: str,
) -> list[dict]:
    members: list[dict] = []
    after = "0"
    headers = {"Authorization": f"Bot {token}"}

    with httpx.Client(timeout=30.0) as client:
        while True:
            resp = client.get(
                f"{DISCORD_API}/guilds/{guild_id}/members",
                headers=headers,
                params={"limit": MEMBERS_PER_PAGE, "after": after},
            )
            resp.raise_for_status()
            batch = resp.json()
            if not batch:
                break

            for m in batch:
                user = m.get("user", {})
                members.append({
                    "id": user.get("id"),
                    "username": user.get("username"),
                    "discriminator": user.get("discriminator", "0"),
                    "global_name": user.get("global_name"),
                    "avatar": user.get("avatar"),
                    "bot": user.get("bot", False),
                    "roles": m.get("roles", []),
                    "joined_at": m.get("joined_at"),
                    "nick": m.get("nick"),
                    "premium_since": m.get("premium_since"),
                })

            log.info(
                job_id,
                f"Fetched {len(batch)} members (total: {len(members)})",
                extra={"batch_size": len(batch), "total": len(members)},
            )

            after = batch[-1]["user"]["id"]
            if len(batch) < MEMBERS_PER_PAGE:
                break
            time.sleep(0.5)

    return members


def scrape_members(job: Job, config: WorkerConfig, log: LogWriter) -> dict:
    export_dir = Path(config.data_root) / "exports" / "members" / job.job_id
    export_dir.mkdir(parents=True, exist_ok=True)

    log.info(
        job.job_id,
        f"Starting member scrape for guild {job.guild_id}",
        extra={"export_path": str(export_dir)},
    )

    try:
        members = _fetch_members_http(
            config.discord_user_token, job.guild_id, log, job.job_id,
        )
    except httpx.HTTPStatusError as exc:
        log.error(
            job.job_id,
            f"HTTP error fetching members: {exc.response.status_code}",
            extra={"status_code": exc.response.status_code},
        )
        raise RuntimeError(
            f"Discord API error {exc.response.status_code}: {exc.response.text}"
        ) from exc
    except httpx.RequestError as exc:
        log.error(job.job_id, f"Network error: {exc}")
        raise RuntimeError(f"Network error: {exc}") from exc

    result_path = export_dir / "members.json"
    result_path.write_text(
        json.dumps(
            {"guild_id": job.guild_id, "members": members},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    member_count = len(members)
    log.info(
        job.job_id,
        f"Member scrape completed: {member_count} members",
        extra={"member_count": member_count, "export_path": str(export_dir)},
    )

    return {
        "export_path": str(export_dir),
        "member_count": member_count,
        "duration_seconds": 0,
    }
