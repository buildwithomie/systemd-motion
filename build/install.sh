#!/usr/bin/env bash
set -euo pipefail

echo "Installing Systemd Motion..."
echo "============================"

# Extract and install
tar -xzf systemd-motion-1.0.0.tar.gz
cd systemd-motion-1.0.0

# Run installation
bash scripts/simple_install.sh

echo ""
echo "✅ Systemd Motion installed successfully!"
echo "Run 'motion-ctl status' to check the service"
