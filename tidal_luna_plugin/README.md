# 🖥️ Incallide Terminal Player Plugin for Tidal Luna

A plugin for Tidal Luna that adds a button to launch a beautiful terminal-based mini player. This gives you a lightweight, keyboard-driven interface to control your music while keeping Tidal Luna running in the background.

## ✨ Features

- **🎵 Terminal Mini Player** - Launch a compact terminal player with a single click
- **⌨️ Keyboard Controls** - Control playback without leaving your terminal
- **🔄 Real-time Sync** - Automatically syncs with Tidal Luna's current track
- **🎨 Beautiful UI** - Rich terminal interface with progress bars and track info
- **🚀 Lightweight** - Minimal resource usage compared to the full Tidal Luna UI
- **🔌 WebSocket Communication** - Real-time bidirectional communication

## 📦 Installation

### Method 1: Via Tidal Luna Plugin Store

1. Open Tidal Luna
2. Go to Settings → Plugins → Store
3. Search for "Incallide Terminal Player"
4. Click Install
5. Restart Tidal Luna

### Method 2: Manual Installation

1. **Download the plugin:**
```bash
git clone https://github.com/yourusername/incallide.git
cd incallide
```

2. **Copy plugin to Tidal Luna plugins folder:**
```bash
# macOS
cp -r tidal_luna_plugin ~/Library/Application\ Support/tidal-luna/plugins/incallide-terminal/

# Or if using portable Tidal Luna
cp -r tidal_luna_plugin /path/to/TidalLuna/plugins/incallide-terminal/
```

3. **Install Python dependencies for the terminal player:**
```bash
pip install websockets rich pynput
```

4. **Restart Tidal Luna**

## 🚀 Usage

### In Tidal Luna

1. Look for the **🖥️ Terminal** button in the player controls
2. Click the button to launch the terminal player
3. The terminal will open with the mini player interface

### Keyboard Shortcuts in Terminal Player

| Key | Action |
|-----|--------|
| `Space` | Play/Pause |
| `N` | Next Track |
| `P` | Previous Track |
| `+` | Volume Up |
| `-` | Volume Down |
| `Q` | Quit Terminal Player |

### Global Shortcut in Tidal Luna

- **Ctrl/Cmd + Shift + T** - Launch terminal player from anywhere in Tidal Luna

## ⚙️ Configuration

The plugin can be configured in Tidal Luna's settings:

1. Go to Settings → Plugins → Incallide Terminal Player
2. Configure options:
   - **WebSocket Port**: Port for communication (default: 9876)
   - **Auto-launch Terminal**: Automatically open terminal when clicking button
   - **Terminal Command**: Custom command to launch terminal

### Custom Terminal Command Examples

**For iTerm2:**
```bash
osascript -e 'tell application "iTerm" to create window with default profile command "cd ~/incallide && ./run_mini_player.sh"'
```

**For Alacritty:**
```bash
alacritty -e bash -c "cd ~/incallide && ./run_mini_player.sh"
```

**For Kitty:**
```bash
kitty -e bash -c "cd ~/incallide && ./run_mini_player.sh"
```

## 🏗️ Architecture

```
┌─────────────────────────┐
│     Tidal Luna          │
│  ┌─────────────────┐    │
│  │  Plugin Button  │    │
│  └────────┬────────┘    │
│           │             │
│  ┌────────▼────────┐    │
│  │  Plugin.js      │    │
│  └────────┬────────┘    │
└───────────┼─────────────┘
            │
     WebSocket (9876)
            │
┌───────────▼─────────────┐
│   Terminal Player       │
│  ┌─────────────────┐    │
│  │  mini_player.py │    │
│  └─────────────────┘    │
│                         │
│  Controls:              │
│  • Space: Play/Pause    │
│  • N: Next              │
│  • P: Previous          │
└─────────────────────────┘
```

## 📁 File Structure

```
tidal_luna_plugin/
├── manifest.json    # Plugin metadata and configuration
├── plugin.js        # Main plugin JavaScript
├── README.md        # This file
└── icon.png        # Plugin icon (optional)

incallide/
├── mini_player.py       # Terminal player application
├── run_mini_player.sh   # Launch script
└── requirements.txt     # Python dependencies
```

## 🔧 Development

### Building from Source

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/incallide.git
cd incallide
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Test the mini player standalone:**
```bash
python mini_player.py
```

### Plugin Development

To modify the plugin:

1. Edit `tidal_luna_plugin/plugin.js`
2. Update `tidal_luna_plugin/manifest.json` if needed
3. Reload the plugin in Tidal Luna (Settings → Plugins → Reload)

### Debugging

Enable debug mode in Tidal Luna:
1. Open Developer Tools (Ctrl/Cmd + Shift + I)
2. Check Console for plugin logs (filter by "Incallide")

## 🐛 Troubleshooting

### Terminal player doesn't launch

1. **Check Python installation:**
```bash
python3 --version  # Should be 3.7+
```

2. **Install required packages:**
```bash
pip install websockets rich pynput
```

3. **Check file permissions:**
```bash
chmod +x run_mini_player.sh
```

### Connection issues

1. **Check if port 9876 is available:**
```bash
lsof -i :9876
```

2. **Try a different port:**
   - Change in Tidal Luna plugin settings
   - Update `mini_player.py` to match

### Button doesn't appear

1. **Check plugin is loaded:**
   - Settings → Plugins → Installed Plugins
   - Should show "Incallide Terminal Player"

2. **Reload plugin:**
   - Settings → Plugins → Reload All

3. **Check console for errors:**
   - Open Developer Tools (Ctrl/Cmd + Shift + I)
   - Look for errors starting with "[Incallide]"

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Tidal Luna team for the plugin system
- Rich library for beautiful terminal UI
- The Incallide community

## 📮 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/incallide/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/incallide/discussions)

## 🗺️ Roadmap

- [ ] Album art display in terminal
- [ ] Lyrics display
- [ ] Queue management
- [ ] Search functionality
- [ ] Playlist support
- [ ] Discord Rich Presence
- [ ] Last.fm scrobbling
- [ ] Visualizer mode

---

Made with ❤️ for the Tidal Luna community