# Operations

## Logs

### Container logs

```bash
# All services
docker compose logs -f

# Single service
docker compose logs -f export-api
docker compose logs -f controller-bot
docker compose logs -f member-worker
```

### Job logs

Each job writes structured JSON logs to `/data/logs/{job_id}.log`. These are append-only files with one JSON object per line.

```bash
# View a job's log
cat data/logs/JOB-20260713-abc12.log

# Filter by severity
grep '"severity":"error"' data/logs/JOB-20260713-abc12.log
```

## Restart strategy

All services are configured with `restart: unless-stopped` in `compose.yaml`. Docker will restart them automatically unless explicitly stopped with `docker compose stop`.

## Backup

The only persistent data is under `/data/`. Back up the entire directory:

```bash
tar czf vekascraper-backup-$(date +%Y%m%d).tar.gz /path/to/data/
```

### What to back up

| Path | Importance | Notes |
|------|------------|-------|
| `/data/jobs/` | High | Job state files. Losing these means losing active job tracking. |
| `/data/logs/` | Medium | Structured job logs. Useful for auditing and debugging. |
| `/data/manifests/` | High | Final extraction manifests. These are the primary output of the system. |
| `/data/exports/` | High | Extracted data (messages, members). The actual archives. |
| `/data/temp/` | Low | Temporary working directories. Not needed for backup. |

## Health checks

The export API has a health endpoint at `GET /health`. The controller bot and workers depend on it via Docker Compose health checks.

## Monitoring (v1)

In v1, monitoring is done through logs. There is no Prometheus integration yet.

## Disk space

Monitor disk usage under `/data/exports/` as it grows with each extraction job. Consider adding a retention policy (e.g., archive exports older than N days) in phase 2.

## Common tasks

```bash
# Restart all services
make restart

# View running state
docker compose ps

# Inspect a specific job
make inspect JOB_ID=JOB-20260713-abc12

# Open a shell in a container
docker compose exec export-api /bin/sh

# Clean everything (destroys volumes)
make clean
```
