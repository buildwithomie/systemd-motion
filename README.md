# Motion - Ubuntu Activity Monitor

<div align="center">
  <img src="data/icons/48x48/apps/com.motion.activity-monitor.png" alt="Motion Logo" width="64" height="64">
  <h3>Professional Activity Monitoring for Ubuntu</h3>
</div>

Motion is a modern, professional-grade activity monitoring application designed specifically for Ubuntu. It provides real-time activity tracking with a beautiful GTK4 interface and seamless system integration.

## ✨ Features

- 🖥️ **Modern GTK4 Interface** - Clean, native Ubuntu desktop integration
- 📊 **Real-time Activity Monitoring** - Tracks user activity via systemd-logind
- ⚙️ **Configurable Settings** - Customizable idle thresholds and behavior
- 🔄 **Optional Activity Simulation** - Prevents system from going idle (user-controlled)
- 📝 **Comprehensive Logging** - Detailed activity logs with timestamps
- 🔧 **Systemd Integration** - Runs as a user service with auto-start capability
- 📦 **Easy Installation** - Available as .deb package or from source

## 🚀 Installation

### Option 1: Install from .deb Package (Recommended)

```bash
# Build the package
bash scripts/build_deb.sh

# Install the package
sudo dpkg -i ../motion-activity-monitor_*.deb

# Fix any dependency issues
sudo apt-get install -f
```

### Option 2: Install from Source

```bash
# Install dependencies and build
bash scripts/install_from_source.sh
```

### Option 3: Manual Installation

```bash
bash scripts/install.sh
```

## 🎮 Usage

### Graphical Interface
Launch the GUI application from your applications menu or run:
```bash
motion-gui
```

The GUI provides:
- **Service Control** - Start/stop the monitoring service
- **Configuration** - Adjust idle thresholds and simulation settings
- **Real-time Logs** - View activity logs with live updates
- **Status Monitoring** - See current service status

### Command Line Control

After installation, you can use these simple commands from anywhere:

```bash
# Start the service
motion-ctl start

# Stop the service  
motion-ctl stop

# Restart the service
motion-ctl restart

# Check status and recent logs
motion-ctl status

# Enable auto-start on login
motion-ctl enable

# Disable auto-start
motion-ctl disable
```

### Debugging & Testing Tools

Motion includes comprehensive debugging and testing tools:

```bash
# System diagnostics and troubleshooting
motion-debug                    # Full diagnostic report
motion-debug system            # Check system requirements
motion-debug dbus              # Test D-Bus connections
motion-debug files             # Check file permissions
motion-debug logs              # Analyze activity logs

# Health monitoring
motion-health                  # Complete health check
motion-health service          # Check service status
motion-health resources        # Monitor resource usage
motion-health dbus             # Test D-Bus functionality

# Linux compatibility checking
motion-compatibility           # Check distribution compatibility
motion-compatibility info      # System information
motion-compatibility deps      # Check dependencies
motion-compatibility install   # Get installation commands

# Quick system test (before installation)
bash scripts/quick-test        # Test basic requirements

# Run full test suite
bash scripts/run-tests         # Comprehensive testing
```

### Configuration

Config file: `~/.config/motion/config.json`

```json
{
  "idle_minutes": 10,
  "simulate_after_minutes": 5,
  "simulate_activity": false
}
```

- `idle_minutes`: Threshold after which the session is considered idle (based on system idle hint).
- `simulate_after_minutes`: If `simulate_activity` is true, simulate activity after this many minutes of continuous idle.
- `simulate_activity`: If true, motion will attempt to call `org.freedesktop.ScreenSaver.SimulateUserActivity` on the session bus when idle long enough. This is off by default and requires your explicit opt-in.

## 📋 Requirements

- **Ubuntu 20.04+** with systemd-logind (default on Ubuntu)
- **Python 3.10+**
- **GTK4** and **libadwaita** for the GUI interface

## 📁 File Locations

- **Application Files**: `~/.local/share/motion/`
- **Configuration**: `~/.config/motion/config.json`
- **Activity Logs**: `~/.local/state/motion/activity.log`
- **Service Unit**: `~/.config/systemd/user/motion.service`

## 🔧 Configuration

The application uses a JSON configuration file located at `~/.config/motion/config.json`:

```json
{
  "idle_minutes": 10,
  "simulate_after_minutes": 5,
  "simulate_activity": false
}
```

### Configuration Options

- **`idle_minutes`**: Threshold after which the session is considered idle (1-60 minutes)
- **`simulate_after_minutes`**: If simulation is enabled, simulate activity after this many minutes of continuous idle (1-30 minutes)
- **`simulate_activity`**: Enable/disable automatic activity simulation when idle (boolean)

## 🗑️ Uninstallation

### For .deb Package Installation
```bash
sudo apt remove motion-activity-monitor
```

### For Source Installation
```bash
bash scripts/uninstall.sh
```

This will:
- Stop and disable the systemd service
- Remove the installed application files
- Clean up systemd service files
- **Note**: Logs and configuration files are preserved by default

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues and pull requests.

## 📄 License

This project is open source. See the license file for details.

## 🧪 Testing & Debugging

Motion includes comprehensive testing and debugging tools:

- **Quick Test**: `bash scripts/quick-test` - Test system requirements before installation
- **Full Test Suite**: `bash scripts/run-tests` - Comprehensive automated testing
- **System Diagnostics**: `motion-debug` - Detailed system analysis and troubleshooting
- **Health Monitoring**: `motion-health` - Real-time system health checks
- **Compatibility Check**: `motion-compatibility` - Linux distribution compatibility verification

For detailed debugging information, see [DEBUGGING.md](DEBUGGING.md).

## 🆘 Support

For support, please:
1. Run `motion-debug full` and include the generated report
2. Check the [Issues](https://github.com/your-repo/motion/issues) page
3. Review the activity logs in `~/.local/state/motion/activity.log`
4. Verify your system meets the requirements with `bash scripts/quick-test`

---

**Motion** - Professional activity monitoring for Ubuntu 🐧


