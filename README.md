# Systemd Motion

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Linux](https://img.shields.io/badge/platform-Linux-lightgrey.svg)](https://www.linux.org/)

> A lightweight session management service that monitors user behavior and maintains system session state with silent background operation.

## 🚀 Quick Install

```bash
# One-click installation
curl -fsSL https://raw.githubusercontent.com/buildwithomie/systemd-motion/main/install.sh | bash
```

## 📋 Features

- ✅ **Silent Operation** - Runs completely hidden in background
- ✅ **Minimal Resource Usage** - Only ~10MB memory footprint
- ✅ **Auto-Start** - Starts automatically on login
- ✅ **Session Monitoring** - Tracks user behavior via systemd-logind
- ✅ **Configurable** - Customizable behavior thresholds
- ✅ **System Integration** - Native systemd user service
- ✅ **Cross-Platform** - Works on all major Linux distributions

## 🎯 Installation

### One-Click Install (Recommended)
```bash
curl -fsSL https://raw.githubusercontent.com/buildwithomie/systemd-motion/main/install.sh | bash
```

### Manual Install
```bash
git clone https://github.com/buildwithomie/systemd-motion.git
cd systemd-motion
bash scripts/simple_install.sh
```

## 🎮 Usage

### Service Control
```bash
# Check service status
motion-ctl status

# Start/stop service
motion-ctl start
motion-ctl stop

# Enable auto-start
motion-ctl enable
```

### Configuration
```bash
# Edit configuration
nano ~/.config/systemd-motion/behavior.json
```

```json
{
  "idle_minutes": 15,
  "simulate_after_minutes": 8,
  "simulate_activity": false
}
```

## 📁 File Locations

- **Service**: `~/.config/systemd/user/systemd-motion.service`
- **Config**: `~/.config/systemd-motion/behavior.json`
- **Logs**: `~/.local/state/systemd-motion/session.log`
- **App**: `~/.local/share/systemd-motion/`

## 🛠️ Requirements

- **OS**: Linux with systemd (Ubuntu 20.04+, Debian 11+, Fedora 36+)
- **Python**: 3.10 or higher
- **Memory**: 50MB available RAM
- **Storage**: 100MB free space

## 🗑️ Uninstall

```bash
# Stop and remove
motion-ctl stop
motion-ctl disable

# Remove files
rm -rf ~/.local/share/systemd-motion
rm -rf ~/.config/systemd-motion
rm -rf ~/.local/state/systemd-motion
rm -f ~/.local/bin/motion-ctl
rm -f ~/.local/bin/motion-gui
```

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/buildwithomie/systemd-motion/issues)
- **Documentation**: [Installation Guide](INSTALLATION_GUIDE.md)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**⭐ If you find this project useful, please consider giving it a star!**

**🔗 Repository**: https://github.com/buildwithomie/systemd-motion