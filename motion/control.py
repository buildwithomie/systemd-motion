#!/usr/bin/env python3

import sys
import subprocess
import os

def main():
    """Main control function for motion-ctl command"""
    if len(sys.argv) < 2:
        print("Usage: motion-ctl [start|stop|restart|status|enable|disable]")
        sys.exit(1)
    
    command = sys.argv[1]
    service_name = "systemd-motion.service"
    
    try:
        if command == "start":
            subprocess.run(["systemctl", "--user", "start", service_name], check=True)
            print("Systemd Motion service started")
        elif command == "stop":
            subprocess.run(["systemctl", "--user", "stop", service_name], check=True)
            print("Systemd Motion service stopped")
        elif command == "restart":
            subprocess.run(["systemctl", "--user", "restart", service_name], check=True)
            print("Systemd Motion service restarted")
        elif command == "status":
            subprocess.run(["systemctl", "--user", "status", service_name], check=False)
        elif command == "enable":
            subprocess.run(["systemctl", "--user", "enable", service_name], check=True)
            print("Systemd Motion service enabled")
        elif command == "disable":
            subprocess.run(["systemctl", "--user", "disable", service_name], check=True)
            print("Systemd Motion service disabled")
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
