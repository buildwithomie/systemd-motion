# Systemd Motion - Installation Guide

## 🚀 Quick Installation

### Option 1: Debian Package (Recommended)
```bash
# Download and install
wget https://github.com/yourusername/systemd-motion/releases/latest/download/systemd-motion_1.0.0_all.deb
sudo dpkg -i systemd-motion_1.0.0_all.deb
sudo apt-get install -f
```

### Option 2: Snap Package
```bash
# Install from Snap Store
sudo snap install systemd-motion

# Or install from local file
sudo snap install systemd-motion_1.0.0_amd64.snap --dangerous
```

### Option 3: From Source
```bash
# Clone and install
git clone https://github.com/yourusername/systemd-motion.git
cd systemd-motion
bash scripts/simple_install.sh
```

## 📦 Package Managers

### Ubuntu/Debian
```bash
# Add repository (when available)
curl -fsSL https://yourusername.github.io/systemd-motion/gpg | sudo apt-key add -
echo "deb https://yourusername.github.io/systemd-motion/ stable main" | sudo tee /etc/apt/sources.list.d/systemd-motion.list
sudo apt update
sudo apt install systemd-motion
```

### Arch Linux (AUR)
```bash
# Using yay
yay -S systemd-motion

# Using makepkg
git clone https://aur.archlinux.org/systemd-motion.git
cd systemd-motion
makepkg -si
```

### Fedora (COPR)
```bash
# Add COPR repository
sudo dnf copr enable yourusername/systemd-motion
sudo dnf install systemd-motion
```

## 🎯 Usage After Installation

### Start the Service
```bash
# The service starts automatically, but you can control it:
motion-ctl start
motion-ctl stop
motion-ctl restart
motion-ctl status
```

### Configuration
```bash
# Edit configuration
nano ~/.config/systemd-motion/behavior.json
```

### GUI (Optional)
```bash
# Launch GUI interface
motion-gui
```

## 🔧 Requirements

- **Ubuntu 20.04+** or **Debian 11+**
- **Python 3.10+**
- **systemd** (default on most Linux distributions)
- **D-Bus** (for session monitoring)

## 🛠️ Troubleshooting

### Service Not Starting
```bash
# Check service status
systemctl --user status systemd-motion.service

# Check logs
journalctl --user -u systemd-motion.service -f
```

### Permission Issues
```bash
# Ensure user has systemd access
systemctl --user list-units

# Check D-Bus permissions
dbus-send --session --dest=org.freedesktop.login1 --print-reply /org/freedesktop/login1/session/self org.freedesktop.DBus.Properties.Get string:org.freedesktop.login1.Session string:IdleHint
```

### Uninstall
```bash
# Remove package
sudo apt remove systemd-motion
# or
sudo snap remove systemd-motion

# Clean up user files
rm -rf ~/.config/systemd-motion ~/.local/state/systemd-motion
```

## 📋 Features

- ✅ **Silent Operation**: Runs completely hidden
- ✅ **Low Resource Usage**: Minimal CPU and memory
- ✅ **Auto-Start**: Starts automatically on login
- ✅ **Session Monitoring**: Tracks user behavior
- ✅ **Configurable**: Customizable thresholds
- ✅ **System Integration**: Native systemd service

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/systemd-motion/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/systemd-motion/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/systemd-motion/discussions)
