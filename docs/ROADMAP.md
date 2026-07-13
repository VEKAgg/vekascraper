# Roadmap

## v1 (current)

- [x] Project scaffolding and repository structure
- [x] File-backed job queue and state management
- [x] Discord control bot with admin validation
- [x] Internal FastAPI for job orchestration
- [x] Worker contract and stub member extraction
- [x] Docker Compose orchestration
- [x] Documentation: architecture, setup, ops, security

## v1.1

- [ ] Implement DiscordChatExporter integration in message worker
- [ ] Implement pixelatedxp/discord-member-scraper in member worker
- [ ] Structured log viewer script
- [ ] Job retention and cleanup policy
- [ ] End-to-end smoke tests

## v2

- [ ] Webhook notifications on job completion (Discord webhook)
- [ ] Concurrent jobs with per-token rate limiting
- [ ] Prometheus metrics on API and workers
- [ ] Job scheduling (cron-like recurring extractions)
- [ ] Export compression and archiving

## v3

- [ ] Copycord failover worker
- [ ] Web UI for job inspection and manual export download
- [ ] Multi-token support for parallel extraction
- [ ] Export comparison/diff tooling

## Future / maybe

- Database-backed queue (PostgreSQL) for reliability at scale
- Kubernetes Helm chart
- Discord webhook export delivery
- SST (serverless) extraction workers
- S3-compatible export storage
