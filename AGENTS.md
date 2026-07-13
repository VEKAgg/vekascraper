# AGENTS.md — Instructions for coding agents

## Golden rules

1. **Preserve the separation.** The bot never performs extraction. The API never runs extraction. Workers never talk to Discord as a bot. These are hard boundaries.

2. **No extraction in the bot.** If you need to add a new extraction type, add a new worker service and a new API endpoint. Do not add extraction logic to the controller bot.

3. **Keep v1 file-backed and simple.** Do not introduce a database, message broker, or web UI unless explicitly requested. The file-backed store is intentional.

4. **Document every structural change.** If you add a new service, endpoint, or job type, update the relevant docs and add a note to DECISIONS.md.

5. **Update docs when endpoints or commands change.** ARCHITECTURE.md, JOBS.md, and any relevant service docs must be kept in sync.

6. **Prefer boring, maintainable code.** Favor standard library, simple patterns, and explicit code over clever abstractions. A function that does one thing with readable variable names is the goal.

7. **No database or frontend without explicit request.** Both are planned for future phases. Do not pre-emptively add them.

8. **Copycord is future failover only.** Do not implement Copycord. Leave room for it (commented compose service, documented extension points) but do not write Copycord integration code.

9. **All secrets in env vars only.** Never hardcode a token, API key, or credential. Validate that env vars are loaded at startup and fail fast if they are missing.

10. **Add TODO markers instead of half-implementing unsafe features.** If a feature would require security review, testing, or a design decision you are not equipped to make, leave a `# TODO(vekascraper):` comment and move on.

## Code conventions

- Use type hints everywhere sensible (`__init__` files are exempt)
- Prefer Pydantic v2 models for data validation
- Use `pathlib.Path` for filesystem operations
- Use `structlog` or `logging` with structured formatting
- Keep functions under 40 lines unless unavoidable
- One class per file unless they are tightly coupled
- Module names are lowercase with underscores
- Test files mirror source layout with `test_` prefix

## Pre-submit checklist

Before considering a change complete:

- [ ] Run `ruff check` — no new lint errors
- [ ] Run `mypy` — no new type errors
- [ ] Existing tests pass
- [ ] New code has tests for critical paths (state transitions, validation, edge cases)
- [ ] Docs updated if endpoints, commands, or architecture changed
- [ ] No tokens or secrets in code
- [ ] `compose.yaml` updated if new service added
- [ ] `.env.example` updated if new env var added
- [ ] AGENTS.md is not stale — rules should still hold
