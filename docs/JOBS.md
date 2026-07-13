# Jobs

## Lifecycle

```
CREATED ──▶ QUEUED ──▶ RUNNING ──▶ COMPLETED
                         └──▶ FAILED
QUEUED ──▶ CANCELLED
RUNNING ──▶ CANCELLING ──▶ CANCELLED
```

| State | Meaning |
|-------|---------|
| `CREATED` | Job has been accepted by the API |
| `QUEUED` | Job is ready for a worker to pick up |
| `RUNNING` | A worker has claimed the job and is executing it |
| `COMPLETED` | Extraction finished successfully |
| `FAILED` | Extraction finished with an error |
| `CANCELLING` | Cancel requested while running; worker should abort |
| `CANCELLED` | Job was cancelled before or during execution |

## Job schema

```json
{
  "job_id": "JOB-20260713-a3f8k",
  "type": "members",
  "state": "QUEUED",
  "guild_id": "123456789012345678",
  "params": {},
  "chain_next": null,
  "created_at": "2026-07-13T10:30:00Z",
  "updated_at": "2026-07-13T10:30:05Z",
  "error": null
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `job_id` | string | Unique, sortable ID: `JOB-YYYYMMDD-XXXXX` |
| `type` | enum | `messages`, `members`, or `both` |
| `state` | enum | Current lifecycle state |
| `guild_id` | string | Discord guild/server ID |
| `params` | object | Type-specific parameters (channel IDs, etc.) |
| `chain_next` | string/null | If part of a chain, the next job ID |
| `created_at` | string | ISO 8601 UTC timestamp |
| `updated_at` | string | ISO 8601 UTC timestamp of last change |
| `error` | string/null | Error message if FAILED |

## Manifest schema

Written to `/data/manifests/{job_id}.json` on completion.

```json
{
  "job_id": "JOB-20260713-a3f8k",
  "type": "members",
  "guild_id": "123456789012345678",
  "started_at": "2026-07-13T10:30:05Z",
  "completed_at": "2026-07-13T10:35:12Z",
  "duration_seconds": 307,
  "member_count": 142,
  "export_path": "/data/exports/members/JOB-20260713-a3f8k/",
  "checksum": "sha256:abc123..."
}
```

## API endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Health check |
| POST | `/jobs/messages` | API key | Create message-extraction job |
| POST | `/jobs/members` | API key | Create member-extraction job |
| POST | `/jobs/both` | API key | Create chained messages+members job plan |
| GET | `/jobs` | API key | List all jobs |
| GET | `/jobs/{job_id}` | API key | Get single job details |
| POST | `/jobs/{job_id}/cancel` | API key | Cancel a job |

## Cancellation

- **Queued jobs** are immediately set to `CANCELLED`.
- **Running jobs** are set to `CANCELLING`. Workers check this state and abort gracefully.
- **Completed or already-cancelled jobs** return an error.
