# 🎵 Incallide Luna Plugin for macOS

A lightweight macOS companion app that adds media key support and system integration to Tidal Luna (or the official TIDAL app).

## ✨ Features

### Current Features (v1.0.0)
- **🎹 Media Keys Support** - Control Tidal Luna with your Mac's media keys
  - Play/Pause (F8 or dedicated media key)
  - Next Track (F9 or dedicated media key)
  - Previous Track (F7 or dedicated media key)
- **🔌 AppleScript Bridge** - Programmatic control of Tidal Luna
- **🔍 Auto-Detection** - Automatically finds Tidal/Tidal Luna installation
- **🚀 Auto-Launch** - Optionally launch Tidal when plugin starts

### Coming Soon
- 📊 Menu Bar App with quick controls
- 🎵 Now Playing sync to Control Center
- 📱 Touch Bar support (for compatible MacBooks)
- 🔔 Track change notifications
- 🔍 Spotlight integration
- ⚡ Shortcuts app support

## 📋 Requirements

- macOS 11.0 (Big Sur) or later
- Python 3.9 or later
- TIDAL or Tidal Luna installed
- Accessibility permissions (for media keys)

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/incallide.git
cd incallide/luna_plugin
```

2. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Grant Accessibility Permissions:**
   - Open System Preferences → Security & Privacy → Privacy → Accessibility
   - Click the lock to make changes
   - Add Terminal (or your terminal app) to the list
   - Check the box to enable

### Running the Plugin

**Basic usage:**
```bash
python src/main.py
```

**With auto-launch (starts Tidal if not running):**
```bash
python src/main.py --auto-launch
```

**Debug mode (verbose logging):**
```bash
python src/main.py --debug
```

**Test mode (verify setup):**
```bash
python src/main.py --test
```

## 🎮 Usage

Once running, the plugin will:
1. Detect your Tidal/Tidal Luna installation
2. Start listening for media keys
3. Forward commands to Tidal Luna

### Supported Media Keys

| Key | Action | Alternative |
|-----|--------|-------------|
| Play/Pause | Toggle playback | F8 |
| Next | Skip to next track | F9 |
| Previous | Go to previous track | F7 |

## 🏗️ Architecture

```
luna_plugin/
├── src/
│   ├── main.py              # Main application entry point
│   ├── bridge/
│   │   └── tidal_luna.py    # AppleScript bridge to Tidal
│   └── macos/
│       └── media_keys.py    # Media key handler
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### How It Works

1. **Detection**: The plugin searches for Tidal/Tidal Luna in standard macOS application locations
2. **Bridge**: Uses AppleScript to send commands to Tidal Luna
3. **Media Keys**: Captures system media key events using `pynput`
4. **Forwarding**: Translates media key presses to Tidal Luna commands

## 🐛 Troubleshooting

### Media keys not working

1. **Check Accessibility permissions:**
   ```bash
   # Check if Terminal has accessibility access
   sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db \
     "SELECT client FROM access WHERE service='kTCCServiceAccessibility';"
   ```

2. **Verify Tidal is detected:**
   ```bash
   python src/main.py --test
   ```

3. **Check for conflicting apps:**
   - Quit other media apps that might capture media keys (Spotify, Apple Music, etc.)

### Tidal Luna not found

1. **Check installation path:**
   - Default: `/Applications/TIDAL.app`
   - User: `~/Applications/TIDAL.app`

2. **Verify app name:**
   - The plugin looks for "TIDAL", "Tidal", and "Tidal Luna"

### Commands not working

1. **Ensure Tidal has focus:**
   - The plugin brings Tidal to front when sending commands
   - Some commands may require the app to be active

2. **Check macOS version:**
   - Requires macOS 11.0 or later
   - Some features may vary by macOS version

## 🔧 Configuration

Configuration file location: `~/.incallide-luna/config.json`

Example configuration:
```json
{
  "auto_launch": true,
  "suppress_native_media_keys": true,
  "debug": false,
  "log_file": "~/.incallide-luna/plugin.log"
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Tidal Luna community for the modded player
- pynput library for media key capture
- rumps for menu bar app framework (coming soon)

## 📮 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/incallide/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/incallide/discussions)

## 🗺️ Roadmap

### Version 1.1 (Next Release)
- [ ] Menu bar app with controls
- [ ] Now Playing in Control Center
- [ ] Basic notifications

### Version 1.2
- [ ] Spotlight search integration
- [ ] Shortcuts app actions
- [ ] Touch Bar support

### Version 2.0
- [ ] Full GUI preferences
- [ ] Multiple player support
- [ ] Custom keyboard shortcuts
- [ ] Discord Rich Presence

## ⚠️ Disclaimer

This is an unofficial plugin and is not affiliated with TIDAL or Tidal Luna. Use at your own risk.

---

Made with ❤️ for the macOS music community