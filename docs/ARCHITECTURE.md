# Architecture

## Two-plane design

vekascraper separates the system into two distinct planes:

### Control plane

The control plane handles user interaction, validation, and orchestration. It never performs extraction.

| Component | Role |
|-----------|------|
| **controller-bot** | Discord bot that validates admin users via slash commands and submits job requests to the export API |
| **export-api** | FastAPI service that queues jobs, tracks state, handles cancellation, and serves job data to workers |

### Extraction plane

The extraction plane does the actual data-gathering work. Workers are stateless, poll-based, and single-purpose.

| Component | Role |
|-----------|------|
| **member-worker** | Polls the job queue for member-extraction jobs, executes against Discord, writes manifests |
| **message-worker** (planned) | Polls the job queue for message-extraction jobs using DiscordChatExporter |
| **copycord-worker** (future) | Failover extraction using Copycord when primary extraction fails |

## Communication flow

1. User runs `/extract messages` in Discord
2. Bot validates user ID against `ADMIN_DISCORD_USER_IDS` env var
3. Bot POSTs to `export-api:8080/jobs/messages` with `X-API-Key`
4. API creates job file at `/data/jobs/{job_id}.json`, returns `job_id`
5. Worker polls `/data/jobs/`, sees new QUEUED job matching its type
6. Worker atomically sets job to RUNNING, executes extraction
7. Worker writes structured logs to `/data/logs/{job_id}.log`
8. Worker writes manifest to `/data/manifests/{job_id}.json`
9. Worker sets job to COMPLETED or FAILED

## Data flow

```
Bot ─POST─▶ API ─write──▶ /data/jobs/{id}.json
                              ▲
Worker ─poll──────────────────┘
Worker ─write──▶ /data/logs/{id}.log
Worker ─write──▶ /data/exports/{type}/{id}/
Worker ─write──▶ /data/manifests/{id}.json
```

## Why file-backed?

- Zero infrastructure dependencies (no PostgreSQL, no Redis)
- Simple to debug: every job is a JSON file you can read with `cat`
- Easy to back up: `tar czf backup.tar.gz /data`
- Transparent: job states are filesystem states
- Sufficient for v1 where job throughput is low (human-paced)

## Container boundaries

Each service runs in its own container. The bot has no access to Discord user tokens. Workers have no access to the Discord bot token. The API has access to neither — it validates via `X-API-Key` only.

## Extension model

Adding a new worker type requires:
1. Create a new service under `services/<name>/`
2. Implement the worker contract (poll loop, claim, execute, report)
3. Add the service to `compose.yaml`
4. Add a new API endpoint if the job type needs extra parameters
