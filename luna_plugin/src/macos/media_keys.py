#!/usr/bin/env python3
"""
macOS Media Keys Handler
Captures system media keys and forwards commands to Tidal Luna
"""

import logging
import threading
import time
from typing import Callable, Dict, Optional
from enum import Enum

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("Warning: pynput not available. Media keys will not work.")

try:
    # Try to import macOS-specific modules for better integration
    from AppKit import NSApplication, NSApp
    from PyObjCTools import AppHelper
    MACOS_NATIVE_AVAILABLE = True
except ImportError:
    MACOS_NATIVE_AVAILABLE = False

logger = logging.getLogger(__name__)


class MediaKey(Enum):
    """Media key types"""
    PLAY_PAUSE = "play_pause"
    NEXT = "next"
    PREVIOUS = "previous"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    MUTE = "mute"


class MediaKeysHandler:
    """
    Handle macOS media keys and forward to Tidal Luna
    
    This handler captures system media keys (F7-F12 on Mac keyboards)
    and forwards the commands to the Tidal Luna bridge.
    """
    
    # Media key codes for macOS
    # These are the virtual key codes for media keys
    MEDIA_KEY_CODES = {
        # F7-F12 keys (media keys on Mac keyboards)
        177: MediaKey.PREVIOUS,     # F7 - Previous track
        176: MediaKey.NEXT,         # F9 - Next track
        179: MediaKey.PLAY_PAUSE,   # F8 - Play/Pause
        
        # Alternative codes (may vary by keyboard)
        # 20: MediaKey.PREVIOUS,     # Previous (some keyboards)
        # 19: MediaKey.NEXT,         # Next (some keyboards)  
        # 16: MediaKey.PLAY_PAUSE,   # Play/Pause (some keyboards)
    }
    
    def __init__(self, bridge=None):
        """
        Initialize the media keys handler
        
        Args:
            bridge: TidalLunaBridge instance for sending commands
        """
        self.bridge = bridge
        self.listener = None
        self.callbacks: Dict[MediaKey, Optional[Callable]] = {
            MediaKey.PLAY_PAUSE: None,
            MediaKey.NEXT: None,
            MediaKey.PREVIOUS: None,
            MediaKey.VOLUME_UP: None,
            MediaKey.VOLUME_DOWN: None,
            MediaKey.MUTE: None,
        }
        self.is_running = False
        self.suppress_native = True  # Whether to suppress native media key handling
        
        # Statistics
        self.key_press_count = 0
        self.last_key_time = 0
        
        logger.info("MediaKeysHandler initialized")
    
    def set_bridge(self, bridge):
        """Set or update the Tidal Luna bridge"""
        self.bridge = bridge
        logger.info("Bridge set for MediaKeysHandler")
    
    def register_callback(self, key: MediaKey, callback: Callable):
        """
        Register a callback for a specific media key
        
        Args:
            key: MediaKey enum value
            callback: Function to call when key is pressed
        """
        self.callbacks[key] = callback
        logger.debug(f"Registered callback for {key.value}")
    
    def _handle_media_key(self, media_key: MediaKey):
        """
        Handle a media key press
        
        Args:
            media_key: The MediaKey that was pressed
        """
        # Update statistics
        self.key_press_count += 1
        current_time = time.time()
        
        # Prevent double-presses (debounce)
        if current_time - self.last_key_time < 0.2:  # 200ms debounce
            logger.debug(f"Ignoring rapid key press for {media_key.value}")
            return
        
        self.last_key_time = current_time
        
        logger.info(f"Media key pressed: {media_key.value}")
        
        # Call registered callback if exists
        if self.callbacks.get(media_key):
            try:
                self.callbacks[media_key]()
            except Exception as e:
                logger.error(f"Error in callback for {media_key.value}: {e}")
        
        # Forward to bridge if available
        if self.bridge:
            try:
                if media_key == MediaKey.PLAY_PAUSE:
                    self.bridge.play_pause()
                elif media_key == MediaKey.NEXT:
                    self.bridge.next_track()
                elif media_key == MediaKey.PREVIOUS:
                    self.bridge.previous_track()
                elif media_key == MediaKey.VOLUME_UP:
                    self.bridge.volume_up()
                elif media_key == MediaKey.VOLUME_DOWN:
                    self.bridge.volume_down()
            except Exception as e:
                logger.error(f"Error forwarding {media_key.value} to bridge: {e}")
    
    def _on_press(self, key):
        """
        Handle key press events from pynput
        
        Args:
            key: The key that was pressed
        """
        try:
            # Check if it's a media key by virtual key code
            if hasattr(key, 'vk') and key.vk:
                vk = key.vk
                
                # Check our media key mapping
                if vk in self.MEDIA_KEY_CODES:
                    media_key = self.MEDIA_KEY_CODES[vk]
                    self._handle_media_key(media_key)
                    
                    # Suppress the native handling if configured
                    if self.suppress_native:
                        return False  # This should suppress the key
                
                # Log unknown media keys for debugging
                elif vk in range(160, 200):  # Range where media keys typically are
                    logger.debug(f"Unknown media key with vk={vk}")
            
            # Also check for function keys with media functions
            if hasattr(key, 'char'):
                return  # Regular character key, ignore
                
        except AttributeError:
            pass  # Not a special key
        except Exception as e:
            logger.error(f"Error processing key press: {e}")
    
    def start(self):
        """Start listening for media keys"""
        if not PYNPUT_AVAILABLE:
            logger.error("pynput is not available. Cannot start media key listener.")
            return False
        
        if self.is_running:
            logger.warning("Media keys handler is already running")
            return True
        
        try:
            # Create and start the listener
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                suppress=False  # Don't suppress all keys, just media keys
            )
            
            # Start listener in daemon mode
            self.listener.daemon = True
            self.listener.start()
            
            self.is_running = True
            logger.info("Media keys handler started")
            
            # Log instructions for the user
            logger.info("Media keys mapped:")
            logger.info("  F7 or Previous Track key -> Previous track")
            logger.info("  F8 or Play/Pause key -> Play/Pause")
            logger.info("  F9 or Next Track key -> Next track")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start media keys handler: {e}")
            self.is_running = False
            return False
    
    def stop(self):
        """Stop listening for media keys"""
        if not self.is_running:
            logger.warning("Media keys handler is not running")
            return
        
        try:
            if self.listener:
                self.listener.stop()
                self.listener = None
            
            self.is_running = False
            logger.info(f"Media keys handler stopped. Total keys handled: {self.key_press_count}")
            
        except Exception as e:
            logger.error(f"Error stopping media keys handler: {e}")
    
    def get_statistics(self) -> Dict:
        """Get handler statistics"""
        return {
            "is_running": self.is_running,
            "key_press_count": self.key_press_count,
            "last_key_time": self.last_key_time,
            "suppress_native": self.suppress_native,
            "has_bridge": self.bridge is not None
        }


