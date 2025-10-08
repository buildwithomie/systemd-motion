#!/usr/bin/env bash
set -euo pipefail

echo "Installing Motion Activity Monitor from source..."

# Check dependencies
echo "Checking dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adwaita-1 python3-dev build-essential

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user dbus-next PyGObject pillow

# Install the application
bash scripts/install.sh

echo "Installation complete!"
echo ""
echo "To start the GUI application, run: motion-gui"
echo "To start the service: bash scripts/start.sh"
echo "To stop the service: bash scripts/stop.sh"
echo ""
echo "The application will also appear in your applications menu."
