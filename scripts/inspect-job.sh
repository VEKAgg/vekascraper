#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <job-id>"
    echo "Example: $0 JOB-20260713-abc12"
    exit 1
fi

JOB_ID="$1"
DATA_DIR="${DATA_ROOT:-data}"

JOB_FILE="$DATA_DIR/jobs/$JOB_ID.json"
LOG_FILE="$DATA_DIR/logs/$JOB_ID.log"
MANIFEST_FILE="$DATA_DIR/manifests/$JOB_ID.json"

echo "=== Job: $JOB_ID ==="

if [ -f "$JOB_FILE" ]; then
    echo ""
    echo "--- State ---"
    python3 -m json.tool "$JOB_FILE" 2>/dev/null || cat "$JOB_FILE"
else
    echo "Job file not found: $JOB_FILE"
fi

if [ -f "$MANIFEST_FILE" ]; then
    echo ""
    echo "--- Manifest ---"
    python3 -m json.tool "$MANIFEST_FILE" 2>/dev/null || cat "$MANIFEST_FILE"
fi

if [ -f "$LOG_FILE" ]; then
    echo ""
    echo "--- Log (last 20 entries) ---"
    tail -20 "$LOG_FILE" | while read -r line; do
        echo "$line" | python3 -m json.tool 2>/dev/null || echo "$line"
    done
fi