class GlobalMediaKeysHandler(MediaKeysHandler):
    """
    Enhanced media keys handler with global hotkey support
    
    This version can also register global hotkeys for additional control
    """
    
    def __init__(self, bridge=None):
        super().__init__(bridge)
        self.hotkeys = {}
        
    def register_hotkey(self, key_combination: str, callback: Callable):
        """
        Register a global hotkey
        
        Args:
            key_combination: Key combination string (e.g., "<cmd>+<shift>+p")
            callback: Function to call when hotkey is pressed
        """
        if not PYNPUT_AVAILABLE:
            logger.error("pynput not available, cannot register hotkey")
            return False
        
        try:
            from pynput import keyboard
            
            # Parse and register the hotkey
            hotkey = keyboard.HotKey(
                keyboard.HotKey.parse(key_combination),
                callback
            )
            
            self.hotkeys[key_combination] = hotkey
            logger.info(f"Registered hotkey: {key_combination}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register hotkey {key_combination}: {e}")
            return False


# Test the handler if run directly
if __name__ == "__main__":
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Import the bridge
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from bridge.tidal_luna import TidalLunaBridge
    
    print("=== Media Keys Handler Test ===")
    print("This will capture media keys and forward them to Tidal Luna")
    print("Press Ctrl+C to stop\n")
    
    # Create bridge and handler
    bridge = TidalLunaBridge()
    handler = MediaKeysHandler(bridge)
    
    # Add some callbacks for testing
    def on_play_pause():
        print("▶️ Play/Pause pressed")
    
    def on_next():
        print("⏭ Next pressed")
    
    def on_previous():
        print("⏮ Previous pressed")
    
    handler.register_callback(MediaKey.PLAY_PAUSE, on_play_pause)
    handler.register_callback(MediaKey.NEXT, on_next)
    handler.register_callback(MediaKey.PREVIOUS, on_previous)
    
    # Start the handler
    if handler.start():
        print("✓ Media keys handler started successfully")
        print("Try pressing media keys (Play/Pause, Next, Previous)")
        print("Press Ctrl+C to stop\n")
        
        try:
            # Keep the program running
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\nStopping...")
            handler.stop()
            
            # Print statistics
            stats = handler.get_statistics()
            print(f"\nStatistics:")
            print(f"  Total key presses: {stats['key_press_count']}")
            
    else:
        print("✗ Failed to start media keys handler")
        print("Make sure you have granted accessibility permissions if on macOS")