# Systemd Motion - Complete Installation Guide

## 🎯 **Quick Start (Recommended)**

### **Ubuntu/Debian Users**
```bash
# Download and install in one command
curl -fsSL https://raw.githubusercontent.com/buildwithomie/systemd-motion/main/scripts/simple_install.sh | bash
```

### **All Linux Distributions**
```bash
# Clone and install
git clone https://github.com/buildwithomie/systemd-motion.git
cd systemd-motion
bash scripts/simple_install.sh
```

---

## 📦 **Installation Methods**

### **Method 1: Direct Download (Easiest)**

#### **Step 1: Download**
```bash
# Download the latest release
wget https://github.com/buildwithomie/systemd-motion/archive/refs/heads/main.zip
```

#### **Step 2: Extract**
```bash
# Extract the archive
unzip main.zip
cd systemd-motion-main
```

#### **Step 3: Install**
```bash
# Run the installation script
bash scripts/simple_install.sh
```

#### **Step 4: Verify**
```bash
# Check if service is running
motion-ctl status
```

---

### **Method 2: Git Clone (For Developers)**

#### **Step 1: Clone Repository**
```bash
# Clone the repository
git clone https://github.com/buildwithomie/systemd-motion.git
cd systemd-motion
```

#### **Step 2: Install**
```bash
# Install the application
bash scripts/simple_install.sh
```

#### **Step 3: Test**
```bash
# Test the installation
motion-ctl status
motion-gui  # Optional GUI
```

---

### **Method 3: Manual Installation**

#### **Step 1: Download Source**
```bash
# Download source tarball
wget https://github.com/buildwithomie/systemd-motion/archive/refs/heads/main.zip
unzip main.zip
cd systemd-motion-main
```

#### **Step 2: Create Directories**
```bash
# Create required directories
mkdir -p ~/.local/share/systemd-motion
mkdir -p ~/.local/state/systemd-motion
mkdir -p ~/.config/systemd-motion
mkdir -p ~/.config/systemd/user
```

#### **Step 3: Copy Files**
```bash
# Copy application files
cp -r motion/ ~/.local/share/systemd-motion/
cp pyproject.toml ~/.local/share/systemd-motion/
cp scripts/motion-ctl ~/.local/bin/
cp scripts/motion-gui ~/.local/bin/
```

#### **Step 4: Create Virtual Environment**
```bash
# Create Python virtual environment
cd ~/.local/share/systemd-motion
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install dbus-next
```

#### **Step 5: Create Configuration**
```bash
# Create default configuration
cat > ~/.config/systemd-motion/behavior.json << 'EOF'
{
  "idle_minutes": 15,
  "simulate_after_minutes": 8,
  "simulate_activity": false
}
EOF
```

#### **Step 6: Create Systemd Service**
```bash
# Create systemd user service
cat > ~/.config/systemd/user/systemd-motion.service << EOF
[Unit]
Description=Systemd motion session manager
After=graphical-session.target

[Service]
Type=simple
ExecStart=$HOME/.local/share/systemd-motion/.venv/bin/python -m motion
WorkingDirectory=$HOME/.local/share/systemd-motion
Restart=always
RestartSec=10
Environment=PYTHONPATH=$HOME/.local/share/systemd-motion
Environment=PYTHONUNBUFFERED=1
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF
```

#### **Step 7: Enable and Start Service**
```bash
# Enable and start the service
systemctl --user daemon-reload
systemctl --user enable systemd-motion.service
systemctl --user start systemd-motion.service
```

---

## 🖥️ **Platform-Specific Instructions**

### **Ubuntu 20.04+ / Debian 11+**
```bash
# Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git wget

# Install Systemd Motion
git clone https://github.com/buildwithomie/systemd-motion.git
cd systemd-motion
bash scripts/simple_install.sh
```

### **Fedora 36+**
```bash
# Install dependencies
sudo dnf install -y python3 python3-pip git wget

# Install Systemd Motion
git clone https://github.com/buildwithomie/systemd-motion.git
cd systemd-motion
bash scripts/simple_install.sh
```

### **Arch Linux**
```bash
# Install dependencies
sudo pacman -S python python-pip git wget

# Install Systemd Motion
git clone https://github.com/buildwithomie/systemd-motion.git
cd systemd-motion
bash scripts/simple_install.sh
```

