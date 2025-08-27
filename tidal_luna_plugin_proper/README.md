# Incallide Terminal Player Plugin for Tidal Luna

A Tidal Luna plugin that adds a button to launch a beautiful terminal-based mini player. This gives you a lightweight, keyboard-driven interface to control your music while keeping Tidal Luna running in the background.

## 📦 Installation

### From Tidal Luna Plugin Store

1. Open Tidal Luna
2. Go to Settings → Plugins → Store
3. Search for "Incallide Terminal Player"
4. Click Install

### Manual Installation

1. Download the plugin from releases
2. Install via URL in Tidal Luna:
   ```
   https://github.com/yourusername/incallide/releases/download/latest/luna.incallide-terminal
   ```

## 🚀 Setup

### 1. Install Python Dependencies

The terminal player requires Python 3.9+ and some packages:

```bash
pip install websockets rich pynput
```

### 2. Install Terminal Player Files

Clone or download the Incallide repository:

```bash
git clone https://github.com/yourusername/incallide.git ~/incallide
cd ~/incallide
chmod +x run_mini_player.sh
```

### 3. Configure Plugin (Optional)

In Tidal Luna:
1. Go to Settings → Plugins → Incallide Terminal Player
2. Configure:
   - WebSocket Port (default: 9876)
   - Terminal Application (Terminal, iTerm2, Alacritty, Kitty)
   - Script Path (default: ~/incallide/run_mini_player.sh)

## 🎮 Usage

### Launch Terminal Player

**Option 1: Click the Terminal Button**
- Look for the Terminal button in player controls
- Click to launch the mini player

**Option 2: Keyboard Shortcut**
- Press `Ctrl/Cmd + Shift + T` anywhere in Tidal Luna

### Terminal Player Controls

| Key | Action |
|-----|--------|
| `Space` | Play/Pause |
| `N` | Next Track |
| `P` | Previous Track |
| `+` | Volume Up |
| `-` | Volume Down |
| `Q` | Quit Terminal Player |

## 🏗️ Plugin Structure

This plugin follows the official Tidal Luna plugin structure:

```
IncallideTerminal/
├── package.json       # Plugin metadata
├── src/
│   ├── index.ts      # Main plugin logic
│   └── Settings.tsx  # Settings UI component
```

## 🔧 Development

### Building from Source

1. Clone the luna-template repository:
```bash
git clone https://github.com/Inrixia/luna-template.git
cd luna-template
```

2. Copy this plugin to the plugins directory:
```bash
cp -r tidal_luna_plugin_proper/IncallideTerminal plugins/
```

3. Install dependencies:
```bash
pnpm install
```

4. Build and watch for changes:
```bash
pnpm run watch
```

5. Test in Tidal Luna via the DEV store

### Plugin API Usage

This plugin uses the following Tidal Luna APIs:
- `@luna/core` - Core plugin functionality
- `@luna/lib` - Media item and Redux store access
- `@luna/ui` - Settings UI components

## 🔌 How It Works

1. **WebSocket Server**: Plugin starts a WebSocket server on port 9876
2. **Terminal Launch**: Clicking the button launches the terminal player script
3. **Real-time Sync**: Terminal player connects via WebSocket for track updates
4. **Bidirectional Control**: Commands from terminal are sent back to Tidal Luna

## 🐛 Troubleshooting

### Terminal doesn't launch
- Check Python is installed: `python3 --version`
- Verify script exists: `ls ~/incallide/run_mini_player.sh`
- Check script permissions: `chmod +x ~/incallide/run_mini_player.sh`

### Connection issues
- Check port 9876 is available: `lsof -i :9876`
- Try a different port in settings
- Ensure WebSocket server started (check Tidal Luna console)

### Button doesn't appear
- Reload plugins: Settings → Plugins → Reload
- Check console for errors: Developer Tools (Ctrl/Cmd + Shift + I)

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- [Tidal Luna](https://github.com/Inrixia/TidaLuna) by Inrixia
- [luna-template](https://github.com/Inrixia/luna-template) for plugin structure
- Rich library for terminal UI

## 📮 Support

- Issues: [GitHub Issues](https://github.com/yourusername/incallide/issues)
- Tidal Luna Discord: [Join Discord](https://discord.gg/tidalluna)

---

Made with ❤️ for the Tidal Luna community