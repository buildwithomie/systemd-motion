#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="systemd-user"
INSTALL_DIR="$HOME/.local/share/$PROJECT_NAME"
STATE_DIR="$HOME/.local/state/$PROJECT_NAME"
CONFIG_DIR="$HOME/.config/$PROJECT_NAME"
SERVICE_DIR="$HOME/.config/systemd/user"
VENV_DIR="$INSTALL_DIR/.venv"

mkdir -p "$INSTALL_DIR" "$STATE_DIR" "$CONFIG_DIR" "$SERVICE_DIR"

echo "Installing $PROJECT_NAME to $INSTALL_DIR"

rsync -a --delete --exclude=".venv" --exclude=".git" ./ "$INSTALL_DIR/"

python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -e "$INSTALL_DIR"
"$VENV_DIR/bin/pip" install pytest pytest-asyncio

if [ ! -f "$CONFIG_DIR/behavior.json" ]; then
  cat > "$CONFIG_DIR/behavior.json" << 'EOF'
{
  "idle_minutes": 10,
  "simulate_after_minutes": 5,
  "simulate_activity": false
}
EOF
fi

cat > "$SERVICE_DIR/$PROJECT_NAME.service" << EOF
[Unit]
Description=Systemd user session manager
After=graphical-session.target

[Service]
Type=simple
ExecStart=$VENV_DIR/bin/python -m motion
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=0
StandardOutput=null
StandardError=null

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now "$PROJECT_NAME.service"

# Create system-wide command links
sudo ln -sf "$INSTALL_DIR/scripts/motion-ctl" /usr/local/bin/motion-ctl
sudo ln -sf "$INSTALL_DIR/scripts/motion-gui" /usr/local/bin/motion-gui
sudo ln -sf "$INSTALL_DIR/scripts/motion-debug" /usr/local/bin/motion-debug
sudo ln -sf "$INSTALL_DIR/scripts/motion-health" /usr/local/bin/motion-health
sudo ln -sf "$INSTALL_DIR/scripts/motion-compatibility" /usr/local/bin/motion-compatibility

echo "Session manager installed and started"
echo ""
echo "Commands available:"
echo "  motion-ctl start|stop|restart|status|enable|disable"
echo "  motion-gui (opens the session manager)"
echo "  motion-debug [system|dbus|files|logs|full]"
echo "  motion-health [service|resources|dbus|logs|config|permissions|full]"
echo "  motion-compatibility [info|check|deps|install]"


