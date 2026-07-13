# AGENTS.md — Instructions for coding agents

## Architecture constraints

- **Bot never extracts.** The controller-bot only routes commands to the API. Extraction lives in workers.
- **Workers never talk to Discord as a bot.** Workers use `DISCORD_USER_TOKEN` (not bot token). Bot uses `DISCORD_BOT_TOKEN` (not user token).
- **API validates via `X-API-Key` only.** It has no Discord token at all. `/health` is the sole unauthenticated endpoint.
- **File-backed v1.** No database, no message broker, no web UI. The filesystem under `/data/` (jobs/, logs/, exports/, manifests/, temp/) is the source of truth.
- **Copycord is future failover only.** Do not implement it. Leave commented compose entries as placeholders.
- **All secrets in env vars only.** Fail fast at startup if a required env var is missing.
- **Half-implemented unsafe features → `# TODO(vekascraper):` marker.** Don't leave untested security-sensitive code.

## Developer commands

```
pip install -e shared/  # install shared first, then services
pip install -e services/export_api/ -e services/controller_bot/ -e services/member_worker/ -e services/message_worker/

make lint       # ruff check services/ shared/ scripts/
make typecheck  # mypy services/ shared/ --pretty
make test       # pytest tests/ shared/src/shared/ services/*/tests/ -v --cov
make inspect JOB_ID=JOB-20260713-abc12  # cat a job file

pre-commit run --all-files  # ruff, ruff-format, trailing-whitespace, etc.

# Run individually (from repo root, after editable install):
python -m export_api        # uvicorn on 0.0.0.0:8080
python -m controller_bot    # discord.py bot
python -m member_worker     # polling worker (members)
python -m message_worker    # polling worker (messages)
```

All services need `.env` (see `.env.example`). Commands in `CONTRIBUTING.md` (`ruff check .`, `mypy .`) are slightly broader than Makefile targets — prefer Makefile targets.

## Known quirks

- **23 tests exist** in `tests/` (test_idgen, test_job_store, test_jobs_router). Pytest is configured in `pyproject.toml`.
- **`.dockerignore` exists.** Excludes `.git/`, `.venv/`, `data/`, `__pycache__/` from Docker build context.
- **Services communicate by HTTP (bot→API) and file polling (worker→/data/jobs/).** Workers claim jobs via atomic rename (`os.replace`).
- **API rejects duplicate guild jobs.** You cannot queue any job for a guild that has one QUEUED, RUNNING, or CANCELLING.
- **`/extract both` order:** MESSAGES first (QUEUED), MEMBERS second (stays CREATED). Chained: MEMBERS gets QUEUED when MESSAGES completes.
- **Job ID format:** `JOB-YYYYMMDD-XXXXX` (sortable, human-readable).
- **`shared/` is a pip-installable package.** All services depend on it via editable install (`-e`).
- **API endpoints:** 7 + health + logs. `GET /jobs/{job_id}/logs` returns parsed JSON-lines.

## Conventions

- Type hints everywhere (exempt `__init__.py`)
- Pydantic v2 models, `pathlib.Path` for filesystem ops
- Ruff: line-length=100, double quotes
- Mypy: strict mode
- Logging with `import logging` (no structlog used yet)

## Pre-submit checklist

- [ ] `make lint` — no new ruff errors
- [ ] `make typecheck` — no new mypy errors
- [ ] `make test` — all tests pass (write tests for new code)
- [ ] Docs updated if endpoints, commands, or architecture changed
- [ ] `compose.yaml` updated if new service added
- [ ] `.env.example` updated if new env var added
- [ ] AGENTS.md is still accurate
