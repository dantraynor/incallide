# macOS Implementation Guide for Incallide

## Phase 1: Core macOS Audio Backend Implementation

### Step 1: Install macOS-specific Dependencies

Create a new `requirements_macos.txt` file with the following content:

```txt
# Core dependencies (keep existing)
tidalapi==0.7.6
rich==13.7.1
textual==0.63.6
python-dotenv==1.0.0
pillow>=9.1,<10.0

# macOS-specific dependencies
pyobjc-core==10.1
pyobjc-framework-AVFoundation==10.1
pyobjc-framework-MediaPlayer==10.1
pyobjc-framework-Cocoa==10.1
pyobjc-framework-CoreMedia==10.1
rumps==0.4.0
py2app==0.28.6
python-mpv==1.0.4  # Fallback audio backend
pynput==1.7.6  # For global media keys
plyer==2.1  # For notifications
```

### Step 2: Create macOS Audio Backend Module

Create `macos/audio_player.py`:

```python
"""
macOS Native Audio Player using AVFoundation
"""
import os
import threading
from typing import Optional, Callable
from urllib.parse import urlparse

try:
    from Foundation import NSURL, NSNotificationCenter
    from AVFoundation import (
        AVPlayer, AVPlayerItem, AVPlayerItemStatus,
        AVPlayerTimeControlStatus, CMTime, CMTimeMake
    )
    from AppKit import NSApplication
    MACOS_AVAILABLE = True
except ImportError:
    MACOS_AVAILABLE = False
    print("Warning: macOS frameworks not available, falling back to VLC")

class MacOSAudioPlayer:
    """Native macOS audio player using AVFoundation"""
    
    def __init__(self):
        if not MACOS_AVAILABLE:
            raise ImportError("macOS frameworks not available")
        
        self.player = AVPlayer.alloc().init()
        self.current_item = None
        self.is_playing = False
        self.volume = 70
        self.duration = 0
        self.position = 0
        
        # Callbacks
        self.on_track_end = None
        self.on_error = None
        
        # Setup observers
        self._setup_observers()
    
    def _setup_observers(self):
        """Setup AVPlayer observers for status changes"""
        # This would include KVO observers for player status
        pass
    
    def play_url(self, url: str) -> bool:
        """Play audio from URL"""
        try:
            # Create NSURL from string
            ns_url = NSURL.URLWithString_(url)
            if not ns_url:
                # Try as file URL if not a valid URL
                ns_url = NSURL.fileURLWithPath_(url)
            
            # Create player item
            self.current_item = AVPlayerItem.playerItemWithURL_(ns_url)
            
            # Replace current item
            self.player.replaceCurrentItemWithPlayerItem_(self.current_item)
            
            # Start playback
            self.player.play()
            self.is_playing = True
            
            return True
            
        except Exception as e:
            print(f"Error playing URL: {e}")
            if self.on_error:
                self.on_error(str(e))
            return False
    
    def pause(self):
        """Pause playback"""
        self.player.pause()
        self.is_playing = False
    
    def resume(self):
        """Resume playback"""
        self.player.play()
        self.is_playing = True
    
    def stop(self):
        """Stop playback"""
        self.player.pause()
        self.player.replaceCurrentItemWithPlayerItem_(None)
        self.is_playing = False
        self.current_item = None
    
    def set_volume(self, volume: int):
        """Set volume (0-100)"""
        self.volume = max(0, min(100, volume))
        self.player.setVolume_(self.volume / 100.0)
    
    def get_position(self) -> float:
        """Get current position (0.0 to 1.0)"""
        if not self.current_item:
            return 0.0
        
        current_time = self.player.currentTime()
        duration = self.current_item.duration()
        
        if duration.value > 0:
            return float(current_time.value) / float(duration.value)
        return 0.0
    
    def get_duration(self) -> int:
        """Get duration in seconds"""
        if not self.current_item:
            return 0
        
        duration = self.current_item.duration()
        if duration.value > 0:
            return int(duration.value / duration.timescale)
        return 0
    
    def seek(self, position: float):
        """Seek to position (0.0 to 1.0)"""
        if not self.current_item:
            return
        
        duration = self.current_item.duration()
        target_time = CMTimeMake(int(position * duration.value), duration.timescale)
        self.player.seekToTime_(target_time)
```

### Step 3: Create Media Keys Handler

Create `macos/media_keys.py`:

