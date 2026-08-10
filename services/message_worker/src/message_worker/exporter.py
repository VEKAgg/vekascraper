from __future__ import annotations

import json
import logging
import time
from pathlib import Path

import httpx
from message_worker.config import WorkerConfig
from shared.models.job import Job
from shared.storage.log_writer import LogWriter

logger = logging.getLogger(__name__)

DISCORD_API = "https://discord.com/api/v10"
MESSAGES_PER_PAGE = 100

TEXT_CHANNEL_TYPES = {0, 5, 15}


def _fetch_channels(token: str, guild_id: str) -> list[dict]:
    headers = {"Authorization": f"Bot {token}"}
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(
            f"{DISCORD_API}/guilds/{guild_id}/channels",
            headers=headers,
        )
        resp.raise_for_status()
        return [c for c in resp.json() if c.get("type") in TEXT_CHANNEL_TYPES]


def _fetch_messages(
    token: str, channel_id: str, log: LogWriter, job_id: str,
) -> list[dict]:
    messages: list[dict] = []
    before = None
    headers = {"Authorization": f"Bot {token}"}

    with httpx.Client(timeout=30.0) as client:
        while True:
            params: dict = {"limit": MESSAGES_PER_PAGE}
            if before:
                params["before"] = before

            resp = client.get(
                f"{DISCORD_API}/channels/{channel_id}/messages",
                headers=headers,
                params=params,
            )
            resp.raise_for_status()
            batch = resp.json()
            if not batch:
                break

            for msg in batch:
                author = msg.get("author", {})
                messages.append({
                    "id": msg.get("id"),
                    "type": msg.get("type"),
                    "content": msg.get("content", ""),
                    "timestamp": msg.get("timestamp"),
                    "edited_timestamp": msg.get("edited_timestamp"),
                    "author_id": author.get("id"),
                    "author_name": author.get("username"),
                    "author_bot": author.get("bot", False),
                    "pinned": msg.get("pinned", False),
                    "attachment_count": len(msg.get("attachments", [])),
                    "embed_count": len(msg.get("embeds", [])),
                    "mention_count": len(msg.get("mentions", [])),
                })

            before = batch[-1]["id"]
            if len(batch) < MESSAGES_PER_PAGE:
                break
            time.sleep(0.5)

    log.info(
        job_id,
        f"Fetched {len(messages)} messages from channel {channel_id}",
        extra={"channel_id": channel_id, "message_count": len(messages)},
    )
    return messages


def export_messages(job: Job, config: WorkerConfig, log: LogWriter) -> dict:
    export_dir = Path(config.data_root) / "exports" / "messages" / job.job_id
    export_dir.mkdir(parents=True, exist_ok=True)

    log.info(
        job.job_id,
        f"Starting message export for guild {job.guild_id}",
        extra={"export_path": str(export_dir)},
    )

    try:
        channels = _fetch_channels(config.discord_user_token, job.guild_id)
    except httpx.HTTPStatusError as exc:
        log.error(
            job.job_id,
            f"HTTP error fetching channels: {exc.response.status_code}",
            extra={"status_code": exc.response.status_code},
        )
        raise RuntimeError(
            f"Discord API error {exc.response.status_code}: {exc.response.text}"
        ) from exc
    except httpx.RequestError as exc:
        log.error(job.job_id, f"Network error: {exc}")
        raise RuntimeError(f"Network error: {exc}") from exc

    log.info(
        job.job_id,
        f"Found {len(channels)} text channels",
        extra={"channel_count": len(channels)},
    )

    total_messages = 0
    for ch in channels:
        channel_id = ch["id"]
        channel_name = ch.get("name", channel_id)
        try:
            messages = _fetch_messages(
                config.discord_user_token, channel_id, log, job.job_id,
            )
        except httpx.HTTPStatusError as exc:
            log.error(
                job.job_id,
                f"HTTP error fetching messages for {channel_name}: "
                f"{exc.response.status_code}",
            )
            continue
        except httpx.RequestError as exc:
            log.error(
                job.job_id,
                f"Network error fetching messages for {channel_name}: {exc}",
            )
            continue

        ch_path = export_dir / f"{channel_name}.json"
        ch_path.write_text(
            json.dumps(
                {
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "category": ch.get("parent_id"),
                    "topic": ch.get("topic"),
                    "message_count": len(messages),
                    "messages": messages,
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        total_messages += len(messages)

    channel_count = len(channels)
    log.info(
        job.job_id,
        f"Message export completed: {total_messages} messages in "
        f"{channel_count} channels",
        extra={
            "message_count": total_messages,
            "channel_count": channel_count,
            "export_path": str(export_dir),
        },
    )

    return {
        "export_path": str(export_dir),
        "message_count": total_messages,
        "duration_seconds": 0,
    }
