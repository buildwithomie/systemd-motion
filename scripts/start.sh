#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="motion"

echo "Starting $PROJECT_NAME service..."
systemctl --user start "$PROJECT_NAME.service"
echo "$PROJECT_NAME service started"
echo "Check status: systemctl --user status $PROJECT_NAME"
echo "View logs: tail -f ~/.local/state/$PROJECT_NAME/activity.log"
