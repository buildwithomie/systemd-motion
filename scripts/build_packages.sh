#!/usr/bin/env bash
set -euo pipefail

echo "Building Systemd Motion Packages"
echo "================================"

# Clean previous builds
rm -rf build/ dist/ *.deb *.snap

# Build Debian package
echo "Building Debian package..."
dpkg-buildpackage -us -uc
echo "✅ Debian package built: ../systemd-motion_*.deb"

# Build Snap package (if snapcraft is available)
if command -v snapcraft &> /dev/null; then
    echo "Building Snap package..."
    snapcraft
    echo "✅ Snap package built: systemd-motion_*.snap"
else
    echo "⚠️  snapcraft not available, skipping Snap package"
fi

echo ""
echo "Packages built successfully!"
echo ""
echo "To install Debian package:"
echo "  sudo dpkg -i ../systemd-motion_*.deb"
echo "  sudo apt-get install -f"
echo ""
echo "To install Snap package:"
echo "  sudo snap install systemd-motion_*.snap --dangerous"
echo ""
echo "To publish to Ubuntu Store:"
echo "  snapcraft upload systemd-motion_*.snap"
