# Tidal Luna macOS Plugin/Companion App Plan

## Overview
Create a macOS-specific companion application that enhances Tidal Luna (the modded Tidal player) with native macOS features and system integration. This plugin will act as a bridge between Tidal Luna and macOS system services.

## Understanding Tidal Luna
Tidal Luna is a modified version of the official Tidal desktop app that removes certain restrictions and adds enhanced features. The plugin we're creating will:
- Monitor Tidal Luna's playback state
- Provide macOS system integration
- Add convenience features without modifying Tidal Luna itself

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     macOS System                        │
├─────────────────────────────────────────────────────────┤
│  Media Keys │ Control Center │ Notifications │ Spotlight│
└──────┬──────┴────────┬───────┴──────┬────────┴────┬─────┘
       │               │              │             │
       ▼               ▼              ▼             ▼
┌─────────────────────────────────────────────────────────┐
│           Incallide macOS Companion App                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Communication Bridge Layer              │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ • WebSocket Server (for real-time updates)      │   │
│  │ • HTTP API (for control commands)               │   │
│  │ • File Watcher (monitor Tidal Luna state)       │   │
│  │ • AppleScript Bridge                            │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    Tidal Luna                           │
│         (Modified Tidal Desktop Application)            │
└─────────────────────────────────────────────────────────┘
```

## Integration Methods

### Method 1: Browser Extension Approach
Since Tidal Luna is likely an Electron app (web-based), we can inject a browser extension or JavaScript that communicates with our macOS companion app.

### Method 2: Accessibility API Approach
Use macOS Accessibility APIs to read Tidal Luna's UI state and control it programmatically.

### Method 3: File System Monitoring
Monitor Tidal Luna's cache/state files to detect playback changes.

### Method 4: Network Interception
Monitor network traffic to detect what's playing (requires local proxy).

## Core Features

### 1. Media Key Integration
```python
# Pseudo-code for media key handling
class MediaKeyBridge:
    def on_play_pause(self):
        # Send play/pause command to Tidal Luna
        self.send_to_tidal_luna("toggle_playback")
    
    def on_next(self):
        # Send next track command
        self.send_to_tidal_luna("next_track")
    
    def on_previous(self):
        # Send previous track command
        self.send_to_tidal_luna("previous_track")
```

### 2. Now Playing Sync
```python
# Monitor Tidal Luna and update macOS Now Playing
class NowPlayingSync:
    def monitor_tidal_luna(self):
        # Watch for track changes
        current_track = self.get_current_track_from_tidal()
        self.update_macos_now_playing(current_track)
```

### 3. Menu Bar Companion
```
┌──────────────────────────┐
│ 🎵 Incallide            │
├──────────────────────────┤
│ ▶️ Playing: Track Name   │
│ 👤 Artist Name           │
│ 💿 Album Name            │
├──────────────────────────┤
│ ⏯  Play/Pause           │
│ ⏭  Next                 │
│ ⏮  Previous             │
├──────────────────────────┤
│ 🔍 Quick Search...       │
│ 📋 Current Queue         │
│ ❤️  Favorite             │
├──────────────────────────┤
│ 🎚  Volume: ████░░░ 70% │
├──────────────────────────┤
│ ⚙️  Preferences...       │
│ 🚪 Quit                  │
└──────────────────────────┘
```

## Implementation Plan

### Phase 1: Research & Proof of Concept
1. **Analyze Tidal Luna Structure**
   - Determine if it's Electron-based
   - Find data storage locations
   - Identify control mechanisms

2. **Create Basic Communication Bridge**
   - Test AppleScript control
   - Test Accessibility API access
   - Test file system monitoring

### Phase 2: Core Plugin Development

#### File Structure
```
incallide-luna-plugin/
├── src/
│   ├── main.py                 # Main application entry
│   ├── bridge/
│   │   ├── __init__.py
│   │   ├── tidal_luna.py       # Tidal Luna interface
│   │   ├── websocket_server.py # WebSocket communication
│   │   └── applescript.py      # AppleScript bridge
│   ├── macos/
│   │   ├── __init__.py
│   │   ├── media_keys.py       # Media key handler
│   │   ├── now_playing.py      # Now Playing updater
│   │   ├── notifications.py    # Notification manager
│   │   └── accessibility.py    # Accessibility API wrapper
│   ├── menubar/
│   │   ├── __init__.py
│   │   └── app.py              # Menu bar application
│   └── utils/
│       ├── __init__.py
│       ├── config.py           # Configuration manager
│       └── logger.py           # Logging utilities
├── scripts/
│   ├── inject.js               # JavaScript injection for Electron
│   └── control.applescript     # AppleScript commands
├── resources/
│   ├── icon.icns
│   └── Info.plist
├── tests/
├── requirements.txt
├── setup.py
└── README.md
```

#### Core Components

**1. Tidal Luna Bridge (`bridge/tidal_luna.py`)**
```python
import subprocess
import os
from typing import Optional, Dict, Any