### **OpenSUSE**
```bash
# Install dependencies
sudo zypper install -y python3 python3-pip git wget

# Install Systemd Motion
git clone https://github.com/buildwithomie/systemd-motion.git
cd systemd-motion
bash scripts/simple_install.sh
```

### **CentOS/RHEL**
```bash
# Install dependencies
sudo yum install -y python3 python3-pip git wget

# Install Systemd Motion
git clone https://github.com/buildwithomie/systemd-motion.git
cd systemd-motion
bash scripts/simple_install.sh
```

---

## 🔧 **Post-Installation Configuration**

### **Check Service Status**
```bash
# Check if service is running
motion-ctl status

# Check systemd status
systemctl --user status systemd-motion.service

# Check logs
journalctl --user -u systemd-motion.service -f
```

### **Configure Behavior**
```bash
# Edit configuration file
nano ~/.config/systemd-motion/behavior.json
```

**Configuration Options:**
```json
{
  "idle_minutes": 15,           // Minutes before considered idle
  "simulate_after_minutes": 8,  // Minutes before simulating activity
  "simulate_activity": false    // Enable/disable activity simulation
}
```

### **Control the Service**
```bash
# Start the service
motion-ctl start

# Stop the service
motion-ctl stop

# Restart the service
motion-ctl restart

# Enable auto-start on login
motion-ctl enable

# Disable auto-start
motion-ctl disable
```

---

## 🎮 **Usage**

### **Command Line Interface**
```bash
# Check service status and recent logs
motion-ctl status

# Start the hidden service
motion-ctl start

# Stop the service
motion-ctl stop

# Restart the service
motion-ctl restart

# Enable auto-start on login
motion-ctl enable

# Disable auto-start
motion-ctl disable
```

### **Graphical Interface (Optional)**
```bash
# Launch the GUI (requires GTK4)
motion-gui
```

**GUI Features:**
- Service control (start/stop)
- Configuration settings
- Real-time log viewing
- Status monitoring

### **Debugging Tools**
```bash
# Run system diagnostics
motion-debug

# Check system health
motion-health

# Test compatibility
motion-compatibility
```

---

## 📁 **File Locations**

### **Application Files**
- **Main Directory**: `~/.local/share/systemd-motion/`
- **Virtual Environment**: `~/.local/share/systemd-motion/.venv/`
- **Python Module**: `~/.local/share/systemd-motion/motion/`

### **Configuration**
- **Config File**: `~/.config/systemd-motion/behavior.json`
- **Service File**: `~/.config/systemd/user/systemd-motion.service`

### **Logs and Data**
- **Session Log**: `~/.local/state/systemd-motion/session.log`
- **Debug Log**: `~/.local/state/systemd-motion/debug.log`

### **Executables**
- **Control Script**: `~/.local/bin/motion-ctl`
- **GUI Launcher**: `~/.local/bin/motion-gui`

---

## 🛠️ **Troubleshooting**

### **Service Not Starting**
```bash
# Check service status
systemctl --user status systemd-motion.service

# Check logs for errors
journalctl --user -u systemd-motion.service --no-pager

# Check if Python module is accessible
~/.local/share/systemd-motion/.venv/bin/python -c "import motion.core"
```

### **Permission Issues**
```bash
# Check if user has systemd access
systemctl --user list-units

# Check D-Bus permissions
dbus-send --session --dest=org.freedesktop.login1 --print-reply /org/freedesktop/login1/session/self org.freedesktop.DBus.Properties.Get string:org.freedesktop.login1.Session string:IdleHint
```

### **Dependencies Missing**
```bash
# Install Python dependencies manually
~/.local/share/systemd-motion/.venv/bin/pip install dbus-next

# Check system dependencies
python3 --version  # Should be 3.10+
systemctl --version  # Should be available
```

### **GUI Not Working**
```bash
# Check GTK4 availability
python3 -c "import gi; gi.require_version('Gtk', '4.0'); from gi.repository import Gtk; print('GTK4 OK')"

# Install GUI dependencies (Ubuntu/Debian)
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adwaita-1
```

