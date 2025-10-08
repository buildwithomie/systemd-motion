#!/usr/bin/env python3

import asyncio
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add the motion module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motion.__main__ import (
    load_config, setup_logging, get_logind_idle_hint, 
    simulate_user_activity_session, monitor
)
from motion.debug import MotionDebugger


class TestMotionCore(unittest.TestCase):
    """Test core motion functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.test_config = {
            "idle_minutes": 5,
            "simulate_after_minutes": 2,
            "simulate_activity": False,
        }
        
    def test_load_config_default(self):
        """Test default config loading"""
        with patch('motion.__main__.Path.home') as mock_home:
            mock_home.return_value = Path('/tmp')
            
            # Test with non-existent config
            with patch('motion.__main__.Path.exists', return_value=False):
                config = load_config()
                self.assertEqual(config["idle_minutes"], 10)
                self.assertEqual(config["simulate_after_minutes"], 5)
                self.assertFalse(config["simulate_activity"])
                
    def test_load_config_file(self):
        """Test config loading from file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text(json.dumps(self.test_config))
            
            with patch('motion.__main__.Path.home') as mock_home:
                mock_home.return_value = Path(temp_dir)
                
                with patch('motion.__main__.Path.exists', return_value=True):
                    with patch('motion.__main__.Path.read_text', return_value=json.dumps(self.test_config)):
                        config = load_config()
                        self.assertEqual(config["idle_minutes"], 5)
                        self.assertEqual(config["simulate_after_minutes"], 2)
                        self.assertFalse(config["simulate_activity"])
                        
    def test_setup_logging(self):
        """Test logging setup"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('motion.__main__.Path.home') as mock_home:
                mock_home.return_value = Path(temp_dir)
                
                log_path = setup_logging()
                self.assertTrue(log_path.exists())
                self.assertEqual(log_path.name, "activity.log")
                
                # Test log writing
                import logging
                test_logger = logging.getLogger()
                test_logger.info("Test log message")
                
                log_content = log_path.read_text()
                self.assertIn("Test log message", log_content)


class TestMotionDbus(unittest.TestCase):
    """Test D-Bus functionality"""
    
    @patch('motion.__main__.MessageBus')
    async def test_get_logind_idle_hint_success(self, mock_message_bus):
        """Test successful idle hint retrieval"""
        # Mock the D-Bus connection and calls
        mock_bus = MagicMock()
        mock_message_bus.return_value.connect.return_value = mock_bus
        
        mock_introspect = MagicMock()
        mock_bus.introspect.return_value = mock_introspect
        
        mock_obj = MagicMock()
        mock_bus.get_proxy_object.return_value = mock_obj
        
        mock_props = MagicMock()
        mock_obj.get_interface.return_value = mock_props
        
        from dbus_next import Variant
        mock_props.call_get.return_value = Variant('b', True)
        
        result = await get_logind_idle_hint(mock_bus)
        self.assertTrue(result)
        
    @patch('motion.__main__.MessageBus')
    async def test_get_logind_idle_hint_error(self, mock_message_bus):
        """Test idle hint retrieval with error"""
        mock_bus = MagicMock()
        mock_bus.introspect.side_effect = Exception("D-Bus error")
        
        result = await get_logind_idle_hint(mock_bus)
        self.assertIsNone(result)
        
    @patch('motion.__main__.MessageBus')
    async def test_simulate_user_activity_success(self, mock_message_bus):
        """Test successful user activity simulation"""
        mock_bus = MagicMock()
        
        mock_introspect = MagicMock()
        mock_bus.introspect.return_value = mock_introspect
        
        mock_obj = MagicMock()
        mock_bus.get_proxy_object.return_value = mock_obj
        
        mock_iface = MagicMock()
        mock_obj.get_interface.return_value = mock_iface
        
        mock_iface.call_simulate_user_activity.return_value = None
        
        result = await simulate_user_activity_session(mock_bus)
        self.assertTrue(result)
        
    @patch('motion.__main__.MessageBus')
    async def test_simulate_user_activity_error(self, mock_message_bus):
        """Test user activity simulation with error"""
        mock_bus = MagicMock()
        mock_bus.introspect.side_effect = Exception("ScreenSaver not available")
        
        result = await simulate_user_activity_session(mock_bus)
        self.assertFalse(result)


class TestMotionDebugger(unittest.TestCase):
    """Test debugging functionality"""
    
    def setUp(self):
        """Setup test debugger"""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.temp_dir = Path(temp_dir)
            with patch('motion.debug.Path.home') as mock_home:
                mock_home.return_value = self.temp_dir
                self.debugger = MotionDebugger()
                
    def test_check_system_requirements(self):
        """Test system requirements check"""
        results = self.debugger.check_system_requirements()
        
        self.assertIn("python_version", results)
        self.assertIn("platform", results)
        self.assertIn("system_info", results)
        self.assertIn("dependencies", results)
        self.assertIn("permissions", results)
        self.assertIn("services", results)
        self.assertIn("errors", results)
        
    def test_check_file_permissions(self):
        """Test file permissions check"""
        # Create test directories and files
        config_dir = self.temp_dir / ".config" / "motion"
        state_dir = self.temp_dir / ".local" / "state" / "motion"
        share_dir = self.temp_dir / ".local" / "share" / "motion"
        
        config_dir.mkdir(parents=True, exist_ok=True)
        state_dir.mkdir(parents=True, exist_ok=True)
        share_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = config_dir / "config.json"
        config_file.write_text('{"test": "config"}')
        
        log_file = state_dir / "activity.log"
        log_file.write_text("test log content\n")
        
        results = self.debugger.check_file_permissions()
        
        self.assertIn("config directory", results)
        self.assertIn("state directory", results)
        self.assertIn("share directory", results)
        self.assertIn("activity log", results)
        self.assertIn("config file", results)
        
    def test_analyze_logs(self):
        """Test log analysis"""
        # Create test log file
        log_dir = self.temp_dir / ".local" / "state" / "motion"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / "activity.log"
        test_log_content = """2024-01-01 10:00:00 INFO motion started