class TidalLunaBridge:
    """Bridge to communicate with Tidal Luna"""
    
    def __init__(self):
        self.luna_path = self._find_tidal_luna()
        self.is_running = False
        
    def _find_tidal_luna(self) -> Optional[str]:
        """Find Tidal Luna installation"""
        possible_paths = [
            "/Applications/TIDAL.app",
            "/Applications/Tidal Luna.app",
            "~/Applications/TIDAL.app",
        ]
        for path in possible_paths:
            expanded = os.path.expanduser(path)
            if os.path.exists(expanded):
                return expanded
        return None
    
    def send_command(self, command: str) -> bool:
        """Send command to Tidal Luna via AppleScript"""
        script = f'''
        tell application "System Events"
            tell process "TIDAL"
                {command}
            end tell
        end tell
        '''
        try:
            subprocess.run(['osascript', '-e', script], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def get_current_track(self) -> Optional[Dict[str, Any]]:
        """Get current playing track information"""
        # Implementation depends on Tidal Luna's structure
        # Options:
        # 1. Read from window title
        # 2. Monitor network requests
        # 3. Read from cache files
        # 4. Use accessibility API
        pass
    
    def play_pause(self):
        """Toggle play/pause"""
        self.send_command('keystroke space')
    
    def next_track(self):
        """Skip to next track"""
        self.send_command('key code 124 using {command down}')  # Cmd+Right
    
    def previous_track(self):
        """Go to previous track"""
        self.send_command('key code 123 using {command down}')  # Cmd+Left
```

**2. WebSocket Server for Real-time Updates (`bridge/websocket_server.py`)**
```python
import asyncio
import websockets
import json
from typing import Set

class TidalLunaWebSocketServer:
    """WebSocket server for real-time communication"""
    
    def __init__(self, bridge):
        self.bridge = bridge
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        
    async def register(self, websocket):
        """Register a new client"""
        self.clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)
    
    async def broadcast_track_update(self, track_info):
        """Broadcast track update to all clients"""
        if self.clients:
            message = json.dumps({
                'type': 'track_update',
                'data': track_info
            })
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )
    
    async def handle_message(self, websocket, path):
        """Handle incoming WebSocket messages"""
        await self.register(websocket)
        try:
            async for message in websocket:
                data = json.loads(message)
                command = data.get('command')
                
                if command == 'play_pause':
                    self.bridge.play_pause()
                elif command == 'next':
                    self.bridge.next_track()
                elif command == 'previous':
                    self.bridge.previous_track()
                elif command == 'get_status':
                    status = self.bridge.get_current_track()
                    await websocket.send(json.dumps(status))
        except websockets.exceptions.ConnectionClosed:
            pass
    
    async def start_server(self, host='localhost', port=9876):
        """Start the WebSocket server"""
        async with websockets.serve(self.handle_message, host, port):
            await asyncio.Future()  # Run forever
```

**3. Media Keys Handler (`macos/media_keys.py`)**
```python
from pynput import keyboard
from typing import Callable, Dict

class MediaKeysHandler:
    """Handle macOS media keys and forward to Tidal Luna"""
    
    def __init__(self, bridge):
        self.bridge = bridge
        self.listener = None
        
    def start(self):
        """Start listening for media keys"""
        def on_press(key):
            try:
                if hasattr(key, 'vk'):
                    if key.vk == 179:  # Play/Pause
                        self.bridge.play_pause()
                    elif key.vk == 176:  # Next
                        self.bridge.next_track()
                    elif key.vk == 177:  # Previous
                        self.bridge.previous_track()
            except Exception as e:
                print(f"Error handling media key: {e}")
        
        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()
    
    def stop(self):
        """Stop listening for media keys"""
        if self.listener:
            self.listener.stop()
