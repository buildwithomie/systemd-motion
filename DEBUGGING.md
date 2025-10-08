# Motion Debugging & Testing Guide

This guide provides comprehensive information about debugging, testing, and troubleshooting the Motion application across different Linux distributions.

## 🔧 Debugging Tools

### Motion Debug Tool (`motion-debug`)

The debug tool provides detailed system analysis and troubleshooting capabilities.

#### Usage
```bash
# Full diagnostic (recommended)
motion-debug

# Specific checks
motion-debug system      # Check system requirements
motion-debug dbus        # Test D-Bus connections
motion-debug files       # Check file permissions
motion-debug logs        # Analyze activity logs
motion-debug full        # Complete diagnostic with report
```

#### What it checks:
- **System Requirements**: Python version, platform, dependencies
- **D-Bus Connectivity**: System/session bus, logind interface, screensaver interface
- **File Permissions**: Config, state, and log directory access
- **Log Analysis**: Activity patterns, error counts, recent entries
- **Service Status**: systemd service state and configuration

### Motion Health Checker (`motion-health`)

Comprehensive health monitoring for ongoing system status.

#### Usage
```bash
# Full health check (recommended)
motion-health

# Specific checks
motion-health service      # Check service health
motion-health resources    # Check resource usage
motion-health dbus         # Test D-Bus functionality
motion-health logs         # Analyze log health
motion-health config       # Check configuration
motion-health permissions  # Check file permissions
motion-health full         # Complete health report
```

#### Health Metrics:
- **Service Health**: Active state, restart count, uptime
- **Resource Usage**: Memory, CPU, disk usage by motion processes
- **D-Bus Health**: Connection status, response times, interface availability
- **Log Health**: File size, rotation needs, error/warning counts
- **Config Health**: File validity, default values usage
- **Permissions**: Directory and file access rights

## 🧪 Testing Suite

### Running Tests

```bash
# Run all tests
cd /home/shubham/workplace/motion
bash scripts/run-tests

# Run tests with verbose output
bash scripts/run-tests verbose

# Run specific test categories
python3 -m pytest tests/test_motion.py::TestMotionCore -v
python3 -m pytest tests/test_motion.py::TestMotionDbus -v
python3 -m pytest tests/test_motion.py::TestMotionDebugger -v
```

### Test Categories

#### 1. **Core Functionality Tests** (`TestMotionCore`)
- Configuration loading (default and file-based)
- Logging setup and file creation
- Basic application initialization

#### 2. **D-Bus Integration Tests** (`TestMotionDbus`)
- System D-Bus connection and idle hint retrieval
- Session D-Bus connection and activity simulation
- Error handling for D-Bus failures

#### 3. **Debugging Tool Tests** (`TestMotionDebugger`)
- System requirements checking
- File permission validation
- Log analysis functionality

#### 4. **Integration Tests** (`TestMotionIntegration`)
- End-to-end monitor flow testing
- Service lifecycle management
- Configuration updates and service restart

#### 5. **Linux Compatibility Tests** (`TestLinuxCompatibility`)
- Ubuntu/Debian compatibility
- Fedora/Arch compatibility
- Dependency availability across distributions

## 🌍 Linux Distribution Compatibility

### Motion Compatibility Checker (`motion-compatibility`)

Check compatibility across different Linux distributions.

#### Usage
```bash
# Full compatibility check
motion-compatibility

# Specific checks
motion-compatibility info     # System information
motion-compatibility check    # Distribution compatibility
motion-compatibility deps     # Dependency availability
motion-compatibility install  # Installation commands
```

### Supported Distributions

#### ✅ **Excellent Compatibility**
- **Ubuntu 20.04+**: Native support with full GTK4 integration
- **Debian 10+**: Full support, may need newer GTK4 packages
- **Fedora 36+**: Native support with latest packages
- **Arch Linux**: Rolling release with latest packages

#### ✅ **Good Compatibility**
- **OpenSUSE 15.4+**: Support available, may need additional repositories
- **Gentoo**: Manual compilation required

#### ⚠️ **Limited Compatibility**
- **Alpine Linux**: Limited due to OpenRC init system

