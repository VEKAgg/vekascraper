# Setup

## Prerequisites

- Docker & Docker Compose v2
- Python 3.12+ (for local development only)
- A Discord bot token with `applications.commands` scope
- A Discord user token (for extraction workers)
- Discord user IDs of admin accounts

## Quick start (Docker)

```bash
# 1. Clone and enter the repo
git clone <repo-url> vekascraper
cd vekascraper

# 2. Configure
cp .env.example .env
# Edit .env with your tokens and admin IDs

# 3. Start everything
docker compose up --build -d

# 4. Check logs
docker compose logs -f
```

## Configuration

All configuration is via environment variables in `.env`. See `.env.example` for the full list.

| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_BOT_TOKEN` | Yes | Discord bot token for the control bot |
| `ADMIN_DISCORD_USER_IDS` | Yes | Comma-separated Discord user IDs allowed to run commands |
| `API_KEY` | Yes | Shared secret between bot, API, and workers |
| `EXPORT_API_URL` | Yes | Internal URL of the export API |
| `DISCORD_USER_TOKEN` | Yes | Discord user token for extraction workers |
| `API_HOST` | No | API bind address (default: 0.0.0.0) |
| `API_PORT` | No | API listen port (default: 8080) |
| `DATA_ROOT` | No | Data directory (default: /data) |

## Local development

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Install shared package in editable mode
pip install -e shared/

# 3. Install service dependencies
pip install -e services/export_api/
pip install -e services/controller_bot/
pip install -e services/member_worker/

# 4. Run individual services
python -m export_api      # starts the API on localhost:8080
python -m controller_bot   # starts the bot
python -m member_worker    # starts the worker
```

Or use the dev script:

```bash
scripts/dev.sh
```

## Generating an API key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## First-run verification

```bash
# Check API health
curl http://localhost:8080/health

# Expected response: {"status": "ok", "service": "export-api"}
```
