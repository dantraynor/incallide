#!/usr/bin/env python3
"""
Incallide Luna Plugin - Main Application
macOS companion app for Tidal Luna with media keys support
"""

import os
import sys
import time
import signal
import logging
import argparse
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bridge.tidal_luna import TidalLunaBridge
from macos.media_keys import MediaKeysHandler, MediaKey

# Setup logging
def setup_logging(level=logging.INFO):
    """Configure logging for the application"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                Path.home() / '.incallide-luna' / 'plugin.log',
                mode='a'
            )
        ]
    )
    return logging.getLogger(__name__)


class IncallideLunaPlugin:
    """Main application class for the Luna plugin"""
    
    def __init__(self, args):
        self.args = args
        self.logger = setup_logging(
            logging.DEBUG if args.debug else logging.INFO
        )
        
        # Create config directory
        self.config_dir = Path.home() / '.incallide-luna'
        self.config_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.bridge = None
        self.media_handler = None
        self.running = False
        
        self.logger.info("=" * 50)
        self.logger.info("Incallide Luna Plugin Starting...")
        self.logger.info("=" * 50)
    
    def initialize_components(self):
        """Initialize the bridge and media handler"""
        # Initialize Tidal Luna bridge
        self.logger.info("Initializing Tidal Luna bridge...")
        self.bridge = TidalLunaBridge()
        
        if not self.bridge.app_name:
            self.logger.error("❌ Tidal/TIDAL Luna not found on system!")
            self.logger.error("Please install TIDAL or Tidal Luna first.")
            return False
        
        self.logger.info(f"✓ Found: {self.bridge.app_name}")
        
        # Check if app is running
        if not self.bridge._check_if_running():
            if self.args.auto_launch:
                self.logger.info(f"Launching {self.bridge.app_name}...")
                if self.bridge.launch_app():
                    self.logger.info(f"✓ {self.bridge.app_name} launched")
                else:
                    self.logger.warning(f"⚠️  Could not launch {self.bridge.app_name}")
            else:
                self.logger.warning(f"⚠️  {self.bridge.app_name} is not running")
                self.logger.info("Tip: Use --auto-launch to start it automatically")
        else:
            self.logger.info(f"✓ {self.bridge.app_name} is running")
        
        # Initialize media keys handler
        self.logger.info("Initializing media keys handler...")
        self.media_handler = MediaKeysHandler(self.bridge)
        
        # Register callbacks for logging
        self.media_handler.register_callback(
            MediaKey.PLAY_PAUSE,
            lambda: self.logger.info("▶️ Play/Pause key pressed")
        )
        self.media_handler.register_callback(
            MediaKey.NEXT,
            lambda: self.logger.info("⏭ Next key pressed")
        )
        self.media_handler.register_callback(
            MediaKey.PREVIOUS,
            lambda: self.logger.info("⏮ Previous key pressed")
        )
        
        return True
    
    def start(self):
        """Start the plugin"""
        if not self.initialize_components():
            return False
        
        # Start media keys handler
        if self.media_handler.start():
            self.logger.info("✓ Media keys handler started")
            self.logger.info("")
            self.logger.info("🎵 Media Keys Active:")
            self.logger.info("  • Play/Pause: F8 or Play/Pause media key")
            self.logger.info("  • Next Track: F9 or Next media key")
            self.logger.info("  • Previous: F7 or Previous media key")
            self.logger.info("")
            self.logger.info("Press Ctrl+C to stop")
            self.logger.info("-" * 50)
            
            self.running = True
            return True
        else:
            self.logger.error("❌ Failed to start media keys handler")
            self.logger.error("Make sure to grant Accessibility permissions:")
            self.logger.error("System Preferences → Security & Privacy → Privacy → Accessibility")
            return False
    
    def stop(self):
        """Stop the plugin"""
        self.logger.info("\nShutting down...")
        self.running = False
        
        if self.media_handler:
            self.media_handler.stop()
            stats = self.media_handler.get_statistics()
            self.logger.info(f"Media keys handled: {stats['key_press_count']}")
        
        self.logger.info("✓ Plugin stopped")
    
    def run(self):
        """Main run loop"""
        if not self.start():
            return 1
        
        # Setup signal handlers
        def signal_handler(signum, frame):
            self.logger.info("\nReceived interrupt signal")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Main loop
        try:
            while self.running:
                time.sleep(1)
                
                # Periodically check if Tidal is still running
                if self.bridge and not self.bridge._check_if_running():
                    self.logger.warning(f"⚠️  {self.bridge.app_name} is no longer running")
                    
                    if self.args.auto_launch:
                        self.logger.info("Attempting to relaunch...")
                        self.bridge.launch_app()
                
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
        
        return 0
    
    def test_mode(self):
        """Run in test mode - test all functions"""
        self.logger.info("🧪 Running in test mode")
        
        if not self.initialize_components():
            return 1
        
        tests = [
            ("Bridge Detection", lambda: self.bridge.app_name is not None),
            ("App Running Check", lambda: self.bridge._check_if_running()),
            ("Media Handler Start", lambda: self.media_handler.start()),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                status = "✓" if result else "✗"
                self.logger.info(f"{status} {test_name}: {'PASS' if result else 'FAIL'}")
                results.append(result)
            except Exception as e:
                self.logger.error(f"✗ {test_name}: ERROR - {e}")
                results.append(False)
        
        # Test sending commands if all basic tests pass
        if all(results):
            self.logger.info("\n📝 Testing commands...")
            time.sleep(1)
            
            # Test play/pause
            self.logger.info("Testing play/pause...")
            if self.bridge.play_pause():
                self.logger.info("✓ Play/pause command sent")
            else:
                self.logger.error("✗ Play/pause command failed")
            
            time.sleep(1)
            
            # Get window title
            title = self.bridge.get_window_title()
            if title:
                self.logger.info(f"Window title: {title}")
        
        # Stop media handler
        if self.media_handler:
            self.media_handler.stop()
        
        passed = sum(results)
        total = len(results)
        self.logger.info(f"\n📊 Test Results: {passed}/{total} passed")
        
        return 0 if all(results) else 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Incallide Luna Plugin - Media keys for Tidal Luna"
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    parser.add_argument(
        '--auto-launch',
        action='store_true',
        help='Automatically launch Tidal if not running'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode'
    )
    parser.add_argument(
        '--menubar',
        action='store_true',
        help='Run with menu bar interface (coming soon)'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print("""
╔══════════════════════════════════════════════════════╗
║     🎵 Incallide Luna Plugin for macOS 🎵           ║
║     Media Keys Support for Tidal Luna               ║
╚══════════════════════════════════════════════════════╝
    """)
    
    # Create and run application
    app = IncallideLunaPlugin(args)
    
    if args.test:
        return app.test_mode()
    elif args.menubar:
        print("Menu bar mode coming soon!")
        return 0
    else:
        return app.run()


if __name__ == "__main__":
    sys.exit(main())