```

**4. Menu Bar App (`menubar/app.py`)**
```python
import rumps
import threading
from bridge.tidal_luna import TidalLunaBridge

class IncallideLunaMenuBar(rumps.App):
    """Menu bar companion for Tidal Luna"""
    
    def __init__(self):
        super().__init__("🎵", title=None)
        self.bridge = TidalLunaBridge()
        self.setup_menu()
        self.start_monitoring()
        
    def setup_menu(self):
        """Setup menu items"""
        self.menu = [
            rumps.MenuItem("Now Playing", callback=None),
            rumps.separator,
            rumps.MenuItem("⏯ Play/Pause", callback=self.play_pause, key="space"),
            rumps.MenuItem("⏭ Next", callback=self.next_track, key="n"),
            rumps.MenuItem("⏮ Previous", callback=self.prev_track, key="p"),
            rumps.separator,
            rumps.MenuItem("🔍 Quick Search", callback=self.quick_search, key="f"),
            rumps.MenuItem("❤️ Favorite", callback=self.favorite_track, key="l"),
            rumps.separator,
            rumps.MenuItem("🚀 Launch Tidal Luna", callback=self.launch_tidal),
            rumps.separator,
            rumps.MenuItem("⚙️ Preferences", callback=self.preferences, key=","),
            rumps.MenuItem("📖 About", callback=self.about),
            rumps.separator,
            rumps.MenuItem("Quit", callback=self.quit_app, key="q")
        ]
    
    def start_monitoring(self):
        """Start monitoring Tidal Luna"""
        def monitor():
            while True:
                track = self.bridge.get_current_track()
                if track:
                    self.update_now_playing(track)
                time.sleep(1)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def update_now_playing(self, track):
        """Update Now Playing menu item"""
        if track:
            title = track.get('title', 'Unknown')[:30]
            artist = track.get('artist', 'Unknown')[:20]
            self.menu["Now Playing"].title = f"🎵 {title} - {artist}"
    
    def play_pause(self, _):
        """Toggle play/pause"""
        self.bridge.play_pause()
    
    def next_track(self, _):
        """Next track"""
        self.bridge.next_track()
    
    def prev_track(self, _):
        """Previous track"""
        self.bridge.previous_track()
    
    def quick_search(self, _):
        """Open quick search dialog"""
        response = rumps.Window(
            title="Quick Search",
            message="Search in Tidal Luna:",
            default_text="",
            ok="Search",
            cancel="Cancel"
        ).run()
        
        if response.clicked and response.text:
            # Send search to Tidal Luna
            self.bridge.send_command(f'keystroke "f" using {{command down}}')
            self.bridge.send_command(f'keystroke "{response.text}"')
    
    def favorite_track(self, _):
        """Favorite current track"""
        self.bridge.send_command('keystroke "l" using {command down}')
    
    def launch_tidal(self, _):
        """Launch Tidal Luna"""
        import subprocess
        if self.bridge.luna_path:
            subprocess.run(['open', self.bridge.luna_path])
        else:
            rumps.alert("Tidal Luna not found", 
                       "Please install Tidal Luna first")
    
    def preferences(self, _):
        """Open preferences"""
        rumps.alert("Preferences", "Preferences coming soon!")
    
    def about(self, _):
        """Show about dialog"""
        rumps.alert(
            "Incallide Luna Plugin",
            "macOS companion app for Tidal Luna\n\n"
            "Version 1.0.0\n"
            "© 2024"
        )
    
    def quit_app(self, _):
        """Quit application"""
        rumps.quit_application()
```

### Phase 3: Advanced Features

#### 1. Spotlight Integration
Create a Spotlight importer that indexes Tidal Luna's library for quick search.

#### 2. Shortcuts/Automator Actions
```applescript
-- Example Shortcuts action
on run {input, parameters}
    tell application "Incallide Luna Plugin"
        play track input
    end tell
    return input
end run
```

#### 3. Touch Bar Support (for compatible MacBooks)
```python
# Touch Bar integration using PyTouchBar
from PyTouchBar import TouchBar, TouchBarButton, TouchBarSlider

