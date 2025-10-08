import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, GLib, Gio
import json
import subprocess
import os
from pathlib import Path
import threading
import time

class MotionWindow(Gtk.Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("System Session Manager")
        self.set_default_size(400, 300)
        self.set_resizable(False)
        self.set_decorated(False)  # No window decorations
        self.set_skip_taskbar_hint(True)  # Hide from taskbar
        
        # Load config
        self.config = self.load_config()
        
        # Create main UI
        self.create_ui()
        
        # Start status monitoring
        self.update_status()
        GLib.timeout_add_seconds(2, self.update_status)
    
    def load_config(self):
        config_path = Path.home() / ".config" / "systemd-user" / "behavior.json"
        if config_path.exists():
            try:
                return json.loads(config_path.read_text())
            except Exception:
                pass
        return {
            "idle_minutes": 10,
            "simulate_after_minutes": 5,
            "simulate_activity": False,
        }
    
    def save_config(self):
        config_path = Path.home() / ".config" / "systemd-user" / "behavior.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(self.config, indent=2))
    
    def create_ui(self):
        # Main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        
        # Hidden title - minimal UI
        title = Gtk.Label(label="Session Manager")
        title.set_css_classes(["title-3"])
        main_box.append(title)
        
        # Status section - minimal
        status_frame = Gtk.Frame()
        status_frame.set_label("Status")
        status_frame.set_margin_bottom(10)
        
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        status_box.set_margin_start(10)
        status_box.set_margin_end(10)
        status_box.set_margin_top(10)
        status_box.set_margin_bottom(10)
        
        self.status_label = Gtk.Label()
        self.status_label.set_hexpand(True)
        status_box.append(self.status_label)
        
        self.start_button = Gtk.Button(label="Start")
        self.start_button.connect("clicked", self.on_start_clicked)
        status_box.append(self.start_button)
        
        self.stop_button = Gtk.Button(label="Stop")
        self.stop_button.connect("clicked", self.on_stop_clicked)
        status_box.append(self.stop_button)
        
        status_frame.set_child(status_box)
        main_box.append(status_frame)
        
        # Configuration section - hidden
        config_frame = Gtk.Frame()
        config_frame.set_label("Settings")
        config_frame.set_margin_bottom(10)
        
        config_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        config_box.set_margin_start(10)
        config_box.set_margin_end(10)
        config_box.set_margin_top(10)
        config_box.set_margin_bottom(10)
        
        # Idle threshold - hidden
        idle_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        idle_label = Gtk.Label(label="Timeout (min):")
        idle_label.set_hexpand(True)
        idle_box.append(idle_label)
        
        self.idle_spin = Gtk.SpinButton()
        self.idle_spin.set_adjustment(Gtk.Adjustment(value=self.config["idle_minutes"], lower=1, upper=60, step_increment=1))
        self.idle_spin.connect("value-changed", self.on_config_changed)
        idle_box.append(self.idle_spin)
        config_box.append(idle_box)
        
        # Simulate activity toggle - hidden
        simulate_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        simulate_label = Gtk.Label(label="Auto-resume:")
        simulate_label.set_hexpand(True)
        simulate_box.append(simulate_label)
        
        self.simulate_switch = Gtk.Switch()
        self.simulate_switch.set_active(self.config["simulate_activity"])
        self.simulate_switch.connect("state-set", self.on_config_changed)
        simulate_box.append(self.simulate_switch)
        config_box.append(simulate_box)
        
        # Simulate after minutes - hidden
        simulate_after_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        simulate_after_label = Gtk.Label(label="Delay (min):")
        simulate_after_label.set_hexpand(True)
        simulate_after_box.append(simulate_after_label)
        
        self.simulate_after_spin = Gtk.SpinButton()
        self.simulate_after_spin.set_adjustment(Gtk.Adjustment(value=self.config["simulate_after_minutes"], lower=1, upper=30, step_increment=1))
        self.simulate_after_spin.connect("value-changed", self.on_config_changed)
        simulate_after_box.append(self.simulate_after_spin)
        config_box.append(simulate_after_box)
        
        config_frame.set_child(config_box)
        main_box.append(config_frame)
        
        # Log section - hidden
        log_frame = Gtk.Frame()
        log_frame.set_label("Session Log")
        
        log_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        log_box.set_margin_start(10)
        log_box.set_margin_end(10)
        log_box.set_margin_top(10)
        log_box.set_margin_bottom(10)
        
        self.log_text = Gtk.TextView()
        self.log_text.set_editable(False)
        self.log_text.set_vexpand(True)
        
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.log_text)
        scrolled_window.set_min_content_height(150)
        log_box.append(scrolled_window)
        
        # Log refresh button
        refresh_button = Gtk.Button(label="Refresh Log")
        refresh_button.connect("clicked", self.refresh_log)
        log_box.append(refresh_button)
        
        log_frame.set_child(log_box)
        main_box.append(log_frame)
        
        self.set_child(main_box)
    
    def on_start_clicked(self, button):
        def start_service():
            try:
                subprocess.run(["systemctl", "--user", "start", "systemd-user.service"], check=True)
                GLib.idle_add(self.show_message, "Started")
            except subprocess.CalledProcessError:
                GLib.idle_add(self.show_message, "Start failed")
        
        threading.Thread(target=start_service, daemon=True).start()
    
    def on_stop_clicked(self, button):
        def stop_service():
            try:
                subprocess.run(["systemctl", "--user", "stop", "systemd-user.service"], check=True)
                GLib.idle_add(self.show_message, "Stopped")
            except subprocess.CalledProcessError:
                GLib.idle_add(self.show_message, "Stop failed")
        
        threading.Thread(target=stop_service, daemon=True).start()
    
    def on_config_changed(self, widget):
        self.config["idle_minutes"] = int(self.idle_spin.get_value())
        self.config["simulate_activity"] = self.simulate_switch.get_active()
        self.config["simulate_after_minutes"] = int(self.simulate_after_spin.get_value())
        
        # Save config and restart service if running
        self.save_config()
        self.restart_service_if_running()
    
    def restart_service_if_running(self):
        def restart():
            try:
                result = subprocess.run(["systemctl", "--user", "is-active", "systemd-user.service"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    subprocess.run(["systemctl", "--user", "restart", "systemd-user.service"], check=True)
                    GLib.idle_add(self.show_message, "Updated")
            except subprocess.CalledProcessError:
                pass
        
        threading.Thread(target=restart, daemon=True).start()
    
    def update_status(self):
        def check_status():
            try:
                result = subprocess.run(["systemctl", "--user", "is-active", "systemd-user.service"], 
                                      capture_output=True, text=True)
                is_active = result.returncode == 0
                
                GLib.idle_add(self.update_status_ui, is_active)
            except subprocess.CalledProcessError:
                GLib.idle_add(self.update_status_ui, False)
        
        threading.Thread(target=check_status, daemon=True).start()
        return True  # Continue timer
    
    def update_status_ui(self, is_active):
        if is_active:
            self.status_label.set_text("Status: Running")
            self.status_label.set_css_classes(["success"])
            self.start_button.set_sensitive(False)
            self.stop_button.set_sensitive(True)
        else:
            self.status_label.set_text("Status: Stopped")
            self.status_label.set_css_classes(["error"])
            self.start_button.set_sensitive(True)
            self.stop_button.set_sensitive(False)
        
        self.refresh_log()
    
    def refresh_log(self, button=None):
        log_path = Path.home() / ".local" / "state" / "systemd-user" / "session.log"
        
        def load_log():
            try:
                if log_path.exists():
                    content = log_path.read_text()
                    GLib.idle_add(self.update_log_display, content)
                else:
                    GLib.idle_add(self.update_log_display, "No log file found")
            except Exception as e:
                GLib.idle_add(self.update_log_display, f"Error reading log: {e}")
        
        threading.Thread(target=load_log, daemon=True).start()
    
    def update_log_display(self, content):
        buffer = self.log_text.get_buffer()
        buffer.set_text(content)
        
        # Scroll to bottom
        end_iter = buffer.get_end_iter()
        self.log_text.scroll_to_iter(end_iter, 0.0, False, 0.0, 0.0)
    
    def show_message(self, message):
        # Update the status label with the message
        self.status_label.set_text(f"Status: {message}")


class MotionApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='org.systemd.session-manager')
        self.connect('activate', self.on_activate)
    
    def on_activate(self, app):
        self.win = MotionWindow(application=app)
        self.win.present()


def main():
    app = MotionApp()
    return app.run()