2024-01-01 10:01:00 INFO state=ACTIVE
2024-01-01 10:05:00 INFO state=IDLE
2024-01-01 10:06:00 ERROR Failed to read IdleHint
2024-01-01 10:07:00 INFO state=ACTIVE
"""
        log_file.write_text(test_log_content)
        
        results = self.debugger.analyze_logs()
        
        self.assertTrue(results["log_exists"])
        self.assertEqual(results["total_lines"], 5)
        self.assertEqual(results["error_count"], 1)
        self.assertEqual(len(results["recent_entries"]), 5)
        self.assertEqual(results["activity_pattern"]["state_changes"], 3)


class TestMotionIntegration(unittest.TestCase):
    """Integration tests for motion"""
    
    @patch('motion.__main__.MessageBus')
    @patch('motion.__main__.setup_logging')
    @patch('motion.__main__.load_config')
    async def test_monitor_basic_flow(self, mock_load_config, mock_setup_logging, mock_message_bus):
        """Test basic monitor flow"""
        # Setup mocks
        mock_load_config.return_value = {
            "idle_minutes": 10,
            "simulate_after_minutes": 5,
            "simulate_activity": False,
        }
        
        mock_log_path = Path("/tmp/test.log")
        mock_setup_logging.return_value = mock_log_path
        
        # Mock D-Bus
        mock_system_bus = MagicMock()
        mock_session_bus = MagicMock()
        mock_message_bus.side_effect = [mock_system_bus, mock_session_bus]
        
        # Mock idle hint
        with patch('motion.__main__.get_logind_idle_hint') as mock_idle_hint:
            mock_idle_hint.return_value = False
            
            # Mock sleep to prevent infinite loop
            with patch('asyncio.sleep') as mock_sleep:
                mock_sleep.side_effect = [None, Exception("Test exit")]
                
                try:
                    await monitor()
                except Exception as e:
                    if "Test exit" not in str(e):
                        raise


class TestLinuxCompatibility(unittest.TestCase):
    """Test Linux distribution compatibility"""
    
    def test_ubuntu_compatibility(self):
        """Test Ubuntu-specific functionality"""
        # This would test Ubuntu-specific features
        # For now, just verify we can import required modules
        try:
            import dbus_next
            import gi
            self.assertTrue(True, "Ubuntu dependencies available")
        except ImportError as e:
            self.fail(f"Ubuntu dependency missing: {e}")
            
    def test_debian_compatibility(self):
        """Test Debian compatibility"""
        # Similar to Ubuntu but for Debian
        try:
            import dbus_next
            import gi
            self.assertTrue(True, "Debian dependencies available")
        except ImportError as e:
            self.fail(f"Debian dependency missing: {e}")
            
    def test_arch_compatibility(self):
        """Test Arch Linux compatibility"""
        # Test Arch-specific behavior
        try:
            import dbus_next
            import gi
            self.assertTrue(True, "Arch dependencies available")
        except ImportError as e:
            self.fail(f"Arch dependency missing: {e}")


def run_tests():
    """Run all tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestMotionCore))
    test_suite.addTest(unittest.makeSuite(TestMotionDbus))
    test_suite.addTest(unittest.makeSuite(TestMotionDebugger))
    test_suite.addTest(unittest.makeSuite(TestMotionIntegration))
    test_suite.addTest(unittest.makeSuite(TestLinuxCompatibility))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
