#!/usr/bin/env python3

import asyncio
import json
import logging
import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from dbus_next.aio import MessageBus
from dbus_next.constants import BusType
from dbus_next import Variant


class MotionDebugger:
    """Comprehensive debugging and testing tool for Motion"""
    
    def __init__(self):
        self.app_name = "motion"
        self.config_dir = Path.home() / ".config" / self.app_name
        self.state_dir = Path.home() / ".local" / "state" / self.app_name
        self.share_dir = Path.home() / ".local" / "share" / self.app_name
        self.log_file = self.state_dir / "activity.log"
        self.debug_log = self.state_dir / "debug.log"
        
        # Setup debug logging
        self.setup_debug_logging()
        
    def setup_debug_logging(self):
        """Setup debug logging to file"""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        debug_handler = logging.FileHandler(self.debug_log, mode='a')
        debug_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        debug_handler.setFormatter(formatter)
        
        debug_logger = logging.getLogger('motion_debug')
        debug_logger.setLevel(logging.DEBUG)
        debug_logger.addHandler(debug_handler)
        
        self.debug_logger = debug_logger
        
    def log_debug(self, message: str, level: str = "INFO"):
        """Log debug message"""
        getattr(self.debug_logger, level.lower())(message)
        print(f"[{level}] {message}")
        
    def check_system_requirements(self) -> Dict[str, Any]:
        """Check system requirements and compatibility"""
        results = {
            "python_version": sys.version,
            "platform": sys.platform,
            "system_info": {},
            "dependencies": {},
            "permissions": {},
            "services": {},
            "errors": []
        }
        
        # Check Python version
        if sys.version_info < (3, 10):
            results["errors"].append("Python 3.10+ required")
        else:
            self.log_debug(f"Python version OK: {sys.version}")
            
        # Check platform
        if sys.platform != "linux":
            results["errors"].append("Linux platform required")
        else:
            self.log_debug("Platform OK: Linux")
            
        # Check system info
        try:
            with open("/etc/os-release", "r") as f:
                os_info = {}
                for line in f:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        os_info[key] = value.strip('"')
                results["system_info"] = os_info
                self.log_debug(f"OS: {os_info.get('PRETTY_NAME', 'Unknown')}")
        except Exception as e:
            results["errors"].append(f"Cannot read OS info: {e}")
            
        # Check Python dependencies
        required_packages = ["dbus_next", "gi"]
        for package in required_packages:
            try:
                if package == "gi":
                    import gi
                    gi.require_version('Gtk', '4.0')
                    from gi.repository import Gtk
                    results["dependencies"][package] = f"Gtk {Gtk.get_major_version()}.{Gtk.get_minor_version()}"
                    self.log_debug(f"Dependency OK: {package}")
                else:
                    __import__(package)
                    results["dependencies"][package] = "Available"
                    self.log_debug(f"Dependency OK: {package}")
            except Exception as e:
                results["dependencies"][package] = f"Error: {e}"
                results["errors"].append(f"Missing dependency: {package}")
                
        # Check permissions
        try:
            # Check if user can access systemd user services
            result = subprocess.run(["systemctl", "--user", "list-units"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                results["permissions"]["systemd_user"] = "OK"
                self.log_debug("Permission OK: systemd user services")
            else:
                results["permissions"]["systemd_user"] = f"Error: {result.stderr}"
                results["errors"].append("Cannot access systemd user services")
        except Exception as e:
            results["permissions"]["systemd_user"] = f"Error: {e}"
            results["errors"].append(f"systemd access error: {e}")
            
        # Check motion service status
        try:
            result = subprocess.run(["systemctl", "--user", "is-active", "motion.service"], 
                                  capture_output=True, text=True, timeout=5)
            results["services"]["motion"] = {
                "status": result.stdout.strip(),
                "active": result.returncode == 0
            }
            self.log_debug(f"Motion service status: {result.stdout.strip()}")
        except Exception as e:
            results["services"]["motion"] = {"error": str(e)}
            results["errors"].append(f"Service check error: {e}")
            
        return results
        
    async def test_dbus_connections(self) -> Dict[str, Any]:
        """Test D-Bus connections and functionality"""
        results = {
            "system_bus": {"connected": False, "error": None},
            "session_bus": {"connected": False, "error": None},
            "logind": {"available": False, "error": None},
            "screensaver": {"available": False, "error": None}
        }
        
        # Test system bus connection
        try:
            system_bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
            results["system_bus"]["connected"] = True
            self.log_debug("System D-Bus connection OK")
        except Exception as e:
            results["system_bus"]["error"] = str(e)
            self.log_debug(f"System D-Bus error: {e}", "ERROR")
            
        # Test session bus connection
        try:
            session_bus = await MessageBus(bus_type=BusType.SESSION).connect()
            results["session_bus"]["connected"] = True
            self.log_debug("Session D-Bus connection OK")
        except Exception as e:
            results["session_bus"]["error"] = str(e)
            self.log_debug(f"Session D-Bus error: {e}", "ERROR")
            
        # Test logind interface
        try:
            if results["system_bus"]["connected"]:
                introspect = await system_bus.introspect("org.freedesktop.login1", "/org/freedesktop/login1/session/self")
                obj = system_bus.get_proxy_object("org.freedesktop.login1", "/org/freedesktop/login1/session/self", introspect)
                props = obj.get_interface("org.freedesktop.DBus.Properties")
                await props.call_get("org.freedesktop.login1.Session", "IdleHint")
                results["logind"]["available"] = True
                self.log_debug("logind interface OK")
        except Exception as e:
            results["logind"]["error"] = str(e)
            self.log_debug(f"logind interface error: {e}", "ERROR")
            
        # Test screensaver interface
        try:
            if results["session_bus"]["connected"]:
                introspect = await session_bus.introspect("org.freedesktop.ScreenSaver", "/org/freedesktop/ScreenSaver")
                results["screensaver"]["available"] = True
                self.log_debug("screensaver interface OK")
        except Exception as e:
            results["screensaver"]["error"] = str(e)
            self.log_debug(f"screensaver interface error: {e}", "ERROR")
            
        return results
        
    def check_file_permissions(self) -> Dict[str, Any]:
        """Check file permissions and accessibility"""
        results = {}
        
        paths_to_check = [
            (self.config_dir, "config directory"),
            (self.state_dir, "state directory"),
            (self.share_dir, "share directory"),
            (self.log_file, "activity log"),
            (self.config_dir / "config.json", "config file")
        ]
        
        for path, description in paths_to_check:
            try:
                if path.is_dir():
                    # Check directory permissions
                    os.listdir(path)
                    results[description] = {
                        "exists": True,
                        "readable": True,
                        "writable": os.access(path, os.W_OK)
                    }
                elif path.is_file():
                    # Check file permissions
                    results[description] = {
                        "exists": True,
                        "readable": os.access(path, os.R_OK),
                        "writable": os.access(path, os.W_OK),
                        "size": path.stat().st_size
                    }
                else:
                    results[description] = {"exists": False}
                    
                self.log_debug(f"File check OK: {description}")
            except Exception as e:
                results[description] = {"error": str(e)}
                self.log_debug(f"File check error: {description} - {e}", "ERROR")
                
        return results
        
    def analyze_logs(self) -> Dict[str, Any]:
        """Analyze activity logs for patterns and issues"""
        results = {
            "log_exists": False,
            "total_lines": 0,
            "recent_entries": [],
            "error_count": 0,
            "activity_pattern": {},
            "issues": []
        }
        
        if not self.log_file.exists():
            results["issues"].append("Activity log file does not exist")
            return results
            
        results["log_exists"] = True
        
        try:
            with open(self.log_file, "r") as f:
                lines = f.readlines()
                results["total_lines"] = len(lines)
                
                # Get recent entries
                results["recent_entries"] = lines[-10:] if len(lines) >= 10 else lines
                
                # Count errors
                error_count = sum(1 for line in lines if "ERROR" in line.upper())
                results["error_count"] = error_count
                
                # Analyze activity pattern
                state_changes = [line for line in lines if "state=" in line]
                results["activity_pattern"]["state_changes"] = len(state_changes)
                
                # Check for long periods without activity
                if len(state_changes) > 0:
                    last_activity = state_changes[-1]
                    # Simple check for recent activity
                    if "state=ACTIVE" in last_activity:
                        results["activity_pattern"]["last_state"] = "ACTIVE"
                    else:
                        results["activity_pattern"]["last_state"] = "IDLE"
                        
                self.log_debug(f"Log analysis complete: {len(lines)} lines, {error_count} errors")
                
        except Exception as e:
            results["issues"].append(f"Log analysis error: {e}")
            self.log_debug(f"Log analysis error: {e}", "ERROR")
            
        return results
        
    def run_diagnostic(self) -> Dict[str, Any]:
        """Run complete diagnostic"""
        self.log_debug("Starting Motion diagnostic...")
        
        diagnostic = {
            "timestamp": datetime.now().isoformat(),
            "system_requirements": {},
            "dbus_connections": {},
            "file_permissions": {},
            "log_analysis": {},
            "recommendations": []
        }
        
        # Run all checks
        diagnostic["system_requirements"] = self.check_system_requirements()
        diagnostic["file_permissions"] = self.check_file_permissions()
        diagnostic["log_analysis"] = self.analyze_logs()
        
        # Run async D-Bus tests
        try:
            diagnostic["dbus_connections"] = asyncio.run(self.test_dbus_connections())
        except Exception as e:
            diagnostic["dbus_connections"] = {"error": str(e)}
            
        # Generate recommendations
        if diagnostic["system_requirements"]["errors"]:
            diagnostic["recommendations"].append("Fix system requirement issues")
            
        if not diagnostic["dbus_connections"]["system_bus"]["connected"]:
            diagnostic["recommendations"].append("Check system D-Bus service")
            
        if not diagnostic["dbus_connections"]["session_bus"]["connected"]:
            diagnostic["recommendations"].append("Check session D-Bus service")
            
        if not diagnostic["dbus_connections"]["logind"]["available"]:
            diagnostic["recommendations"].append("Install systemd-logind or check permissions")
            
        if diagnostic["log_analysis"]["error_count"] > 0:
            diagnostic["recommendations"].append("Review error logs for issues")
            
        self.log_debug("Diagnostic complete")
        return diagnostic
        
    def save_report(self, diagnostic: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save diagnostic report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.state_dir / f"motion_diagnostic_{timestamp}.json"
        else:
            filename = Path(filename)
            
        with open(filename, "w") as f:
            json.dump(diagnostic, f, indent=2)
            
        self.log_debug(f"Diagnostic report saved: {filename}")
        return str(filename)
        
    def print_summary(self, diagnostic: Dict[str, Any]):
        """Print diagnostic summary"""
        print("\n" + "="*60)
        print("MOTION DIAGNOSTIC SUMMARY")
        print("="*60)
        
        # System info
        sys_info = diagnostic["system_requirements"]["system_info"]
        if sys_info:
            print(f"OS: {sys_info.get('PRETTY_NAME', 'Unknown')}")
        print(f"Python: {diagnostic['system_requirements']['python_version']}")
        
        # Service status
        service_status = diagnostic["system_requirements"]["services"].get("motion", {})
        if "active" in service_status:
            status = "RUNNING" if service_status["active"] else "STOPPED"
            print(f"Motion Service: {status}")
        
        # D-Bus status
        dbus = diagnostic["dbus_connections"]
        print(f"System D-Bus: {'OK' if dbus.get('system_bus', {}).get('connected') else 'FAIL'}")
        print(f"Session D-Bus: {'OK' if dbus.get('session_bus', {}).get('connected') else 'FAIL'}")
        print(f"logind Interface: {'OK' if dbus.get('logind', {}).get('available') else 'FAIL'}")
        
        # Log status
        log_analysis = diagnostic["log_analysis"]
        if log_analysis["log_exists"]:
            print(f"Activity Log: {log_analysis['total_lines']} entries, {log_analysis['error_count']} errors")
        else:
            print("Activity Log: NOT FOUND")
            
        # Issues
        all_errors = []
        all_errors.extend(diagnostic["system_requirements"]["errors"])
        all_errors.extend(log_analysis["issues"])
        
        if all_errors:
            print(f"\nISSUES FOUND ({len(all_errors)}):")
            for error in all_errors:
                print(f"  - {error}")
        else:
            print("\nNO ISSUES FOUND")
            
        # Recommendations
        if diagnostic["recommendations"]:
            print(f"\nRECOMMENDATIONS ({len(diagnostic['recommendations'])}):")
            for rec in diagnostic["recommendations"]:
                print(f"  - {rec}")
        
        print("="*60)


def main():
    """Main debug function"""
    debugger = MotionDebugger()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "system":
            results = debugger.check_system_requirements()
            print(json.dumps(results, indent=2))
            
        elif command == "dbus":
            results = asyncio.run(debugger.test_dbus_connections())
            print(json.dumps(results, indent=2))
            
        elif command == "files":
            results = debugger.check_file_permissions()
            print(json.dumps(results, indent=2))
            
        elif command == "logs":
            results = debugger.analyze_logs()
            print(json.dumps(results, indent=2))
            
        elif command == "full":
            diagnostic = debugger.run_diagnostic()
            debugger.print_summary(diagnostic)
            report_file = debugger.save_report(diagnostic)
            print(f"\nFull report saved: {report_file}")
            
        else:
            print("Usage: motion-debug [system|dbus|files|logs|full]")
            
    else:
        # Run full diagnostic by default
        diagnostic = debugger.run_diagnostic()
        debugger.print_summary(diagnostic)
        report_file = debugger.save_report(diagnostic)
        print(f"\nFull report saved: {report_file}")


if __name__ == "__main__":
    main()
