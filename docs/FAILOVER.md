# Failover: Copycord integration

## What is Copycord?

Copycord is an alternative Discord archiving tool that can serve as a fallback when primary extraction (DiscordChatExporter / member scraper) fails. It is **not implemented in v1** — this document describes how to integrate it later.

## Extension points

The system already has the hooks needed for Copycord integration:

### 1. New worker service

Create `services/copycord_worker/` with its own Dockerfile, following the same contract as existing workers:

- Poll `/data/jobs/` for jobs matching its type (e.g., `copycord_messages`)
- Claim jobs by setting state to RUNNING
- Execute Copycord with the job parameters
- Write logs to `/data/logs/{job_id}.log`
- Write manifests to `/data/manifests/{job_id}.json`
- Set state to COMPLETED or FAILED

### 2. New job type

The export API supports any job type string. Add `copycord_messages` and `copycord_members` as valid types. No API changes needed — the job store is type-agnostic.

### 3. Failover logic

When a primary worker fails a job (sets state to FAILED), a failover orchestrator can:

1. Create a new job with type `copycord_messages` using the same parameters
2. Set `chain_prev` to link back to the failed job
3. Let the Copycord worker pick it up

This orchestrator is not yet built. The `compose.yaml` has a commented-out `copycord-worker` service ready to be uncommented.

### 4. compose.yaml extension

```yaml
copycord-worker:
  build:
    context: .
    dockerfile: services/copycord_worker/Dockerfile
  volumes:
    - data:/data
  depends_on:
    export-api:
      condition: service_healthy
  env_file:
    - .env
  restart: unless-stopped
  profiles:
    - copycord
```

Use `docker compose --profile copycord up` to enable it.

## What keeps Copycord safe to add later?

- Workers are **pluggable** — they all follow the same file-based contract
- Job types are **arbitrary strings** — the API doesn't hardcode worker types
- The **separation of concerns** means Copycord never touches the bot or API logic
- Adding a worker never requires changing existing workers

## Integration steps

1. Create `services/copycord_worker/` with Copycord CLI wrapper
2. Add Copycord's dependencies to `shared/pyproject.toml` or the worker's own
3. Uncomment `copycord-worker` in `compose.yaml`
4. (Optional) Build the failover orchestrator that retries failed jobs as Copycord jobs