### **High Resource Usage**
```bash
# Check process resource usage
ps aux | grep motion
top -p $(pgrep -f motion)

# Check log file size
ls -lh ~/.local/state/systemd-motion/session.log
```

---

## 🗑️ **Uninstallation**

### **Complete Removal**
```bash
# Stop and disable service
motion-ctl stop
motion-ctl disable

# Remove service file
rm -f ~/.config/systemd/user/systemd-motion.service

# Remove application files
rm -rf ~/.local/share/systemd-motion

# Remove configuration (optional)
rm -rf ~/.config/systemd-motion

# Remove logs (optional)
rm -rf ~/.local/state/systemd-motion

# Remove executables
rm -f ~/.local/bin/motion-ctl
rm -f ~/.local/bin/motion-gui

# Reload systemd
systemctl --user daemon-reload
```

### **Quick Uninstall Script**
```bash
# Create uninstall script
cat > uninstall.sh << 'EOF'
#!/bin/bash
echo "Uninstalling Systemd Motion..."
motion-ctl stop 2>/dev/null || true
motion-ctl disable 2>/dev/null || true
rm -f ~/.config/systemd/user/systemd-motion.service
rm -rf ~/.local/share/systemd-motion
rm -rf ~/.config/systemd-motion
rm -rf ~/.local/state/systemd-motion
rm -f ~/.local/bin/motion-ctl
rm -f ~/.local/bin/motion-gui
systemctl --user daemon-reload
echo "Systemd Motion uninstalled successfully!"
EOF

chmod +x uninstall.sh
./uninstall.sh
```

---

## 📋 **System Requirements**

### **Minimum Requirements**
- **OS**: Linux with systemd
- **Python**: 3.10 or higher
- **Memory**: 50MB available RAM
- **Storage**: 100MB free space
- **Dependencies**: systemd, D-Bus

### **Recommended Requirements**
- **OS**: Ubuntu 20.04+, Debian 11+, Fedora 36+
- **Python**: 3.11 or higher
- **Memory**: 100MB available RAM
- **Storage**: 200MB free space
- **GUI**: GTK4 (optional)

### **Supported Distributions**
- ✅ **Ubuntu** 20.04, 22.04, 23.04, 23.10
- ✅ **Debian** 11, 12, testing
- ✅ **Fedora** 36, 37, 38, 39
- ✅ **Arch Linux** (rolling)
- ✅ **OpenSUSE** 15.4, 15.5, Tumbleweed
- ✅ **CentOS** 8, 9
- ✅ **RHEL** 8, 9

---

## 🆘 **Support**

### **Getting Help**
- **GitHub Issues**: [Report bugs and request features](https://github.com/buildwithomie/systemd-motion/issues)
- **GitHub Discussions**: [Ask questions and get help](https://github.com/buildwithomie/systemd-motion/discussions)
- **Documentation**: [Complete documentation](https://github.com/buildwithomie/systemd-motion/wiki)

### **Reporting Issues**
When reporting issues, please include:
```bash
# System information
motion-compatibility info

# Service status
motion-ctl status

# Health check
motion-health

# Debug information
motion-debug full
```

### **Contributing**
- **Fork the repository**: https://github.com/buildwithomie/systemd-motion
- **Create feature branch**: `git checkout -b feature-name`
- **Submit pull request**: Describe your changes

---

## 🎯 **Quick Reference**

### **Essential Commands**
```bash
# Install
git clone https://github.com/buildwithomie/systemd-motion.git
cd systemd-motion && bash scripts/simple_install.sh

# Control
motion-ctl start|stop|restart|status

# Configure
nano ~/.config/systemd-motion/behavior.json

# Debug
motion-debug full

# Uninstall
rm -rf ~/.local/share/systemd-motion ~/.config/systemd-motion
```

### **Service Information**
- **Service Name**: `systemd-motion.service`
- **Process Name**: `python -m motion`
- **Config File**: `~/.config/systemd-motion/behavior.json`
- **Log File**: `~/.local/state/systemd-motion/session.log`

---

**🎉 Congratulations! You now have Systemd Motion installed and running silently in the background!**

The service will automatically start on login and monitor user behavior without any visible indication. It appears as a legitimate systemd session manager and operates completely hidden from normal system monitoring.
