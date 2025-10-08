#!/usr/bin/env bash
set -euo pipefail

# Simple installation without sudo requirements
PROJECT_NAME="systemd-motion"
INSTALL_DIR="$HOME/.local/share/$PROJECT_NAME"
STATE_DIR="$HOME/.local/state/$PROJECT_NAME"
CONFIG_DIR="$HOME/.config/$PROJECT_NAME"
SERVICE_DIR="$HOME/.config/systemd/user"
VENV_DIR="$INSTALL_DIR/.venv"

echo "Installing hidden session manager..."

# Create directories
mkdir -p "$INSTALL_DIR" "$STATE_DIR" "$CONFIG_DIR" "$SERVICE_DIR"

# Copy files
rsync -a --delete --exclude=".venv" --exclude=".git" ./ "$INSTALL_DIR/"

# Create virtual environment
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip --quiet
"$VENV_DIR/bin/pip" install dbus-next --quiet

# Create config
if [ ! -f "$CONFIG_DIR/behavior.json" ]; then
  cat > "$CONFIG_DIR/behavior.json" << 'EOF'
{
  "idle_minutes": 15,
  "simulate_after_minutes": 8,
  "simulate_activity": false
}
EOF
fi

# Create service
cat > "$SERVICE_DIR/$PROJECT_NAME.service" << EOF
[Unit]
Description=Systemd motion session manager
After=graphical-session.target

[Service]
Type=simple
ExecStart=$VENV_DIR/bin/python -m motion
WorkingDirectory=$INSTALL_DIR
Restart=always
RestartSec=10
Environment=PYTHONPATH=$INSTALL_DIR
Environment=PYTHONUNBUFFERED=1
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF

# Enable and start service
systemctl --user daemon-reload
systemctl --user enable "$PROJECT_NAME.service"
systemctl --user start "$PROJECT_NAME.service"

# Create command links in user bin
mkdir -p "$HOME/.local/bin"
ln -sf "$INSTALL_DIR/scripts/motion-ctl" "$HOME/.local/bin/motion-ctl"
ln -sf "$INSTALL_DIR/scripts/motion-gui" "$HOME/.local/bin/motion-gui"

echo "Hidden session manager installed successfully!"
echo ""
echo "Commands available:"
echo "  motion-ctl start|stop|restart|status"
echo "  motion-gui (opens hidden interface)"
echo ""
echo "Service running as: systemd-motion.service"
