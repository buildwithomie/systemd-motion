#!/usr/bin/env bash
set -euo pipefail

echo "Building Motion Activity Monitor .deb package..."

# Clean previous builds
rm -rf debian/motion-activity-monitor
rm -f motion-activity-monitor_*.deb

# Build the package
dpkg-buildpackage -us -uc

echo "Package built successfully!"
echo "Install with: sudo dpkg -i ../motion-activity-monitor_*.deb"
echo "Fix dependencies with: sudo apt-get install -f"
