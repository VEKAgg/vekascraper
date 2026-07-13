# vekascraper

**Self-hosted Discord archive control system.**

A production-minded, Docker-based toolchain for extracting and archiving Discord server data — messages, members, and more — without a database, web UI, or unnecessary complexity.

## Architecture at a glance

```
Discord (slash commands)
       │
       ▼
┌─────────────────┐      ┌────────────────┐      ┌──────────────────┐
│ controller_bot  │─────▶│  export_api    │─────▶│  member_worker   │
│ (discord.py)    │      │  (FastAPI)     │      │  (poll+execute)  │
│                 │      │                │      │                  │
│ validates admin │      │ queues jobs    │      │ scrapes members  │
│ posts to API    │      │ manages state  │      │ writes manifests │
└─────────────────┘      └────────────────┘      └──────────────────┘
                                  │
                          ┌───────┴────────┐
                          │   /data (bind)  │
                          │ jobs / logs /   │
                          │ exports / temp  │
                          └────────────────┘
```

## Quick start

```bash
cp .env.example .env
# Fill in DISCORD_BOT_TOKEN, ADMIN_DISCORD_USER_IDS, API_KEY
docker compose up --build
```

## Repo layout

| Path | Purpose |
|------|---------|
| `services/controller_bot/` | Discord bot — validates admins, submits jobs |
| `services/export_api/` | FastAPI — job queue, state, cancellation |
| `services/member_worker/` | Extraction worker — polls for jobs, executes |
| `shared/` | Pydantic models, file storage, utility code |
| `data/` | Runtime data: jobs, logs, exports, temp |
| `docs/` | Architecture, setup, ops, security, roadmap |
| `scripts/` | Bootstrap, dev helpers, inspection |
| `compose.yaml` | Docker Compose orchestration |

## Project status

**v1 — Active development.** Stable foundation, no database, file-backed queue. Message extraction (DiscordChatExporter) is a planned service.

## License

MIT
