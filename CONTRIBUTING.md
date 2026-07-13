# Contributing

## Getting started

```bash
git clone <repo-url>
cd vekascraper
cp .env.example .env
python -m venv .venv
pip install -e shared/ -e services/export_api/ -e services/controller_bot/ -e services/member_worker/
```

## Development workflow

1. Make your changes
2. Run `ruff check .` to lint
3. Run `mypy .` to type-check
4. Run `pytest` to test
5. Update docs if you changed endpoints, commands, or architecture
6. Commit with a descriptive message

## Pull request guidelines

- One change per PR. If you're adding a feature and fixing a bug, split them.
- Keep the diff small. A 50-line PR is better than a 500-line PR.
- Update tests for any new or changed behavior.
- Update docs if user-facing behavior changes.
- Do not add dependencies without discussion. Every dependency is a maintenance burden.

## Code review

All PRs need at least one approval. Reviewers should check:

- Does this preserve the bot/API/worker boundary?
- Are env vars used for all secrets?
- Is the file-backed approach still appropriate, or does this change push toward needing a database?
- Are there TODO markers left for future work?
