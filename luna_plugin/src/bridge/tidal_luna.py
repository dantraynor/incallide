#!/usr/bin/env python3
"""
Tidal Luna Bridge
Interfaces with Tidal Luna application via AppleScript and system events
"""

import subprocess
import os
import time
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


class TidalLunaBridge:
    """Bridge to communicate with Tidal Luna application"""
    
    # Common Tidal app names to search for
    TIDAL_APP_NAMES = [
        "TIDAL",
        "Tidal Luna",
        "Tidal",
    ]
    
    def __init__(self):
        self.app_name = self._detect_tidal_app()
        self.is_running = False
        
        if self.app_name:
            logger.info(f"Detected Tidal app: {self.app_name}")
            self.is_running = self._check_if_running()
        else:
            logger.warning("Tidal Luna/TIDAL app not found on system")
    
    def _detect_tidal_app(self) -> Optional[str]:
        """Detect which Tidal app is installed"""
        for app_name in self.TIDAL_APP_NAMES:
            app_path = f"/Applications/{app_name}.app"
            if os.path.exists(app_path):
                return app_name
            
            # Check in user Applications folder
            user_app_path = os.path.expanduser(f"~/Applications/{app_name}.app")
            if os.path.exists(user_app_path):
                return app_name
        
        # Try to find via system_profiler (slower but thorough)
        try:
            result = subprocess.run(
                ["system_profiler", "SPApplicationsDataType", "-json"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                apps = data.get("SPApplicationsDataType", [])
                for app in apps:
                    app_name = app.get("_name", "")
                    if "tidal" in app_name.lower():
                        return app_name
        except Exception as e:
            logger.debug(f"Could not search via system_profiler: {e}")
        
        return None
    
    def _check_if_running(self) -> bool:
        """Check if Tidal app is currently running"""
        if not self.app_name:
            return False
        
        script = f'''
        tell application "System Events"
            set appList to name of every application process
            return "{self.app_name}" is in appList
        end tell
        '''
        
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True
            )
            return result.stdout.strip() == "true"
        except Exception as e:
            logger.error(f"Error checking if app is running: {e}")
            return False
    
    def launch_app(self) -> bool:
        """Launch Tidal Luna/TIDAL if not running"""
        if not self.app_name:
            logger.error("Cannot launch - Tidal app not found")
            return False
        
        if self._check_if_running():
            logger.info(f"{self.app_name} is already running")
            return True
        
        try:
            subprocess.run(["open", "-a", self.app_name], check=True)
            time.sleep(2)  # Give app time to launch
            self.is_running = True
            logger.info(f"Launched {self.app_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to launch {self.app_name}: {e}")
            return False
    
    def send_keystroke(self, key: str, modifiers: List[str] = None) -> bool:
        """
        Send a keystroke to Tidal app
        
        Args:
            key: The key to press (e.g., "space", "right arrow")
            modifiers: List of modifiers (e.g., ["command down", "shift down"])
        """
        if not self.app_name:
            logger.error("Cannot send keystroke - Tidal app not found")
            return False
        
        if not self._check_if_running():
            logger.warning(f"{self.app_name} is not running")
            return False
        
        # Build the modifier string
        modifier_str = ""
        if modifiers:
            modifier_str = f" using {{{', '.join(modifiers)}}}"
        
        script = f'''
        tell application "System Events"
            tell process "{self.app_name}"
                set frontmost to true
                keystroke {key}{modifier_str}
            end tell
        end tell
        '''
        
        try:
            subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                check=True
            )
            logger.debug(f"Sent keystroke: {key} with modifiers: {modifiers}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to send keystroke: {e}")
            return False
    
    def send_key_code(self, code: int, modifiers: List[str] = None) -> bool:
        """
        Send a key code to Tidal app
        
        Args:
            code: The key code (e.g., 49 for space, 124 for right arrow)
            modifiers: List of modifiers
        """
        if not self.app_name:
            logger.error("Cannot send key code - Tidal app not found")
            return False
        
        if not self._check_if_running():
            logger.warning(f"{self.app_name} is not running")
            return False
        
        # Build the modifier string
        modifier_str = ""
        if modifiers:
            modifier_str = f" using {{{', '.join(modifiers)}}}"
        
        script = f'''
        tell application "System Events"
            tell process "{self.app_name}"
                set frontmost to true
                key code {code}{modifier_str}
            end tell
        end tell
        '''
        
        try:
            subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                check=True
            )
            logger.debug(f"Sent key code: {code} with modifiers: {modifiers}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to send key code: {e}")
            return False
    
    def play_pause(self) -> bool:
        """Toggle play/pause in Tidal"""
        # Try space key (common play/pause shortcut)
        return self.send_key_code(49)  # Space key code
    
    def next_track(self) -> bool:
        """Skip to next track"""
        # Try Cmd+Right Arrow (common next track shortcut)
        return self.send_key_code(124, ["command down"])  # Right arrow with Cmd
    
    def previous_track(self) -> bool:
        """Go to previous track"""
        # Try Cmd+Left Arrow (common previous track shortcut)
        return self.send_key_code(123, ["command down"])  # Left arrow with Cmd
    
    def volume_up(self) -> bool:
        """Increase volume"""
        # Try Cmd+Up Arrow
        return self.send_key_code(126, ["command down"])  # Up arrow with Cmd
    
    def volume_down(self) -> bool:
        """Decrease volume"""
        # Try Cmd+Down Arrow
        return self.send_key_code(125, ["command down"])  # Down arrow with Cmd
    
    def search(self, query: str) -> bool:
        """
        Open search and type query
        
        Args:
            query: Search query string
        """
        if not self.app_name:
            return False
        
        # Focus the app first
        self.bring_to_front()
        time.sleep(0.5)
        
        # Send Cmd+F to open search (common shortcut)
        if self.send_key_code(3, ["command down"]):  # 'f' key with Cmd
            time.sleep(0.5)
            # Type the search query
            return self.send_keystroke(f'"{query}"')
        
        return False
    
    def bring_to_front(self) -> bool:
        """Bring Tidal app to front"""
        if not self.app_name:
            return False
        
        script = f'''
        tell application "{self.app_name}"
            activate
        end tell
        '''
        
        try:
            subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def get_window_title(self) -> Optional[str]:
        """
        Get the window title (might contain track info)
        """
        if not self.app_name or not self._check_if_running():
            return None
        
        script = f'''
        tell application "System Events"
            tell process "{self.app_name}"
                if exists window 1 then
                    return name of window 1
                else
                    return ""
                end if
            end tell
        end tell
        '''
        
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True
            )
            title = result.stdout.strip()
            return title if title else None
        except Exception as e:
            logger.error(f"Error getting window title: {e}")
            return None
    
    def quit_app(self) -> bool:
        """Quit Tidal app"""
        if not self.app_name:
            return False
        
        script = f'''
        tell application "{self.app_name}"
            quit
        end tell
        '''
        
        try:
            subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                check=True
            )
            self.is_running = False
            return True
        except subprocess.CalledProcessError:
            return False


# Test the bridge if run directly
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    bridge = TidalLunaBridge()
    
    if bridge.app_name:
        print(f"✓ Found Tidal app: {bridge.app_name}")
        
        if bridge._check_if_running():
            print("✓ App is running")
            
            # Test getting window title
            title = bridge.get_window_title()
            if title:
                print(f"Window title: {title}")
            
            # Test play/pause
            print("Testing play/pause...")
            if bridge.play_pause():
                print("✓ Play/pause command sent")
        else:
            print("App is not running. Launch it? (y/n)")
            if input().lower() == 'y':
                if bridge.launch_app():
                    print("✓ App launched")
    else:
        print("✗ Tidal app not found. Please install TIDAL or Tidal Luna.")