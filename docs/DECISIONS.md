# Engineering decisions

## Why file-backed instead of a database?

**Decision:** File-based queue and state storage (JSON files in `/data/`).

**Rationale:** v1 has low throughput (human-paced Discord commands). A database adds operational overhead (PostgreSQL container, migrations, connection management). JSON files are debuggable with `cat`, backup-friendly, and zero-infrastructure. If throughput grows, switching to SQLite or PostgreSQL later requires changing only the `shared/storage/` layer.

## Why admin by env var whitelist instead of Discord role checks?

**Decision:** `ADMIN_DISCORD_USER_IDS` comma-separated env var.

**Rationale:** Discord permission checks require server member cache and are racy with role changes. An env var is explicit, auditable, and works the same way in every guild. Trade-off: it requires updating the env var and restarting when adding admins.

## Why JOB-YYYYMMDD-XXXXX for job IDs?

**Decision:** Timestamp-prefixed, human-readable, sortable.

**Rationale:** UUIDs are not human-friendly for debugging. Simple incrementing counters are fragile across restarts. The chosen format sorts chronologically by default, includes a random suffix for uniqueness, and is easy to type and grep.

## Why a shared pip-installable package instead of copy-pasting?

**Decision:** `shared/` is a pip-installable package (`-e shared/`).

**Rationale:** Job models, storage helpers, and utilities are used by every service. A shared package enforces a single source of truth. Each service declares `shared` as a dependency in its own `pyproject.toml`.

## Why separate pyproject.toml per service?

**Decision:** Each service has its own `pyproject.toml`.

**Rationale:** Services should be independently deployable and testable. A single monolith `pyproject.toml` would blur boundaries and make it harder to extract a service later. The root `pyproject.toml` contains only tooling config (ruff, mypy, pytest).

## Why worker polling instead of push/queue?

**Decision:** Workers poll the filesystem for jobs.

**Rationale:** No message broker needed. Filesystem atomic renames (`write temp → rename`) are a well-known pattern for reliable job claiming. Push-based systems (Redis pub/sub, RabbitMQ) add infrastructure that v1 doesn't need.

## Why no web UI in v1?

**Decision:** No frontend.

**Rationale:** A web UI is a separate product with its own security model, auth, and maintenance burden. v1 focuses on the CLI/Docker operational model. The API is the frontend for now.

## Why Copycord as failover instead of primary?

**Decision:** Copycord is a fallback, not the primary extraction method.

**Rationale:** DiscordChatExporter is more mature, more widely used, and produces cleaner output. Copycord exists as insurance — if DCE fails on a particular server or export, Copycord can be tried as an alternative.
