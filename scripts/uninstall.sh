#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="systemd-user"
INSTALL_DIR="$HOME/.local/share/$PROJECT_NAME"
SERVICE_DIR="$HOME/.config/systemd/user"

systemctl --user stop "$PROJECT_NAME.service" || true
systemctl --user disable "$PROJECT_NAME.service" || true
systemctl --user daemon-reload || true

rm -f "$SERVICE_DIR/$PROJECT_NAME.service"

# Remove system-wide command links
sudo rm -f /usr/local/bin/motion-ctl
sudo rm -f /usr/local/bin/motion-gui
sudo rm -f /usr/local/bin/motion-debug
sudo rm -f /usr/local/bin/motion-health
sudo rm -f /usr/local/bin/motion-compatibility

rm -rf "$INSTALL_DIR"

echo "Session manager uninstalled. To remove logs and config: rm -rf ~/.local/state/$PROJECT_NAME ~/.config/$PROJECT_NAME"


