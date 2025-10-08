#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="motion"

echo "=== $PROJECT_NAME Service Status ==="
systemctl --user status "$PROJECT_NAME.service" --no-pager

echo ""
echo "=== Recent Activity Log ==="
LOG_FILE="$HOME/.local/state/$PROJECT_NAME/activity.log"
if [ -f "$LOG_FILE" ]; then
    tail -10 "$LOG_FILE"
else
    echo "No log file found at $LOG_FILE"
fi
