# Security

## Environment variables

All secrets live in environment variables only — never in code, config files, or the filesystem.

| Variable | Risk if leaked |
|----------|---------------|
| `DISCORD_BOT_TOKEN` | Attacker controls the bot, can read messages in accessible channels |
| `DISCORD_USER_TOKEN` | Attacker has full access to the Discord user account |
| `API_KEY` | Attacker can create, cancel, and inspect extraction jobs |

**Never commit `.env` to version control.** The `.env.example` file contains placeholder values only.

## Token handling

### Separation of concerns

- The **controller bot** only knows `DISCORD_BOT_TOKEN`. It has no access to the user token.
- Workers only know `DISCORD_USER_TOKEN`. They have no access to the bot token.
- The API knows neither. It validates requests via `X-API-Key` header.

This means a compromise of any single component does not expose all credentials.

## Admin validation

The bot checks command author IDs against `ADMIN_DISCORD_USER_IDS` (a comma-separated env var). Only listed users can create or cancel jobs. There is no role-based check — this is intentional to keep v1 simple and auditable.

## Internal API protection

The export API listens on an internal Docker network. The bot and workers reach it by container name (`http://export-api:8080`). In `compose.yaml`, the API port is bound to `127.0.0.1:8080` — only localhost can reach it from the host machine.

All job endpoints require the `X-API-Key` header matching `API_KEY`. The `/health` endpoint is unauthenticated.

## Least privilege

- Bot: read message history, view channels, use slash commands — nothing else
- API: read/write `/data/` only
- Workers: read `/data/jobs/`, write `/data/logs/`, write `/data/exports/`, write `/data/manifests/`
- Containers run as non-root where possible

## Network

All inter-service communication is over HTTP inside the Docker internal network. The API is not exposed to the internet by default.

## Data at rest

Extracted Discord data (messages, member lists) is stored unencrypted on disk in `/data/exports/`. Protect this directory at the filesystem level. For production, consider encrypting the Docker volume.

## Future improvements

- Mutual TLS between services
- Signed job manifests
- Audit log of all API requests
- Per-guild rate limiting
