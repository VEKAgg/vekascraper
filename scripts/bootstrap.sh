#!/usr/bin/env bash
set -euo pipefail

echo "=== vekascraper Bootstrap ==="

# Copy .env if not present
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example — edit it with your tokens."
fi

# Create data directories
mkdir -p data/{jobs,logs,manifests,exports/{messages,members},temp}

# Create Python venv if not present
if [ ! -d .venv ]; then
    python3 -m venv .venv
    echo "Created Python virtual environment at .venv"
fi

# Activate and install
source .venv/bin/activate
pip install --upgrade pip
pip install -e shared/
pip install -e services/export_api/
pip install -e services/controller_bot/
pip install -e services/member_worker/

echo "=== Bootstrap complete ==="
echo "Activate: source .venv/bin/activate"
echo "Start:    docker compose up --build"
