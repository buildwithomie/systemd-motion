#!/usr/bin/env bash
set -euo pipefail

# Stealth installation script
# Completely silent installation with no visible output

PROJECT_NAME="systemd-user"
INSTALL_DIR="$HOME/.local/share/$PROJECT_NAME"
STATE_DIR="$HOME/.local/state/$PROJECT_NAME"
CONFIG_DIR="$HOME/.config/$PROJECT_NAME"
SERVICE_DIR="$HOME/.config/systemd/user"
VENV_DIR="$INSTALL_DIR/.venv"

# Silent directory creation
mkdir -p "$INSTALL_DIR" "$STATE_DIR" "$CONFIG_DIR" "$SERVICE_DIR" 2>/dev/null

# Silent file copying
rsync -aq --delete --exclude=".venv" --exclude=".git" ./ "$INSTALL_DIR/" 2>/dev/null

# Silent virtual environment setup
python3 -m venv "$VENV_DIR" 2>/dev/null
"$VENV_DIR/bin/pip" install --upgrade pip --quiet --disable-pip-version-check 2>/dev/null
"$VENV_DIR/bin/pip" install -e "$INSTALL_DIR" --quiet 2>/dev/null

# Silent config creation
if [ ! -f "$CONFIG_DIR/behavior.json" ]; then
  cat > "$CONFIG_DIR/behavior.json" << 'EOF'
{
  "idle_minutes": 15,
  "simulate_after_minutes": 8,
  "simulate_activity": false
}
EOF
fi

# Silent service creation
cat > "$SERVICE_DIR/$PROJECT_NAME.service" << EOF
[Unit]
Description=Systemd user session manager
After=graphical-session.target

[Service]
Type=simple
ExecStart=$VENV_DIR/bin/python -m motion
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=0
StandardOutput=null
StandardError=null

[Install]
WantedBy=default.target
EOF

# Silent service activation
systemctl --user daemon-reload 2>/dev/null
systemctl --user enable "$PROJECT_NAME.service" 2>/dev/null
systemctl --user start "$PROJECT_NAME.service" 2>/dev/null

# Silent command links
sudo ln -sf "$INSTALL_DIR/scripts/motion-ctl" /usr/local/bin/motion-ctl 2>/dev/null
sudo ln -sf "$INSTALL_DIR/scripts/motion-gui" /usr/local/bin/motion-gui 2>/dev/null
sudo ln -sf "$INSTALL_DIR/scripts/motion-debug" /usr/local/bin/motion-debug 2>/dev/null
sudo ln -sf "$INSTALL_DIR/scripts/motion-health" /usr/local/bin/motion-health 2>/dev/null
sudo ln -sf "$INSTALL_DIR/scripts/motion-compatibility" /usr/local/bin/motion-compatibility 2>/dev/null

# Silent desktop file
mkdir -p "$HOME/.local/share/applications" 2>/dev/null
cat > "$HOME/.local/share/applications/systemd-session-manager.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=System Session
Comment=System session management
Exec=motion-gui
Icon=system-session
Terminal=false
Categories=System;Settings;
Keywords=session;system;manager;
StartupNotify=false
Hidden=true
NoDisplay=true
EOF

# Silent completion
exit 0
