#!/usr/bin/env bash
set -euo pipefail

# Systemd Motion - One-Click Installation Script
# This script installs Systemd Motion on any Linux distribution

echo "🚀 Systemd Motion - Installation Script"
echo "======================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this script as root (sudo)"
    echo "   Run it as a regular user: bash install.sh"
    exit 1
fi

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "📦 Installing git..."
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y git
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y git
    elif command -v pacman &> /dev/null; then
        sudo pacman -S git
    elif command -v zypper &> /dev/null; then
        sudo zypper install -y git
    else
        echo "❌ Please install git manually and run this script again"
        exit 1
    fi
fi

# Check if Python 3.10+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    echo "   Please install Python 3.10 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION or higher is required"
    echo "   Found Python $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Check if systemd is available
if ! command -v systemctl &> /dev/null; then
    echo "❌ systemd is required but not found"
    echo "   This application requires systemd to run"
    exit 1
fi

echo "✅ systemd found"

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

echo "📥 Downloading Systemd Motion..."
git clone https://github.com/buildwithomie/systemd-motion.git
cd systemd-motion

echo "🔧 Installing Systemd Motion..."
bash scripts/simple_install.sh

# Clean up
cd /
rm -rf "$TEMP_DIR"

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "✅ Systemd Motion has been installed successfully!"
echo ""
echo "📋 What was installed:"
echo "   - Service: systemd-motion.service"
echo "   - Commands: motion-ctl, motion-gui"
echo "   - Config: ~/.config/systemd-motion/behavior.json"
echo "   - Logs: ~/.local/state/systemd-motion/session.log"
echo ""
echo "🎮 Quick Start:"
echo "   motion-ctl status    # Check service status"
echo "   motion-ctl start     # Start the service"
echo "   motion-ctl stop      # Stop the service"
echo "   motion-gui           # Launch GUI (optional)"
echo ""
echo "📖 For detailed usage instructions:"
echo "   https://github.com/buildwithomie/systemd-motion/blob/main/INSTALLATION_GUIDE.md"
echo ""
echo "🆘 Need help? Visit:"
echo "   https://github.com/buildwithomie/systemd-motion/issues"
echo ""
echo "The service is now running silently in the background! 🥷"