class TidalLunaTouchBar:
    def __init__(self, bridge):
        self.bridge = bridge
        self.setup_touchbar()
    
    def setup_touchbar(self):
        self.touchbar = TouchBar([
            TouchBarButton("⏮", action=self.bridge.previous_track),
            TouchBarButton("⏯", action=self.bridge.play_pause),
            TouchBarButton("⏭", action=self.bridge.next_track),
            TouchBarSlider(min=0, max=100, action=self.set_volume)
        ])
```

## Installation & Setup

### For Users

1. **Install Tidal Luna**
   ```bash
   # Download and install Tidal Luna from GitHub
   ```

2. **Install Incallide Luna Plugin**
   ```bash
   # Download latest release
   curl -L https://github.com/yourusername/incallide-luna/releases/latest/download/IncallideLuna.dmg -o IncallideLuna.dmg
   
   # Mount and install
   hdiutil attach IncallideLuna.dmg
   cp -r /Volumes/IncallideLuna/IncallideLuna.app /Applications/
   hdiutil detach /Volumes/IncallideLuna
   ```

3. **Grant Permissions**
   - System Preferences → Security & Privacy → Accessibility
   - Add IncallideLuna.app

4. **Launch**
   ```bash
   open /Applications/IncallideLuna.app
   ```

### For Developers

1. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/incallide-luna
   cd incallide-luna
   ```

2. **Setup Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run in Development**
   ```bash
   python src/main.py
   ```

4. **Build Application**
   ```bash
   python setup.py py2app
   ```

## Configuration File

Create `~/.incallide-luna/config.json`:
```json
{
  "tidal_luna_path": "/Applications/TIDAL.app",
  "enable_media_keys": true,
  "enable_now_playing": true,
  "enable_notifications": true,
  "enable_menubar": true,
  "menubar_icon": "musical_note",
  "update_interval": 1000,
  "websocket_port": 9876,
  "log_level": "INFO"
}
```

## Testing Strategy

### Unit Tests
- Bridge communication tests
- Media key handling tests
- WebSocket server tests

### Integration Tests
- Tidal Luna detection
- Command execution
- Now Playing updates

### End-to-End Tests
- Full playback control flow
- Menu bar interactions
- System integration

## Security Considerations

1. **Code Signing**
   - Sign with Developer ID for distribution
   - Notarize for Gatekeeper

2. **Sandboxing**
   - Limited file system access
   - Network access only to localhost

3. **Privacy**
   - No data collection
   - Local processing only
   - Optional crash reporting

## Distribution

### GitHub Releases
- Automated builds with GitHub Actions
- DMG and ZIP formats
- Auto-updater support

### Homebrew Cask
```ruby
cask "incallide-luna" do
  version "1.0.0"
  sha256 "..."
  
  url "https://github.com/yourusername/incallide-luna/releases/download/v#{version}/IncallideLuna.dmg"
  name "Incallide Luna Plugin"
  desc "macOS companion app for Tidal Luna"
  homepage "https://github.com/yourusername/incallide-luna"
  
  app "IncallideLuna.app"
  
  zap trash: [
    "~/Library/Preferences/com.incallide.luna.plist",
    "~/.incallide-luna",
  ]
end
```

## Roadmap

### Version 1.0 (MVP)
- ✅ Media key support
- ✅ Menu bar app
- ✅ Basic playback control
- ✅ Now Playing sync

### Version 1.1
- ⬜ Spotlight integration
- ⬜ Shortcuts support
- ⬜ Touch Bar support
- ⬜ Notification center widget

### Version 1.2
- ⬜ Lyrics display
- ⬜ Discord Rich Presence
- ⬜ Last.fm scrobbling
- ⬜ Custom themes

### Version 2.0
- ⬜ Multi-account support
- ⬜ Queue management
- ⬜ Playlist sync
- ⬜ iOS companion app

## Support & Documentation

### User Guide
- Installation instructions
- Permission setup
- Troubleshooting guide
- FAQ

### Developer Documentation
- API reference
- Plugin development
- Contributing guidelines
- Architecture overview

## Conclusion

This plugin approach provides a non-invasive way to add macOS-specific features to Tidal Luna without modifying the original application. It acts as a companion that enhances the user experience with native macOS integration while respecting the integrity of Tidal Luna.