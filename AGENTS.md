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

## Agent workflow — audit, fix, commit, repeat

Every coding session must follow this loop for each task:

1. **Write the code** for the current task / step.
2. **Audit** — run `make lint`, `make typecheck`, `make test`. Fix any errors or warnings.
3. **Commit** — stage changes and commit with a descriptive message (e.g. `fix: swap both job creation order` or `feat: add message_worker service`).
4. **Push** — push the commit.
5. **Move on** — only start the next task after the current one is linted, tested, committed, and pushed.

Never batch multiple tasks into one commit. Each completed task = one clean commit.

## Pre-submit checklist

- [ ] `make lint` — no new ruff errors
- [ ] `make typecheck` — no new mypy errors
- [ ] `make test` — all tests pass (write tests for new code)
- [ ] Docs updated if endpoints, commands, or architecture changed
- [ ] `compose.yaml` updated if new service added
- [ ] `.env.example` updated if new env var added
- [ ] AGENTS.md is still accurate

---

## Known gaps, bugs & required fixes (post-audit 2026-08-10)

All items below are **actionable instructions for the next coding agent**. Address in the priority order shown in the table at the bottom. Mark `[x]` when resolved.

---

### ✅ Completed fixes (2026-08-10 session)

| ID | Status | File |
|---|---|---|
| FIX-1 | ✅ Done | `jobs.py` — `/both` order: MESSAGES first, MEMBERS second |
| FIX-4 | ✅ Done | `jobs.py` — second job stays CREATED |
| FIX-BUG5 | ✅ Done | `dependencies.py` — `hmac.compare_digest` for constant-time API key check |
| FIX-REL2 | ✅ Done | `job.py` — removed dead `JobType.BOTH` variant |
| FIX-REL4 | ✅ Done | Both `worker.py` — narrow exception catch (`KeyboardInterrupt` re-raised) |
| FIX-REL5 | ✅ Done | Both `worker.py` — `_execute_job` and helpers typed as `Job`, not `object` |
| FIX-SEC1 | ✅ Done | `config.py` — API key masked in `__repr__` |
| FIX-SEC3 | ✅ Done | `app.py` — removed `CORSMiddleware` |
| FIX-DQ2 | ✅ Done | `job.py` — `_VALID_TRANSITIONS` uses `frozenset` |
| FIX-DQ3 | ✅ Done | `bot.py` — removed dead `if config.discord_token` guard |
| FIX-DQ4 | ✅ Done | `manifest.py` — uses `AwareDatetime` |
| FIX-DQ5 | ✅ Done | `bot.py` — warns on empty `ADMIN_DISCORD_USER_IDS` |
| FIX-DQ6 | ✅ Done | `status.py` — deleted unused `StatusResponse` |
| FIX-DQ7 | ✅ Done | `admin.py` — `/status` shows sorted jobs with state emoji, capped at 15 |
| FIX-DQ8 | ✅ Done | `admin.py` — shared `httpx.AsyncClient` with `cog_unload` cleanup |
| GAP-1 | ✅ Done | `services/message_worker/` created |
| GAP-2 | ✅ Done | Orphaned empty dirs deleted |
| GAP-3 | ✅ Done | `.dockerignore` created |
| GAP-4 | ✅ Done | `data/` subdirectory `.gitkeep` files added |
| Tests | ✅ Done | 23 tests (test_idgen, test_job_store, test_jobs_router) |
| FIX-BUG3 | ✅ Done | Both `worker.py` — `_check_cancelled` + `_finish_cancelled` implemented |

---

### 🔴 MUST FIX — correctness bugs

#### FIX-BUG2 — `claim_next()` is not atomic — architecture vs implementation gap
**File:** `shared/src/shared/storage/job_store.py` — `claim_next()`
**Problem:** The stated architecture says workers "claim via atomic file renames." The actual code does read-all-QUEUED → pick one → write-RUNNING — a non-atomic read-modify-write with a TOCTOU race window.
**v1 mitigation:** Single-worker-per-type assumption (one member_worker, one message_worker). Acceptable for v1.
**v2 upgrade path:** Either POSIX directory rename pattern (`queued/` → `processing/`) or SQLite `UPDATE ... WHERE status='QUEUED' LIMIT 1 RETURNING *`.

