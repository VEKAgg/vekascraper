#!/usr/bin/env bash
set -euo pipefail

echo "=== vekascraper Dev ==="
echo "Starting all services locally (requires .env configured)"

# Ensure data dirs exist
mkdir -p data/{jobs,logs,manifests,exports/{messages,members},temp}

# Start export API in background
echo "Starting export-api on http://localhost:8080"
PYTHONPATH=$(pwd)/shared/src:$(pwd)/services/export_api/src \
    python -m export_api &
API_PID=$!
sleep 2

# Start controller bot
echo "Starting controller-bot"
PYTHONPATH=$(pwd)/shared/src:$(pwd)/services/controller_bot/src \
    python -m controller_bot &
BOT_PID=$!

# Start member worker
echo "Starting member-worker"
PYTHONPATH=$(pwd)/shared/src:$(pwd)/services/member_worker/src \
    python -m member_worker &
WORKER_PID=$!

# Start message worker
echo "Starting message-worker"
PYTHONPATH=$(pwd)/shared/src:$(pwd)/services/message_worker/src \
    python -m message_worker &
MESSAGE_WORKER_PID=$!

echo "=== All services started ==="
echo "API PID:    $API_PID"
echo "Bot PID:    $BOT_PID"
echo "Worker PID: $WORKER_PID"
echo "Msg PID:    $MESSAGE_WORKER_PID"
echo "Press Ctrl+C to stop all"

trap "kill $API_PID $BOT_PID $WORKER_PID $MESSAGE_WORKER_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
