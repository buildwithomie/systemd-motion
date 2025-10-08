#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="systemd-motion"
INSTALL_DIR="$HOME/.local/share/$PROJECT_NAME"
SERVICE_DIR="$HOME/.config/systemd/user"

echo "Uninstalling Systemd Motion..."

systemctl --user stop "$PROJECT_NAME.service" || true
systemctl --user disable "$PROJECT_NAME.service" || true
systemctl --user daemon-reload || true

rm -f "$SERVICE_DIR/$PROJECT_NAME.service"
rm -rf "$INSTALL_DIR"
rm -f "$HOME/.local/bin/motion-ctl"
rm -f "$HOME/.local/bin/motion-gui"

echo "Systemd Motion uninstalled successfully!"
echo "To remove logs and config: rm -rf ~/.local/state/$PROJECT_NAME ~/.config/$PROJECT_NAME"