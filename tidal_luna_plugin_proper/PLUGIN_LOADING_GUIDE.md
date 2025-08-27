# Tidal Luna Plugin Loading Guide

## Dev Server Status
✅ **Dev server is running on port 8765**

The Incallide Terminal plugin has been successfully built and is being served at:
- **URL**: http://localhost:8765
- **Plugin File**: http://localhost:8765/luna.incallide-terminal.mjs
- **Store Info**: http://localhost:8765/store.json

## How to Load the Plugin in Tidal Luna

### Method 1: DEV Store (Recommended for Testing)

1. **Open Tidal Luna**
   - Launch the Tidal desktop application

2. **Access Luna Settings**
   - Click on your profile icon or settings menu
   - Navigate to "Luna Settings" or "Plugins"

3. **Enable Developer Mode**
   - Look for a "Developer Mode" toggle and enable it
   - This will show the DEV store option

4. **Add DEV Store URL**
   - In the Plugin Store section, look for "Add DEV Store" or "Custom Store"
   - Enter the URL: `http://localhost:8765`
   - Click "Add" or "Connect"

5. **Install the Plugin**
   - The "Incallide Terminal" plugin should appear in the available plugins list
   - Click "Install" or "Enable"
   - The plugin will be loaded and the Terminal button should appear in the player controls

### Method 2: Direct Plugin Loading

If Tidal Luna supports direct plugin URLs:

1. **Open Luna Settings**
2. **Go to Plugins section**
3. **Look for "Load from URL" or "Add Plugin"**
4. **Enter**: `http://localhost:8765/luna.incallide-terminal.mjs`
5. **Click Load/Add**

### Method 3: Manual Installation

If the above methods don't work:

1. **Download the plugin file**:
   ```bash
   curl -O http://localhost:8765/luna.incallide-terminal.mjs
   curl -O http://localhost:8765/luna.incallide-terminal.json
   ```

2. **Copy to Luna plugins directory**:
   - On macOS: `~/Library/Application Support/TIDAL/plugins/`
   - On Windows: `%APPDATA%\TIDAL\plugins\`
   - On Linux: `~/.config/TIDAL/plugins/`

3. **Restart Tidal Luna**

## Verifying the Plugin is Loaded

Once loaded, you should see:
1. **Terminal Button**: A new "Terminal" button in the player controls
2. **Keyboard Shortcut**: Press `Ctrl/Cmd + Shift + T` to launch the terminal player
3. **Console Log**: Open DevTools (F12) and check for: `[IncallideTerminal] Incallide Terminal Player plugin loaded!`

## Using the Plugin

### Launching the Terminal Player

1. **Click the Terminal button** in the player controls, OR
2. **Press `Ctrl/Cmd + Shift + T`**

This will attempt to:
- Connect to the terminal player via WebSocket (port 9876)
- Launch the terminal player via HTTP request (port 9877)

### Manual Terminal Player Launch

If automatic launch doesn't work, run this in a terminal:
```bash
cd ~/incallide && ./run_mini_player.sh
```

Or directly:
```bash
python3 ~/incallide/mini_player.py
```

## Troubleshooting

### Plugin Not Showing in Store
- Ensure the dev server is running: `cd tidal_luna_plugin_proper && pnpm run serve`
- Check the server is accessible: `curl http://localhost:8765/store.json`
- Try a different port if 8765 is blocked

### Plugin Not Loading
- Check browser console for errors (F12 in Tidal Luna)
- Verify WebSocket connectivity on port 9876
- Ensure Python dependencies are installed for the terminal player

### Terminal Player Not Launching
- Manually start the terminal player first
- Check that the launcher service is running on port 9877
- Verify Python 3 is installed and in PATH

## Development Workflow

### Making Changes
1. Edit files in `plugins/IncallideTerminal/src/`
2. The watcher will automatically rebuild (if `pnpm run watch` is running)
3. Refresh Tidal Luna to reload the plugin

### Viewing Logs
- Plugin logs: Open DevTools console in Tidal Luna (F12)
- Build logs: Check the terminal running `pnpm run watch`
- Server logs: Check the terminal running `pnpm run serve`

## Current Server Status

```
Server: http://localhost:8765
Status: ✅ Running
Plugin: luna.incallide-terminal.mjs
Store: http://localhost:8765/store.json
```

## Files Being Served

- `/luna.incallide-terminal.mjs` - Main plugin file
- `/luna.incallide-terminal.json` - Plugin metadata
- `/luna.incallide-terminal.mjs.map` - Source map for debugging
- `/store.json` - Store information for DEV store

## Next Steps

1. Open Tidal Luna
2. Navigate to Plugin Settings
3. Add DEV store URL: `http://localhost:8765`
4. Install the Incallide Terminal plugin
5. Test the Terminal button in player controls