#### FIX-REL1 — Worker starts with empty DISCORD_USER_TOKEN (no fast-fail)
**File:** `services/member_worker/src/member_worker/config.py` L21
**Problem:** `get_env("DISCORD_USER_TOKEN", "")` defaults to empty string. Worker boots without a token and fails silently only when the scraper authenticates.
**Fix:** `discord_user_token=get_env("DISCORD_USER_TOKEN")` — no default, raises RuntimeError at startup.

---

### 🟡 SECURITY limitations (documented, v2 fix)

#### FIX-SEC2 — No guild_id ownership validation
Any admin can submit a job for any `guild_id`, even guilds the bot is not in.
**v2 fix:** Bot validates `guild_id` against `bot.guilds`; API optionally checks `ALLOWED_GUILD_IDS` env var.

#### FIX-SEC4 — Token isolation is logical, not enforced
All services share one `.env` file in `compose.yaml`, so every service has access to all tokens.
**v2 fix:** Split into per-service env files (`.env.bot`, `.env.api`, `.env.worker`) and update `compose.yaml` `env_file:` per service.

---

### 📋 Fix priority order

| Priority | ID | File | Effort | Status |
|---|---|---|---|---|
| 1 | FIX-1 | `jobs.py` — swap chain order | 2 lines | ✅ Done |
| 2 | FIX-4 | `jobs.py` — remove `_queue_job` on second job | 1 line | ✅ Done |
| 3 | FIX-BUG5 | `dependencies.py` — `hmac.compare_digest` | 3 lines | ✅ Done |
| 4 | FIX-REL1 | `member_worker/config.py` — remove empty default | 1 line | ⬜ Pending |
| 5 | FIX-DQ5 | `bot.py` — warn on empty admin list | 3 lines | ✅ Done |
| 6 | FIX-DQ8 | `admin.py` — shared `httpx.AsyncClient` | ~20 lines | ✅ Done |
| 7 | FIX-DQ2 | `job.py` — frozenset transitions | ~15 lines | ✅ Done |
| 8 | FIX-REL2 | `job.py` — remove `JobType.BOTH` | ~10 lines | ✅ Done |
| 9 | FIX-REL4 | `worker.py` — narrow exception catch | 5 lines | ✅ Done |
| 10 | FIX-REL5 | `worker.py` — type `_execute_job` correctly | ~5 lines | ✅ Done |
| 11 | FIX-DQ3 | `bot.py` — remove dead if-token guard | 3 lines | ✅ Done |
| 12 | FIX-DQ4 | `manifest.py` — `AwareDatetime` | 3 lines | ✅ Done |
| 13 | FIX-DQ7 | `admin.py` + `jobs.py` — /status emoji + sort | ~30 lines | ✅ Done |
| 14 | FIX-SEC1 | `config.py` — mask API key in `__repr__` | 5 lines | ✅ Done |
| 15 | FIX-SEC3 | `app.py` — remove `CORSMiddleware` | 5 lines | ✅ Done |
| 16 | FIX-DQ6 | `status.py` — delete unused `StatusResponse` | varies | ✅ Done |
| 17 | GAP-1 | Create `services/message_worker/` | large | ✅ Done |
| 18 | GAP-2 | Delete orphaned empty dirs | trivial | ✅ Done |
| 19 | GAP-3 | Create `.dockerignore` | trivial | ✅ Done |
| 20 | GAP-4 | Add `data/` subdirectory `.gitkeep` files | trivial | ✅ Done |
| 21 | Tests | Write starter tests | medium | ✅ Done |
| 22 | FIX-BUG2 | `job_store.py` — atomic claim via dir rename | medium (v2) | ⬜ Deferred |
| 23 | FIX-BUG3 | `worker.py` — poll CANCELLING during exec | medium (after stub removed) | ✅ Done |
| 24 | FIX-SEC4 | Per-service env files in compose | medium (v2) | ⬜ Deferred |
| 25 | FIX-SEC2 | guild_id ownership validation | medium (v2) | ⬜ Deferred |
