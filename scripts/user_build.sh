#!/usr/bin/env bash
set -euo pipefail

echo "Systemd Motion - User Build Script"
echo "=================================="
echo ""
echo "This script will help you build packages for distribution."
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the motion project root directory"
    exit 1
fi

echo "✅ Project structure found"
echo ""

# Create build directory
mkdir -p build
cd build

echo "📦 Building packages..."
echo ""

# Create a simple tarball for distribution
echo "Creating source tarball..."
cd ..
tar --exclude='.git' --exclude='build' --exclude='__pycache__' --exclude='*.pyc' \
    -czf build/systemd-motion-1.0.0.tar.gz .

echo "✅ Source tarball created: build/systemd-motion-1.0.0.tar.gz"
echo ""

# Create installation script
cat > build/install.sh << 'EOF'
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
EOF

chmod +x build/install.sh

echo "✅ Installation script created: build/install.sh"
echo ""

# Create README for users
cat > build/README.md << 'EOF'
# Systemd Motion - Quick Install

## Installation

```bash
# Download and extract
wget https://github.com/yourusername/systemd-motion/archive/refs/heads/main.zip
unzip main.zip
cd systemd-motion-main

# Install
bash scripts/simple_install.sh
```

## Usage

```bash
# Check status
motion-ctl status

# Start/stop service
motion-ctl start
motion-ctl stop

# Launch GUI (optional)
motion-gui
```

## Features

- ✅ Silent operation
- ✅ Hidden behavior monitoring
- ✅ Minimal resource usage
- ✅ Auto-start on login
- ✅ Native systemd integration
EOF

echo "✅ User README created: build/README.md"
echo ""

echo "🎉 Build complete!"
echo ""
echo "Files created in build/ directory:"
echo "  - systemd-motion-1.0.0.tar.gz (source package)"
echo "  - install.sh (installation script)"
echo "  - README.md (user instructions)"
echo ""
echo "Next steps:"
echo "1. Upload these files to GitHub Releases"
echo "2. Users can download and install with the provided scripts"
