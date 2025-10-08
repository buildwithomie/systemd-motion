#!/usr/bin/env python3

import asyncio
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from dbus_next.aio import MessageBus
from dbus_next.constants import BusType


class MotionHealthChecker:
    """Comprehensive health monitoring for Motion application"""
    
    def __init__(self):
        self.app_name = "motion"
        self.config_dir = Path.home() / ".config" / self.app_name
        self.state_dir = Path.home() / ".local" / "state" / self.app_name
        self.share_dir = Path.home() / ".local" / "share" / self.app_name
        self.log_file = self.state_dir / "activity.log"
        
    def check_service_health(self) -> Dict[str, Any]:
        """Check systemd service health"""
        result = {
            "service_name": "motion.service",
            "status": "unknown",
            "active": False,
            "enabled": False,
            "restart_count": 0,
            "uptime": None,
            "errors": []
        }
        
        try:
            # Check if service is active
            proc = subprocess.run(
                ["systemctl", "--user", "is-active", "motion.service"],
                capture_output=True, text=True, timeout=5
            )
            result["active"] = proc.returncode == 0
            result["status"] = proc.stdout.strip()
            
            # Check if service is enabled
            proc = subprocess.run(
                ["systemctl", "--user", "is-enabled", "motion.service"],
                capture_output=True, text=True, timeout=5
            )
            result["enabled"] = proc.returncode == 0
            
            # Get detailed service status
            proc = subprocess.run(
                ["systemctl", "--user", "show", "motion.service", 
                 "--property=ActiveState,SubState,MainPID,RestartCount"],
                capture_output=True, text=True, timeout=5
            )
            
            if proc.returncode == 0:
                for line in proc.stdout.strip().split('\n'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        if key == "ActiveState":
                            result["status"] = value
                        elif key == "RestartCount":
                            try:
                                result["restart_count"] = int(value)
                            except ValueError:
                                pass
                                
        except subprocess.TimeoutExpired:
            result["errors"].append("Service check timeout")
        except Exception as e:
            result["errors"].append(f"Service check error: {e}")
            
        return result
        
    def check_resource_usage(self) -> Dict[str, Any]:
        """Check system resource usage"""
        result = {
            "memory": {"used": 0, "total": 0, "percentage": 0},
            "cpu": {"usage": 0},
            "disk": {"used": 0, "total": 0, "percentage": 0},
            "process_info": {},
            "errors": []
        }
        
        try:
            # Get motion process info
            proc = subprocess.run(
                ["pgrep", "-f", "motion"],
                capture_output=True, text=True, timeout=5
            )
            
            if proc.returncode == 0:
                pids = proc.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        try:
                            # Get process memory and CPU info
                            proc_info = subprocess.run(
                                ["ps", "-p", pid, "-o", "pid,ppid,cmd,%mem,%cpu"],
                                capture_output=True, text=True, timeout=5
                            )
                            
                            if proc_info.returncode == 0:
                                lines = proc_info.stdout.strip().split('\n')
                                if len(lines) > 1:
                                    parts = lines[1].split()
                                    if len(parts) >= 5:
                                        result["process_info"][pid] = {
                                            "memory_percent": float(parts[3]),
                                            "cpu_percent": float(parts[4]),
                                            "command": ' '.join(parts[2:])
                                        }
                        except (ValueError, IndexError) as e:
                            result["errors"].append(f"Process info error for PID {pid}: {e}")
                            
            # Get system memory info
            try:
                with open("/proc/meminfo", "r") as f:
                    meminfo = {}
                    for line in f:
                        if ":" in line:
                            key, value = line.strip().split(":", 1)
                            meminfo[key] = int(value.split()[0]) * 1024  # Convert to bytes
                    
                    if "MemTotal" in meminfo and "MemAvailable" in meminfo:
                        result["memory"]["total"] = meminfo["MemTotal"]
                        result["memory"]["used"] = meminfo["MemTotal"] - meminfo["MemAvailable"]
                        result["memory"]["percentage"] = (
                            result["memory"]["used"] / result["memory"]["total"] * 100
                        )
            except Exception as e:
                result["errors"].append(f"Memory info error: {e}")
                
            # Get disk usage for motion directories
            try:
                motion_dir = self.share_dir
                if motion_dir.exists():
                    proc = subprocess.run(
                        ["df", str(motion_dir)],
                        capture_output=True, text=True, timeout=5
                    )
                    
                    if proc.returncode == 0:
                        lines = proc.stdout.strip().split('\n')
                        if len(lines) > 1:
                            parts = lines[1].split()
                            if len(parts) >= 4:
                                result["disk"]["total"] = int(parts[1]) * 1024
                                result["disk"]["used"] = int(parts[2]) * 1024
                                result["disk"]["percentage"] = (
                                    result["disk"]["used"] / result["disk"]["total"] * 100
                                )
            except Exception as e:
                result["errors"].append(f"Disk info error: {e}")
                
        except Exception as e:
            result["errors"].append(f"Resource check error: {e}")
            
        return result
        
    async def check_dbus_health(self) -> Dict[str, Any]:
        """Check D-Bus connectivity and functionality"""
        result = {
            "system_bus": {"connected": False, "error": None},
            "session_bus": {"connected": False, "error": None},
            "logind": {"available": False, "error": None, "last_check": None},
            "screensaver": {"available": False, "error": None, "last_check": None},
            "response_times": {},
            "errors": []
        }
        
        # Test system bus
        try:
            start_time = time.time()
            system_bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
            response_time = time.time() - start_time
            result["system_bus"]["connected"] = True
            result["response_times"]["system_bus"] = response_time
            
            # Test logind interface
            try:
                start_time = time.time()
                introspect = await system_bus.introspect(
                    "org.freedesktop.login1", 
                    "/org/freedesktop/login1/session/self"
                )
                obj = system_bus.get_proxy_object(
                    "org.freedesktop.login1", 
                    "/org/freedesktop/login1/session/self", 
                    introspect
                )
                props = obj.get_interface("org.freedesktop.DBus.Properties")
                await props.call_get("org.freedesktop.login1.Session", "IdleHint")
                response_time = time.time() - start_time
                result["logind"]["available"] = True
                result["logind"]["last_check"] = datetime.now().isoformat()
                result["response_times"]["logind"] = response_time
            except Exception as e:
                result["logind"]["error"] = str(e)
                
        except Exception as e:
            result["system_bus"]["error"] = str(e)
            
        # Test session bus
        try:
            start_time = time.time()
            session_bus = await MessageBus(bus_type=BusType.SESSION).connect()
            response_time = time.time() - start_time
            result["session_bus"]["connected"] = True
            result["response_times"]["session_bus"] = response_time
            
            # Test screensaver interface
            try:
                start_time = time.time()
                introspect = await session_bus.introspect(
                    "org.freedesktop.ScreenSaver", 
                    "/org/freedesktop/ScreenSaver"
                )
                response_time = time.time() - start_time
                result["screensaver"]["available"] = True
                result["screensaver"]["last_check"] = datetime.now().isoformat()
                result["response_times"]["screensaver"] = response_time
            except Exception as e:
                result["screensaver"]["error"] = str(e)
                
        except Exception as e:
            result["session_bus"]["error"] = str(e)
            
        return result
        
    def check_log_health(self) -> Dict[str, Any]:
        """Check log file health and activity"""
        result = {
            "log_exists": False,
            "log_size": 0,
            "last_modified": None,
            "total_entries": 0,
            "error_count": 0,
            "warning_count": 0,
            "recent_activity": False,
            "log_rotation_needed": False,
            "errors": []
        }
        
        if not self.log_file.exists():
            result["errors"].append("Activity log file does not exist")
            return result
            
        try:
            result["log_exists"] = True
            stat = self.log_file.stat()
            result["log_size"] = stat.st_size
            result["last_modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            # Check if log needs rotation (larger than 10MB)
            if result["log_size"] > 10 * 1024 * 1024:
                result["log_rotation_needed"] = True
                
            # Analyze log content
            with open(self.log_file, "r") as f:
                lines = f.readlines()
                result["total_entries"] = len(lines)
                
                # Count errors and warnings
                error_count = sum(1 for line in lines if "ERROR" in line.upper())
                warning_count = sum(1 for line in lines if "WARNING" in line.upper())
                result["error_count"] = error_count
                result["warning_count"] = warning_count
                
                # Check for recent activity (within last hour)
                recent_threshold = datetime.now() - timedelta(hours=1)
                recent_lines = []
                
                for line in lines[-50:]:  # Check last 50 lines
                    try:
                        # Extract timestamp from log line
                        timestamp_str = line.split()[0] + " " + line.split()[1]
                        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                        
                        if timestamp > recent_threshold:
                            recent_lines.append(line)
                    except (ValueError, IndexError):
                        continue
                        
                result["recent_activity"] = len(recent_lines) > 0
                
        except Exception as e:
            result["errors"].append(f"Log analysis error: {e}")
            
        return result
        
    def check_config_health(self) -> Dict[str, Any]:
        """Check configuration file health"""
        result = {
            "config_exists": False,
            "config_valid": False,
            "config_values": {},
            "default_values_used": False,
            "errors": []
        }
        
        config_file = self.config_dir / "config.json"
        
        if not config_file.exists():
            result["errors"].append("Configuration file does not exist")
            return result
            
        result["config_exists"] = True
        
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
                result["config_values"] = config
                result["config_valid"] = True
                
                # Check if using default values
                default_config = {
                    "idle_minutes": 10,
                    "simulate_after_minutes": 5,
                    "simulate_activity": False
                }
                
                if config == default_config:
                    result["default_values_used"] = True
                    
        except json.JSONDecodeError as e:
            result["errors"].append(f"Invalid JSON in config file: {e}")
        except Exception as e:
            result["errors"].append(f"Config file error: {e}")
            
        return result
        
    def check_file_permissions(self) -> Dict[str, Any]:
        """Check file and directory permissions"""
        result = {
            "directories": {},
            "files": {},
            "permission_issues": [],
            "errors": []
        }
        
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
                    readable = os.access(path, os.R_OK)
                    writable = os.access(path, os.W_OK)
                    executable = os.access(path, os.X_OK)
                    
                    result["directories"][description] = {
                        "path": str(path),
                        "readable": readable,
                        "writable": writable,
                        "executable": executable
                    }
                    
                    if not readable:
                        result["permission_issues"].append(f"{description} not readable")
                    if not writable:
                        result["permission_issues"].append(f"{description} not writable")
                    if not executable:
                        result["permission_issues"].append(f"{description} not executable")
                        
                elif path.is_file():
                    # Check file permissions
                    readable = os.access(path, os.R_OK)
                    writable = os.access(path, os.W_OK)
                    
                    result["files"][description] = {
                        "path": str(path),
                        "readable": readable,
                        "writable": writable,
                        "size": path.stat().st_size
                    }
                    
                    if not readable:
                        result["permission_issues"].append(f"{description} not readable")
                    if not writable:
                        result["permission_issues"].append(f"{description} not writable")
                        
                else:
                    result["permission_issues"].append(f"{description} does not exist")
                    
            except Exception as e:
                result["errors"].append(f"Permission check error for {description}: {e}")
                
        return result
        
    async def run_health_check(self) -> Dict[str, Any]:
        """Run complete health check"""
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "service_health": {},
            "resource_usage": {},
            "dbus_health": {},
            "log_health": {},
            "config_health": {},
            "file_permissions": {},
            "overall_health": "unknown",
            "recommendations": [],
            "critical_issues": []
        }
        
        # Run all health checks
        health_report["service_health"] = self.check_service_health()
        health_report["resource_usage"] = self.check_resource_usage()
        health_report["dbus_health"] = await self.check_dbus_health()
        health_report["log_health"] = self.check_log_health()
        health_report["config_health"] = self.check_config_health()
        health_report["file_permissions"] = self.check_file_permissions()
        
        # Determine overall health
        issues = []
        
        # Check service health
        if not health_report["service_health"]["active"]:
            issues.append("Service not running")
            health_report["critical_issues"].append("Motion service is not active")
            
        if health_report["service_health"]["restart_count"] > 5:
            issues.append("Service restarting frequently")
            health_report["critical_issues"].append("Service has restarted multiple times")
            
        # Check D-Bus health
        if not health_report["dbus_health"]["system_bus"]["connected"]:
            issues.append("System D-Bus not accessible")
            health_report["critical_issues"].append("Cannot connect to system D-Bus")
            
        if not health_report["dbus_health"]["logind"]["available"]:
            issues.append("logind interface not available")
            health_report["recommendations"].append("Check systemd-logind installation")
            
        # Check log health
        if not health_report["log_health"]["log_exists"]:
            issues.append("Activity log missing")
            health_report["critical_issues"].append("Activity log file does not exist")
            
        if health_report["log_health"]["log_rotation_needed"]:
            issues.append("Log file too large")
            health_report["recommendations"].append("Consider log rotation")
            
        if health_report["log_health"]["error_count"] > 10:
            issues.append("High error count in logs")
            health_report["recommendations"].append("Review error logs")
            
        # Check permissions
        if health_report["file_permissions"]["permission_issues"]:
            issues.append("Permission issues detected")
            health_report["critical_issues"].extend(
                health_report["file_permissions"]["permission_issues"]
            )
            
        # Determine overall health
        if not health_report["critical_issues"]:
            if not issues:
                health_report["overall_health"] = "excellent"
            elif len(issues) <= 2:
                health_report["overall_health"] = "good"
            else:
                health_report["overall_health"] = "fair"
        else:
            health_report["overall_health"] = "poor"
            
        return health_report
        
    def save_health_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save health report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.state_dir / f"motion_health_{timestamp}.json"
        else:
            filename = Path(filename)
            
        with open(filename, "w") as f:
            json.dump(report, f, indent=2)
            
        return str(filename)
        
    def print_health_summary(self, report: Dict[str, Any]):
        """Print health check summary"""
        print("\n" + "="*60)
        print("MOTION HEALTH CHECK SUMMARY")
        print("="*60)
        
        # Overall health
        health_status = report["overall_health"].upper()
        print(f"Overall Health: {health_status}")
        
        # Service status
        service = report["service_health"]
        status = "RUNNING" if service["active"] else "STOPPED"
        print(f"Service Status: {status}")
        
        if service["restart_count"] > 0:
            print(f"Restart Count: {service['restart_count']}")
            
        # D-Bus status
        dbus = report["dbus_health"]
        print(f"System D-Bus: {'OK' if dbus['system_bus']['connected'] else 'FAIL'}")
        print(f"Session D-Bus: {'OK' if dbus['session_bus']['connected'] else 'FAIL'}")
        print(f"logind Interface: {'OK' if dbus['logind']['available'] else 'FAIL'}")
        
        # Resource usage
        resources = report["resource_usage"]
        if resources["process_info"]:
            for pid, info in resources["process_info"].items():
                print(f"Process {pid}: {info['memory_percent']:.1f}% memory, {info['cpu_percent']:.1f}% CPU")
                
        # Log status
        log = report["log_health"]
        if log["log_exists"]:
            size_mb = log["log_size"] / (1024 * 1024)
            print(f"Activity Log: {size_mb:.1f}MB, {log['total_entries']} entries")
            if log["error_count"] > 0:
                print(f"  Errors: {log['error_count']}, Warnings: {log['warning_count']}")
        else:
            print("Activity Log: NOT FOUND")
            
        # Critical issues
        if report["critical_issues"]:
            print(f"\nCRITICAL ISSUES ({len(report['critical_issues'])}):")
            for issue in report["critical_issues"]:
                print(f"  ❌ {issue}")
                
        # Recommendations
        if report["recommendations"]:
            print(f"\nRECOMMENDATIONS ({len(report['recommendations'])}):")
            for rec in report["recommendations"]:
                print(f"  💡 {rec}")
        
        print("="*60)


async def main():
    """Main health check function"""
    checker = MotionHealthChecker()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "service":
            result = checker.check_service_health()
            print(json.dumps(result, indent=2))
            
        elif command == "resources":
            result = checker.check_resource_usage()
            print(json.dumps(result, indent=2))
            
        elif command == "dbus":
            result = await checker.check_dbus_health()
            print(json.dumps(result, indent=2))
            
        elif command == "logs":
            result = checker.check_log_health()
            print(json.dumps(result, indent=2))
            
        elif command == "config":
            result = checker.check_config_health()
            print(json.dumps(result, indent=2))
            
        elif command == "permissions":
            result = checker.check_file_permissions()
            print(json.dumps(result, indent=2))
            
        elif command == "full":
            report = await checker.run_health_check()
            checker.print_health_summary(report)
            report_file = checker.save_health_report(report)
            print(f"\nFull report saved: {report_file}")
            
        else:
            print("Usage: motion-health [service|resources|dbus|logs|config|permissions|full]")
            
    else:
        # Run full health check by default
        report = await checker.run_health_check()
        checker.print_health_summary(report)
        report_file = checker.save_health_report(report)
        print(f"\nFull report saved: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())
