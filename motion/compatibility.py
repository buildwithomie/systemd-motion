#!/usr/bin/env python3

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import platform


class LinuxCompatibilityChecker:
    """Check compatibility across different Linux distributions"""
    
    def __init__(self):
        self.distribution_info = self.get_distribution_info()
        self.compatibility_matrix = self.load_compatibility_matrix()
        
    def get_distribution_info(self) -> Dict[str, Any]:
        """Get current distribution information"""
        info = {
            "platform": sys.platform,
            "machine": platform.machine(),
            "processor": platform.processor(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "distribution": {},
            "package_manager": None,
            "init_system": None
        }
        
        # Try to get distribution info from /etc/os-release
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        info["distribution"][key] = value.strip('"')
        except FileNotFoundError:
            pass
            
        # Try to get distribution info from /etc/lsb-release
        try:
            with open("/etc/lsb-release", "r") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        info["distribution"][key] = value.strip('"')
        except FileNotFoundError:
            pass
            
        # Detect package manager
        info["package_manager"] = self.detect_package_manager()
        
        # Detect init system
        info["init_system"] = self.detect_init_system()
        
        return info
        
    def detect_package_manager(self) -> Optional[str]:
        """Detect the package manager used by the system"""
        package_managers = {
            "apt": ["apt", "apt-get", "dpkg"],
            "yum": ["yum"],
            "dnf": ["dnf"],
            "pacman": ["pacman"],
            "zypper": ["zypper"],
            "portage": ["emerge"],
            "apk": ["apk"]
        }
        
        for pm, commands in package_managers.items():
            for cmd in commands:
                try:
                    subprocess.run([cmd, "--version"], 
                                 capture_output=True, check=True, timeout=5)
                    return pm
                except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                    continue
                    
        return None
        
    def detect_init_system(self) -> Optional[str]:
        """Detect the init system"""
        # Check for systemd
        try:
            subprocess.run(["systemctl", "--version"], 
                         capture_output=True, check=True, timeout=5)
            return "systemd"
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass
            
        # Check for other init systems
        if os.path.exists("/sbin/init"):
            try:
                with open("/sbin/init", "r") as f:
                    content = f.read()
                    if "systemd" in content:
                        return "systemd"
                    elif "upstart" in content:
                        return "upstart"
                    elif "sysvinit" in content:
                        return "sysvinit"
            except Exception:
                pass
                
        return "unknown"
        
    def load_compatibility_matrix(self) -> Dict[str, Any]:
        """Load compatibility matrix for different distributions"""
        return {
            "ubuntu": {
                "versions": ["20.04", "22.04", "23.04", "23.10", "24.04"],
                "package_manager": "apt",
                "init_system": "systemd",
                "dependencies": {
                    "python3": ">=3.8",
                    "python3-gi": "required",
                    "python3-gi-cairo": "required",
                    "gir1.2-gtk-4.0": "required",
                    "gir1.2-adwaita-1": "required",
                    "python3-dbus-next": "required",
                    "python3-pil": "required",
                    "systemd": "required"
                },
                "compatibility": "excellent",
                "notes": "Native Ubuntu support with full GTK4 integration"
            },
            "debian": {
                "versions": ["10", "11", "12", "testing"],
                "package_manager": "apt",
                "init_system": "systemd",
                "dependencies": {
                    "python3": ">=3.8",
                    "python3-gi": "required",
                    "python3-gi-cairo": "required",
                    "gir1.2-gtk-4.0": "required",
                    "gir1.2-adwaita-1": "required",
                    "python3-dbus-next": "required",
                    "python3-pil": "required",
                    "systemd": "required"
                },
                "compatibility": "excellent",
                "notes": "Full Debian support, may need newer GTK4 packages"
            },
            "fedora": {
                "versions": ["36", "37", "38", "39", "40"],
                "package_manager": "dnf",
                "init_system": "systemd",
                "dependencies": {
                    "python3": ">=3.8",
                    "python3-gobject": "required",
                    "python3-gobject-devel": "required",
                    "gtk4": "required",
                    "libadwaita": "required",
                    "python3-dbus-next": "required",
                    "python3-pillow": "required",
                    "systemd": "required"
                },
                "compatibility": "excellent",
                "notes": "Native Fedora support with latest packages"
            },
            "arch": {
                "versions": ["rolling"],
                "package_manager": "pacman",
                "init_system": "systemd",
                "dependencies": {
                    "python": ">=3.8",
                    "python-gobject": "required",
                    "gtk4": "required",
                    "libadwaita": "required",
                    "python-dbus-next": "required",
                    "python-pillow": "required",
                    "systemd": "required"
                },
                "compatibility": "excellent",
                "notes": "Arch Linux rolling release with latest packages"
            },
            "opensuse": {
                "versions": ["15.4", "15.5", "tumbleweed"],
                "package_manager": "zypper",
                "init_system": "systemd",
                "dependencies": {
                    "python3": ">=3.8",
                    "python3-gobject": "required",
                    "python3-gobject-devel": "required",
                    "gtk4": "required",
                    "libadwaita": "required",
                    "python3-dbus-next": "required",
                    "python3-pillow": "required",
                    "systemd": "required"
                },
                "compatibility": "good",
                "notes": "OpenSUSE support, may need additional repositories for GTK4"
            },
            "gentoo": {
                "versions": ["stable", "testing"],
                "package_manager": "portage",
                "init_system": "systemd",
                "dependencies": {
                    "dev-lang/python": ">=3.8",
                    "dev-python/pygobject": "required",
                    "x11-libs/gtk": ">=4.0",
                    "gui-libs/libadwaita": "required",
                    "dev-python/dbus-next": "required",
                    "dev-python/pillow": "required",
                    "sys-apps/systemd": "required"
                },
                "compatibility": "good",
                "notes": "Gentoo support, requires manual compilation"
            },
            "alpine": {
                "versions": ["3.18", "3.19", "edge"],
                "package_manager": "apk",
                "init_system": "openrc",
                "dependencies": {
                    "python3": ">=3.8",
                    "py3-gobject": "required",
                    "gtk4": "required",
                    "libadwaita": "required",
                    "py3-dbus-next": "required",
                    "py3-pillow": "required",
                    "systemd": "optional"
                },
                "compatibility": "limited",
                "notes": "Alpine Linux support limited due to OpenRC init system"
            }
        }
        
    def check_current_distribution(self) -> Dict[str, Any]:
        """Check compatibility for current distribution"""
        dist_id = self.distribution_info["distribution"].get("ID", "").lower()
        dist_name = self.distribution_info["distribution"].get("NAME", "").lower()
        
        # Try to match distribution
        matched_dist = None
        for dist_key in self.compatibility_matrix.keys():
            if (dist_key in dist_id or 
                dist_key in dist_name or 
                dist_id in dist_key or 
                dist_name in dist_key):
                matched_dist = dist_key
                break
                
        if not matched_dist:
            # Try to guess from package manager
            pm = self.distribution_info["package_manager"]
            if pm == "apt":
                matched_dist = "ubuntu"  # Default to Ubuntu for apt
            elif pm == "dnf":
                matched_dist = "fedora"
            elif pm == "pacman":
                matched_dist = "arch"
            elif pm == "zypper":
                matched_dist = "opensuse"
                
        result = {
            "detected_distribution": matched_dist,
            "distribution_info": self.distribution_info,
            "compatibility": {},
            "recommendations": [],
            "issues": []
        }
        
        if matched_dist and matched_dist in self.compatibility_matrix:
            dist_info = self.compatibility_matrix[matched_dist]
            result["compatibility"] = dist_info
            
            # Check compatibility
            if dist_info["compatibility"] == "excellent":
                result["recommendations"].append("Full compatibility - ready to install")
            elif dist_info["compatibility"] == "good":
                result["recommendations"].append("Good compatibility - may need additional setup")
            elif dist_info["compatibility"] == "limited":
                result["recommendations"].append("Limited compatibility - some features may not work")
                
            # Check init system
            if (dist_info["init_system"] == "systemd" and 
                self.distribution_info["init_system"] != "systemd"):
                result["issues"].append("Systemd required but not detected")
                result["recommendations"].append("Install systemd or use alternative init system")
                
        else:
            result["issues"].append("Distribution not recognized")
            result["recommendations"].append("Manual installation may be required")
            
        return result
        
    def check_dependencies(self, distribution: Optional[str] = None) -> Dict[str, Any]:
        """Check if required dependencies are available"""
        if not distribution:
            dist_check = self.check_current_distribution()
            distribution = dist_check["detected_distribution"]
            
        if not distribution or distribution not in self.compatibility_matrix:
            return {"error": "Unknown distribution"}
            
        dist_info = self.compatibility_matrix[distribution]
        dependencies = dist_info["dependencies"]
        
        result = {
            "distribution": distribution,
            "dependencies": {},
            "missing": [],
            "available": [],
            "recommendations": []
        }
        
        for dep, requirement in dependencies.items():
            try:
                # Try to import Python packages
                if dep.startswith("python") or dep.startswith("py3-"):
                    package_name = dep.replace("python3-", "").replace("py3-", "").replace("-", "_")
                    
                    if package_name == "gobject":
                        import gi
                        gi.require_version('Gtk', '4.0')
                        from gi.repository import Gtk
                        result["dependencies"][dep] = f"Available (Gtk {Gtk.get_major_version()}.{Gtk.get_minor_version()})"
                        result["available"].append(dep)
                    elif package_name == "dbus_next":
                        import dbus_next
                        result["dependencies"][dep] = f"Available ({dbus_next.__version__})"
                        result["available"].append(dep)
                    elif package_name == "pil" or package_name == "pillow":
                        import PIL
                        result["dependencies"][dep] = f"Available ({PIL.__version__})"
                        result["available"].append(dep)
                    else:
                        try:
                            __import__(package_name)
                            result["dependencies"][dep] = "Available"
                            result["available"].append(dep)
                        except ImportError:
                            result["dependencies"][dep] = "Missing"
                            result["missing"].append(dep)
                            
                # Check system packages
                elif dep in ["systemd", "gtk4", "libadwaita"]:
                    try:
                        subprocess.run(["pkg-config", "--exists", dep], 
                                     capture_output=True, check=True, timeout=5)
                        result["dependencies"][dep] = "Available"
                        result["available"].append(dep)
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        result["dependencies"][dep] = "Missing"
                        result["missing"].append(dep)
                        
                else:
                    # Generic package check
                    try:
                        subprocess.run([dep, "--version"], 
                                     capture_output=True, check=True, timeout=5)
                        result["dependencies"][dep] = "Available"
                        result["available"].append(dep)
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        result["dependencies"][dep] = "Missing"
                        result["missing"].append(dep)
                        
            except Exception as e:
                result["dependencies"][dep] = f"Error: {e}"
                result["missing"].append(dep)
                
        # Generate recommendations
        if result["missing"]:
            result["recommendations"].append(f"Install missing dependencies: {', '.join(result['missing'])}")
            
        return result
        
    def generate_install_commands(self, distribution: Optional[str] = None) -> Dict[str, List[str]]:
        """Generate installation commands for different distributions"""
        if not distribution:
            dist_check = self.check_current_distribution()
            distribution = dist_check["detected_distribution"]
            
        if not distribution or distribution not in self.compatibility_matrix:
            return {"error": "Unknown distribution"}
            
        commands = {
            "ubuntu": [
                "sudo apt update",
                "sudo apt install -y python3 python3-pip python3-venv python3-gi python3-gi-cairo",
                "sudo apt install -y gir1.2-gtk-4.0 gir1.2-adwaita-1",
                "sudo apt install -y python3-dev build-essential",
                "pip3 install --user dbus-next pillow"
            ],
            "debian": [
                "sudo apt update",
                "sudo apt install -y python3 python3-pip python3-venv python3-gi python3-gi-cairo",
                "sudo apt install -y gir1.2-gtk-4.0 gir1.2-adwaita-1",
                "sudo apt install -y python3-dev build-essential",
                "pip3 install --user dbus-next pillow"
            ],
            "fedora": [
                "sudo dnf update",
                "sudo dnf install -y python3 python3-pip python3-gobject python3-gobject-devel",
                "sudo dnf install -y gtk4 libadwaita python3-dev gcc",
                "pip3 install --user dbus-next pillow"
            ],
            "arch": [
                "sudo pacman -Syu",
                "sudo pacman -S python python-gobject gtk4 libadwaita",
                "sudo pacman -S python-pip python-dev gcc",
                "pip install --user dbus-next pillow"
            ],
            "opensuse": [
                "sudo zypper refresh",
                "sudo zypper install -y python3 python3-pip python3-gobject python3-gobject-devel",
                "sudo zypper install -y gtk4 libadwaita python3-devel gcc",
                "pip3 install --user dbus-next pillow"
            ],
            "gentoo": [
                "sudo emerge --sync",
                "sudo emerge dev-lang/python dev-python/pygobject",
                "sudo emerge x11-libs/gtk gui-libs/libadwaita",
                "sudo emerge dev-python/pip dev-python/dbus-next dev-python/pillow"
            ],
            "alpine": [
                "sudo apk update",
                "sudo apk add python3 py3-pip py3-gobject",
                "sudo apk add gtk4 libadwaita python3-dev gcc musl-dev",
                "pip3 install --user dbus-next pillow"
            ]
        }
        
        return {distribution: commands.get(distribution, [])}


def main():
    """Main compatibility checker function"""
    checker = LinuxCompatibilityChecker()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "info":
            info = checker.get_distribution_info()
            print(json.dumps(info, indent=2))
            
        elif command == "check":
            result = checker.check_current_distribution()
            print(json.dumps(result, indent=2))
            
        elif command == "deps":
            result = checker.check_dependencies()
            print(json.dumps(result, indent=2))
            
        elif command == "install":
            commands = checker.generate_install_commands()
            print(json.dumps(commands, indent=2))
            
        else:
            print("Usage: motion-compatibility [info|check|deps|install]")
            
    else:
        # Run full compatibility check
        print("Linux Distribution Compatibility Check")
        print("=" * 50)
        
        # Distribution info
        info = checker.get_distribution_info()
        print(f"Distribution: {info['distribution'].get('PRETTY_NAME', 'Unknown')}")
        print(f"Package Manager: {info['package_manager']}")
        print(f"Init System: {info['init_system']}")
        
        # Compatibility check
        result = checker.check_current_distribution()
        print(f"\nDetected: {result['detected_distribution']}")
        
        if result['compatibility']:
            comp = result['compatibility']
            print(f"Compatibility: {comp['compatibility']}")
            print(f"Notes: {comp['notes']}")
            
        # Dependencies check
        deps = checker.check_dependencies()
        print(f"\nDependencies Status:")
        print(f"Available: {len(deps['available'])}")
        print(f"Missing: {len(deps['missing'])}")
        
        if deps['missing']:
            print(f"Missing: {', '.join(deps['missing'])}")
            
        # Recommendations
        if result['recommendations']:
            print(f"\nRecommendations:")
            for rec in result['recommendations']:
                print(f"  - {rec}")
                
        # Install commands
        commands = checker.generate_install_commands()
        if commands and not commands.get('error'):
            dist = result['detected_distribution']
            if dist and dist in commands:
                print(f"\nInstallation Commands for {dist}:")
                for cmd in commands[dist]:
                    print(f"  {cmd}")


if __name__ == "__main__":
    main()