### Installation Commands by Distribution

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-gi python3-gi-cairo
sudo apt install -y gir1.2-gtk-4.0 gir1.2-adwaita-1
sudo apt install -y python3-dev build-essential
pip3 install --user dbus-next pillow
```

#### Fedora
```bash
sudo dnf update
sudo dnf install -y python3 python3-pip python3-gobject python3-gobject-devel
sudo dnf install -y gtk4 libadwaita python3-dev gcc
pip3 install --user dbus-next pillow
```

#### Arch Linux
```bash
sudo pacman -Syu
sudo pacman -S python python-gobject gtk4 libadwaita
sudo pacman -S python-pip python-dev gcc
pip install --user dbus-next pillow
```

#### OpenSUSE
```bash
sudo zypper refresh
sudo zypper install -y python3 python3-pip python3-gobject python3-gobject-devel
sudo zypper install -y gtk4 libadwaita python3-devel gcc
pip3 install --user dbus-next pillow
```

## 🚨 Troubleshooting Common Issues

### Service Not Starting

#### Check service status:
```bash
motion-health service
systemctl --user status motion.service
```

#### Common causes:
1. **Missing dependencies**: Run `motion-compatibility deps`
2. **Permission issues**: Run `motion-health permissions`
3. **D-Bus problems**: Run `motion-debug dbus`
4. **Configuration errors**: Check `~/.config/motion/config.json`

### GUI Not Launching

#### Check GUI dependencies:
```bash
python3 -c "import gi; gi.require_version('Gtk', '4.0'); from gi.repository import Gtk; print('GTK4 OK')"
```

#### Common fixes:
1. Install GTK4 development packages
2. Update graphics drivers
3. Check desktop environment compatibility

### Activity Not Being Detected

#### Debug D-Bus connectivity:
```bash
motion-debug dbus
motion-health dbus
```

#### Check logind interface:
```bash
# Test logind manually
busctl --user call org.freedesktop.login1 /org/freedesktop/login1/session/self \
  org.freedesktop.DBus.Properties Get ss org.freedesktop.login1.Session IdleHint
```

### High Resource Usage

#### Monitor resource usage:
```bash
motion-health resources
top -p $(pgrep -f motion)
```

#### Optimization tips:
1. Check for memory leaks in logs
2. Reduce check interval in configuration
3. Disable activity simulation if not needed

### Log File Issues

#### Check log health:
```bash
motion-health logs
```

#### Log rotation:
```bash
# Manual log rotation
mv ~/.local/state/motion/activity.log ~/.local/state/motion/activity.log.old
motion-ctl restart
```

## 📊 Performance Monitoring

### Real-time Monitoring
```bash
# Watch service status
watch -n 1 'motion-ctl status'

# Monitor resource usage
htop -p $(pgrep -f motion)

# Watch logs
tail -f ~/.local/state/motion/activity.log
```

### Automated Health Checks
```bash
# Create cron job for daily health checks
echo "0 9 * * * motion-health full > /tmp/motion-health-$(date +\%Y\%m\%d).log" | crontab -
```

## 🔍 Advanced Debugging

### Enable Debug Logging
```python
# Add to motion/__main__.py for more verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### D-Bus Debugging
```bash
# Monitor D-Bus messages
dbus-monitor --session "interface='org.freedesktop.login1.Session'"
dbus-monitor --session "interface='org.freedesktop.ScreenSaver'"
```

### Systemd Debugging
```bash
# Enable systemd user debugging
systemd --user log-level debug
journalctl --user -f -u motion.service
```

## 📝 Reporting Issues

When reporting issues, please include:

1. **System Information**:
   ```bash
   motion-compatibility info > system-info.txt
   ```

2. **Health Report**:
   ```bash
   motion-health full > health-report.json
   ```

3. **Debug Report**:
   ```bash
   motion-debug full > debug-report.json
   ```

4. **Activity Logs**:
   ```bash
   cp ~/.local/state/motion/activity.log activity.log
   ```

5. **Service Logs**:
   ```bash
   journalctl --user -u motion.service --no-pager > service.log
   ```

This comprehensive debugging and testing framework ensures Motion works reliably across different Linux distributions and provides detailed insights into any issues that may arise.
