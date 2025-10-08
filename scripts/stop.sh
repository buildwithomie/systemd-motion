#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="motion"

echo "Stopping $PROJECT_NAME service..."
systemctl --user stop "$PROJECT_NAME.service"
echo "$PROJECT_NAME service stopped"