```python
"""
macOS Media Keys Handler
Handles play/pause, next, previous media keys
"""
import threading
from typing import Callable, Optional

try:
    from AppKit import NSApplication, NSEvent, NSSystemDefined
    from Cocoa import NSEventModifierFlagCommand, NSEventModifierFlagShift
    from pynput import keyboard
    MACOS_AVAILABLE = True
except ImportError:
    MACOS_AVAILABLE = False

class MediaKeysHandler:
    """Handle macOS media keys"""
    
    # Media key codes
    PLAY_PAUSE = 16
    NEXT = 17
    PREVIOUS = 18
    
    def __init__(self):
        if not MACOS_AVAILABLE:
            raise ImportError("macOS frameworks not available")
        
        self.callbacks = {
            'play_pause': None,
            'next': None,
            'previous': None
        }
        
        self.listener = None
        self._start_listener()
    
    def _start_listener(self):
        """Start listening for media keys"""
        def on_press(key):
            try:
                # Check for media keys
                if hasattr(key, 'vk'):
                    if key.vk == 179:  # Play/Pause
                        if self.callbacks['play_pause']:
                            self.callbacks['play_pause']()
                    elif key.vk == 176:  # Next
                        if self.callbacks['next']:
                            self.callbacks['next']()
                    elif key.vk == 177:  # Previous
                        if self.callbacks['previous']:
                            self.callbacks['previous']()
            except Exception as e:
                print(f"Error handling media key: {e}")
        
        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()
    
    def register_callback(self, action: str, callback: Callable):
        """Register callback for media key action"""
        if action in self.callbacks:
            self.callbacks[action] = callback
    
    def stop(self):
        """Stop listening for media keys"""
        if self.listener:
            self.listener.stop()
```

### Step 4: Create Now Playing Integration

Create `macos/now_playing.py`:

```python
"""
macOS Now Playing Integration
Updates Control Center and Touch Bar with current track info
"""
try:
    from MediaPlayer import (
        MPNowPlayingInfoCenter,
        MPMediaItemPropertyTitle,
        MPMediaItemPropertyArtist,
        MPMediaItemPropertyAlbumTitle,
        MPMediaItemPropertyPlaybackDuration,
        MPNowPlayingInfoPropertyElapsedPlaybackTime,
        MPNowPlayingInfoPropertyPlaybackRate
    )
    from Foundation import NSMutableDictionary
    MACOS_AVAILABLE = True
except ImportError:
    MACOS_AVAILABLE = False

class NowPlayingManager:
    """Manage Now Playing information for Control Center"""
    
    def __init__(self):
        if not MACOS_AVAILABLE:
            raise ImportError("macOS MediaPlayer framework not available")
        
        self.info_center = MPNowPlayingInfoCenter.defaultCenter()
    
    def update_now_playing(self, title: str, artist: str, album: str, 
                          duration: int, position: float = 0.0,
                          artwork_url: str = None):
        """Update Now Playing information"""
        info = NSMutableDictionary.alloc().init()
        
        # Set basic metadata
        info[MPMediaItemPropertyTitle] = title
        info[MPMediaItemPropertyArtist] = artist
        info[MPMediaItemPropertyAlbumTitle] = album
        info[MPMediaItemPropertyPlaybackDuration] = duration
        info[MPNowPlayingInfoPropertyElapsedPlaybackTime] = position * duration
        info[MPNowPlayingInfoPropertyPlaybackRate] = 1.0
        
        # TODO: Add artwork support
        # if artwork_url:
        #     self._set_artwork(info, artwork_url)
        
        self.info_center.setNowPlayingInfo_(info)
    
    def set_playback_state(self, is_playing: bool):
        """Update playback state"""
        if self.info_center.nowPlayingInfo():
            info = NSMutableDictionary.dictionaryWithDictionary_(
                self.info_center.nowPlayingInfo()
            )
            info[MPNowPlayingInfoPropertyPlaybackRate] = 1.0 if is_playing else 0.0
            self.info_center.setNowPlayingInfo_(info)
    
    def clear(self):
        """Clear Now Playing information"""
        self.info_center.setNowPlayingInfo_(None)
```

### Step 5: Create Notification Manager

Create `macos/notifications.py`:

