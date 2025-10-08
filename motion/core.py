#!/usr/bin/env python3

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

# Check if dbus_next is available
try:
    from dbus_next.aio import MessageBus
    from dbus_next.constants import BusType
    from dbus_next import Variant
    DBUS_AVAILABLE = True
except ImportError:
    DBUS_AVAILABLE = False

APP_NAME = "systemd-motion"


def load_config() -> dict:
    config_path = Path.home() / ".config" / APP_NAME / "behavior.json"
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


def setup_logging() -> Path:
    state_dir = Path.home() / ".local" / "state" / APP_NAME
    state_dir.mkdir(parents=True, exist_ok=True)
    log_path = state_dir / "session.log"
    
    # Create a simple file logger
    logger = logging.getLogger('session_manager')
    logger.setLevel(logging.WARNING)
    
    if not logger.handlers:
        handler = logging.FileHandler(log_path, encoding="utf-8")
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return log_path


async def get_logind_idle_hint(bus: MessageBus) -> Optional[bool]:
    if not DBUS_AVAILABLE:
        return None
        
    try:
        introspect = await bus.introspect("org.freedesktop.login1", "/org/freedesktop/login1/session/self")
        obj = bus.get_proxy_object("org.freedesktop.login1", "/org/freedesktop/login1/session/self", introspect)
        props = obj.get_interface("org.freedesktop.DBus.Properties")
        value = await props.call_get("org.freedesktop.login1.Session", "IdleHint")
        if isinstance(value, Variant):
            return bool(value.value)
        return bool(value)
    except Exception:
        return None


async def simulate_user_activity_session(bus: MessageBus) -> bool:
    if not DBUS_AVAILABLE:
        return False
        
    try:
        introspect = await bus.introspect("org.freedesktop.ScreenSaver", "/org/freedesktop/ScreenSaver")
        obj = bus.get_proxy_object("org.freedesktop.ScreenSaver", "/org/freedesktop/ScreenSaver", introspect)
        iface = obj.get_interface("org.freedesktop.ScreenSaver")
        await iface.call_simulate_user_activity()
        return True
    except Exception:
        return False


async def monitor():
    config = load_config()
    log_path = setup_logging()
    logger = logging.getLogger('session_manager')
    
    idle_minutes = int(config.get("idle_minutes", 10))
    simulate_after_minutes = int(config.get("simulate_after_minutes", 5))
    simulate_activity = bool(config.get("simulate_activity", False))

    # Try to connect to D-Bus if available
    system_bus = None
    session_bus = None
    
    if DBUS_AVAILABLE:
        try:
            system_bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
            session_bus = await MessageBus(bus_type=BusType.SESSION).connect()
        except Exception as e:
            logger.error(f"D-Bus connection failed: {e}")
            return

    last_idle_state: Optional[bool] = None
    idle_since: Optional[float] = None
    check_interval_seconds = 30

    while True:
        try:
            idle_hint = None
            if system_bus:
                idle_hint = await get_logind_idle_hint(system_bus)
            
            now = time.time()

            if idle_hint is not None:
                if idle_hint:
                    if idle_since is None:
                        idle_since = now
                else:
                    idle_since = None

                # Only log state changes
                if last_idle_state != idle_hint:
                    state = "IDLE" if idle_hint else "ACTIVE"
                    if state == "IDLE":
                        logger.warning("Session idle detected")
                    last_idle_state = idle_hint

                if idle_hint and simulate_activity and session_bus:
                    idle_duration_minutes = ((now - idle_since) / 60.0) if idle_since is not None else 0.0
                    if idle_duration_minutes >= simulate_after_minutes:
                        ok = await simulate_user_activity_session(session_bus)
                        if not ok:
                            logger.error("Activity simulation failed")
                        # Reset timer
                        idle_since = now
            else:
                # No D-Bus available, just log periodic status
                if int(now) % 300 == 0:  # Every 5 minutes
                    logger.warning("Session monitor running (no D-Bus)")

        except Exception as e:
            logger.error(f"Monitor error: {e}")

        await asyncio.sleep(check_interval_seconds)


def main() -> None:
    try:
        asyncio.run(monitor())
    except KeyboardInterrupt:
        pass
    except Exception:
        pass


if __name__ == "__main__":
    main()