```python
"""
macOS Notification Manager
Shows native notifications for track changes and events
"""
try:
    from Foundation import NSUserNotification, NSUserNotificationCenter
    from AppKit import NSImage
    import requests
    from io import BytesIO
    MACOS_AVAILABLE = True
except ImportError:
    MACOS_AVAILABLE = False
    # Fallback to plyer
    try:
        from plyer import notification
        PLYER_AVAILABLE = True
    except ImportError:
        PLYER_AVAILABLE = False

class NotificationManager:
    """Manage macOS notifications"""
    
    def __init__(self):
        self.use_native = MACOS_AVAILABLE
        self.use_plyer = PLYER_AVAILABLE and not MACOS_AVAILABLE
        
        if self.use_native:
            self.center = NSUserNotificationCenter.defaultUserNotificationCenter()
    
    def show_track_notification(self, title: str, artist: str, 
                               album: str = None, artwork_url: str = None):
        """Show notification for new track"""
        if self.use_native:
            notification = NSUserNotification.alloc().init()
            notification.setTitle_("Now Playing")
            notification.setSubtitle_(title)
            notification.setInformativeText_(f"{artist} - {album}" if album else artist)
            
            # TODO: Add artwork to notification
            # if artwork_url:
            #     self._set_notification_image(notification, artwork_url)
            
            self.center.deliverNotification_(notification)
            
        elif self.use_plyer:
            notification.notify(
                title="Now Playing",
                message=f"{title}\n{artist} - {album}" if album else f"{title}\n{artist}",
                app_name="Incallide",
                timeout=3
            )
    
    def show_message(self, title: str, message: str):
        """Show generic notification"""
        if self.use_native:
            notification = NSUserNotification.alloc().init()
            notification.setTitle_(title)
            notification.setInformativeText_(message)
            self.center.deliverNotification_(notification)
            
        elif self.use_plyer:
            notification.notify(
                title=title,
                message=message,
                app_name="Incallide",
                timeout=3
            )
```

### Step 6: Create Menu Bar Application

Create `macos/menubar_app.py`:

```python
"""
macOS Menu Bar Application
Provides quick access to player controls from the menu bar
"""
import rumps
import threading
from typing import Optional

class TidalMenuBarApp(rumps.App):
    """Menu bar application for Incallide"""
    
    def __init__(self, player_core):
        super().__init__("🎵", title=None)
        self.player = player_core
        self.setup_menu()
        
    def setup_menu(self):
        """Setup menu items"""
        self.menu = [
            rumps.MenuItem("Now Playing", callback=self.show_now_playing),
            rumps.separator,
            rumps.MenuItem("⏯ Play/Pause", callback=self.play_pause, key="space"),
            rumps.MenuItem("⏭ Next Track", callback=self.next_track, key="n"),
            rumps.MenuItem("⏮ Previous Track", callback=self.prev_track, key="p"),
            rumps.separator,
            rumps.MenuItem("🔍 Search...", callback=self.search, key="s"),
            rumps.separator,
            rumps.MenuItem("Volume", callback=None),
            rumps.SliderMenuItem(value=70, min_value=0, max_value=100, 
                               callback=self.volume_changed),
            rumps.separator,
            rumps.MenuItem("Preferences...", callback=self.preferences, key=","),
            rumps.separator,
            rumps.MenuItem("Quit", callback=self.quit_app, key="q")
        ]
    
    def show_now_playing(self, _):
        """Show current track info"""
        if self.player.current_track:
            track = self.player.current_track
            rumps.alert(
                title="Now Playing",
                message=f"{track['title']}\n{track['artist']}\n{track['album']}"
            )
        else:
            rumps.alert("Now Playing", "No track playing")
    
    def play_pause(self, _):
        """Toggle play/pause"""
        self.player.pause_resume()
        self.update_menu_state()
    
    def next_track(self, _):
        """Play next track"""
        self.player.next_track()
        self.update_menu_state()
    
    def prev_track(self, _):
        """Play previous track"""
        self.player.prev_track()
        self.update_menu_state()
    
    def search(self, _):
        """Open search dialog"""
        response = rumps.Window(
            title="Search Tidal",
            message="Enter search query:",
            default_text="",
            ok="Search",
            cancel="Cancel"
        ).run()
        
        if response.clicked:
            query = response.text
            if query:
                # Run search in background thread
                threading.Thread(
                    target=self.player.search_and_play,
                    args=(query,)
                ).start()
    
    def volume_changed(self, sender):
        """Handle volume slider change"""
        self.player.set_volume(sender.value)
    
    def preferences(self, _):
        """Open preferences window"""
        rumps.alert("Preferences", "Preferences window coming soon!")
    
    def quit_app(self, _):
        """Quit the application"""
        self.player.stop()
        rumps.quit_application()
    
    def update_menu_state(self):
        """Update menu items based on player state"""
        if self.player.is_playing:
            self.menu["⏯ Play/Pause"].title = "⏸ Pause"
        else:
            self.menu["⏯ Play/Pause"].title = "▶️ Play"
        
        if self.player.current_track:
            track = self.player.current_track
            self.menu["Now Playing"].title = f"🎵 {track['title'][:30]}..."
        else:
            self.menu["Now Playing"].title = "Now Playing"
```

## Phase 2: Integration with Existing Code

### Step 1: Create Audio Backend Abstraction

Create `core/audio_backend.py`:

```python
"""
Audio Backend Abstraction Layer
Allows switching between VLC, AVFoundation, and MPV
"""
from abc import ABC, abstractmethod
from typing import Optional

class AudioBackend(ABC):
    """Abstract base class for audio backends"""
    
    @abstractmethod
    def play_url(self, url: str) -> bool:
        """Play audio from URL"""
        pass
    
    @abstractmethod
    def pause(self):
        """Pause playback"""
        pass
    
    @abstractmethod
    def resume(self):
        """Resume playback"""
        pass
    
    @abstractmethod
    def stop(self):
        """Stop playback"""
        pass
    
    @abstractmethod
    def set_volume(self, volume: int):
        """Set volume (0-100)"""
        pass
    
    @abstractmethod
    def get_position(self) -> float:
        """Get current position (0.0 to 1.0)"""
        pass
    
    @abstractmethod
    def get_duration(self) -> int:
        """Get duration in seconds"""
        pass

class AudioBackendFactory:
    """Factory for creating appropriate audio backend"""
    
    @staticmethod
    def create_backend(preferred: str = "auto") -> AudioBackend:
        """Create audio backend based on platform and availability"""
        import platform
        
        if platform.system() == "Darwin":  # macOS
            try:
                from macos.audio_player import MacOSAudioPlayer
                return MacOSAudioPlayer()
            except ImportError:
                pass
        
        # Fallback to VLC
        try:
            from backends.vlc_backend import VLCBackend
            return VLCBackend()
        except ImportError:
            pass
        
        # Final fallback to MPV
        try:
            from backends.mpv_backend import MPVBackend
            return MPVBackend()
        except ImportError:
            raise RuntimeError("No audio backend available")
```

### Step 2: Modify Main Player Class

Update the existing player classes to use the abstraction:

```python
# In main.py, tidal_tui.py, etc.
from core.audio_backend import AudioBackendFactory

class TidalPlayer:
    def __init__(self):
        # ... existing code ...
        
        # Replace VLC initialization with:
        self.audio_backend = AudioBackendFactory.create_backend()
        
        # Platform-specific features
        self._init_platform_features()
    
    def _init_platform_features(self):
        """Initialize platform-specific features"""
        import platform
        
        if platform.system() == "Darwin":
            try:
                from macos.media_keys import MediaKeysHandler
                from macos.now_playing import NowPlayingManager
                from macos.notifications import NotificationManager
                
                # Setup media keys
                self.media_keys = MediaKeysHandler()
                self.media_keys.register_callback('play_pause', self.pause_resume)
                self.media_keys.register_callback('next', self.next_track)
                self.media_keys.register_callback('previous', self.prev_track)
                
                # Setup Now Playing
                self.now_playing = NowPlayingManager()
                
                # Setup notifications
                self.notifications = NotificationManager()
                
            except ImportError:
                print("macOS features not available")
```

## Phase 3: Build and Distribution

### Step 1: Create Setup Script for macOS

Create `setup_macos.py`:

```python
"""
py2app setup script for building macOS application
"""
from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'resources/icon.icns',
    'plist': {
        'CFBundleName': 'Incallide',
        'CFBundleDisplayName': 'Incallide - Tidal Player',
        'CFBundleIdentifier': 'com.incallide.tidalplayer',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2024',
        'NSHighResolutionCapable': True,
        'LSUIElement': False,  # Set to True for menu bar only app
        'NSAppleMusicUsageDescription': 'Incallide needs access to play music.',
    },
    'packages': ['tidalapi', 'rich', 'textual', 'vlc'],
    'includes': [
        'macos.audio_player',
        'macos.media_keys',
        'macos.now_playing',
        'macos.notifications',
        'macos.menubar_app'
    ],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

### Step 2: Create Makefile

Create `Makefile`:

```makefile
# Makefile for Incallide macOS build

.PHONY: all clean install build run test

# Variables
PYTHON = python3
VENV = venv_macos
APP_NAME = Incallide.app
DMG_NAME = Incallide-1.0.0.dmg

all: build

# Setup development environment
setup:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements_macos.txt

# Build macOS app
build: setup
	$(VENV)/bin/python setup_macos.py py2app

# Create DMG for distribution
dmg: build
	hdiutil create -volname "Incallide" -srcfolder dist/$(APP_NAME) -ov -format UDZO $(DMG_NAME)

# Run in development mode
run:
	$(VENV)/bin/python main.py

# Run menu bar app
menubar:
	$(VENV)/bin/python -m macos.menubar_app

# Run tests
test:
	$(VENV)/bin/pytest tests/

# Clean build artifacts
clean:
	rm -rf build dist *.egg-info
	rm -f $(DMG_NAME)
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Install to Applications folder
install: build
	cp -r dist/$(APP_NAME) /Applications/

# Uninstall from Applications folder
uninstall:
	rm -rf /Applications/$(APP_NAME)
```

### Step 3: Create Homebrew Formula

Create `homebrew/incallide.rb`:

```ruby
class Incallide < Formula
  desc "Native macOS terminal music player for Tidal"
  homepage "https://github.com/yourusername/incallide"
  url "https://github.com/yourusername/incallide/archive/v1.0.0.tar.gz"
  sha256 "YOUR_SHA256_HERE"
  license "MIT"

  depends_on "python@3.11"
  depends_on "mpv" => :optional

  def install
    virtualenv_install_with_resources
    
    # Install launch agent for menu bar app
    (prefix/"com.incallide.menubar.plist").write plist_content
  end

  def post_install
    system "#{bin}/incallide", "--setup"
  end

  service do
    run [opt_bin/"incallide", "--menubar"]
    keep_alive true
    log_path var/"log/incallide.log"
    error_log_path var/"log/incallide.error.log"
  end

  test do
    system "#{bin}/incallide", "--version"
  end

  private

  def plist_content
    <<~EOS
      <?xml version="1.0" encoding="UTF-8"?>
      <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
      <plist version="1.0">
      <dict>
        <key>Label</key>
        <string>com.incallide.menubar</string>
        <key>ProgramArguments</key>
        <array>
          <string>#{opt_bin}/incallide</string>
          <string>--menubar</string>
        </array>
        <key>RunAtLoad</key>
        <true/>
        <key>KeepAlive</key>
        <false/>
      </dict>
      </plist>
    EOS
  end
end
```

## Testing Checklist

### Functional Tests
- [ ] Audio playback works with AVFoundation
- [ ] VLC fallback works when AVFoundation unavailable
- [ ] Media keys respond correctly
- [ ] Now Playing shows in Control Center
- [ ] Notifications appear for track changes
- [ ] Menu bar app launches and controls work
- [ ] Search functionality works from menu bar
- [ ] Volume control works from menu bar

### Integration Tests
- [ ] Tidal authentication works
- [ ] Session persistence works
- [ ] Queue management works
- [ ] All three UI modes work (main, simple, enhanced)

### Performance Tests
- [ ] Memory usage < 100MB idle
- [ ] CPU usage < 5% during playback
- [ ] Launch time < 2 seconds
- [ ] No memory leaks during extended playback

### Compatibility Tests
- [ ] Works on Intel Macs
- [ ] Works on Apple Silicon (M1/M2/M3)
- [ ] Works on macOS 11 (Big Sur)
- [ ] Works on macOS 12 (Monterey)
- [ ] Works on macOS 13 (Ventura)
- [ ] Works on macOS 14 (Sonoma)

## Deployment Steps

1. **Development Build**
   ```bash
   make setup
   make run
   ```

2. **Test Menu Bar App**
   ```bash
   make menubar
   ```

3. **Build Application**
   ```bash
   make build
   ```

4. **Create DMG**
   ```bash
   make dmg
   ```

5. **Code Sign** (requires Apple Developer account)
   ```bash
   codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/Incallide.app
   ```

6. **Notarize** (for distribution outside App Store)
   ```bash
   xcrun altool --notarize-app --primary-bundle-id "com.incallide.tidalplayer" --username "your@email.com" --password "@keychain:AC_PASSWORD" --file Incallide-1.0.0.dmg
   ```

7. **Submit to Homebrew**
   ```bash
   brew tap homebrew/core
   brew create https://github.com/yourusername/incallide/archive/v1.0.0.tar.gz
   ```

## Next Steps

1. **Immediate Actions**
   - Review and approve this implementation guide
   - Set up macOS development environment
   - Start with Phase 1 implementation

2. **Short Term**
   - Implement core audio backend
   - Add media key support
   - Create menu bar app

3. **Medium Term**
   - Add Now Playing integration
   - Implement notifications
   - Create installer packages

4. **Long Term**
   - Submit to Homebrew
   - Create native SwiftUI app
   - Add iOS/iPadOS support via Catalyst