# Tidal Luna Plugin Troubleshooting Guide

## Error: "Failed to load Cannot add dependency to non plugin!"

This error occurs when Luna can't properly resolve the plugin dependencies. Here are the solutions:

### Solution 1: Use Global Luna APIs (Implemented)

The plugin has been updated to use Luna APIs through the global scope instead of direct imports:

```javascript
// Instead of:
import { LunaPlugin, Tracer } from "@luna/core";

// We now use:
declare const luna: any;
const { LunaPlugin, Tracer } = luna.core || {};
```

### Solution 2: Clear Luna Plugin Cache

1. Close Tidal Luna completely
2. Clear the plugin cache:
   - macOS: `~/Library/Application Support/TIDAL/plugins/cache/`
   - Windows: `%APPDATA%\TIDAL\plugins\cache\`
   - Linux: `~/.config/TIDAL/plugins/cache/`
3. Restart Tidal Luna
4. Re-add the DEV store URL

### Solution 3: Manual Plugin Installation

If the DEV store isn't working, try manual installation:

1. **Download the built plugin**:
   ```bash
   cd tidal_luna_plugin_proper/dist
   ls -la luna.incallide-terminal.*
   ```

2. **Copy to Luna plugins directory**:
   ```bash
   # macOS
   cp luna.incallide-terminal.* ~/Library/Application\ Support/TIDAL/plugins/
   
   # Windows (in PowerShell)
   Copy-Item luna.incallide-terminal.* "$env:APPDATA\TIDAL\plugins\"
   
   # Linux
   cp luna.incallide-terminal.* ~/.config/TIDAL/plugins/
   ```

3. **Restart Tidal Luna**

### Solution 4: Check Plugin Structure

Ensure the plugin is properly structured:

```
dist/
├── luna.incallide-terminal.mjs       # Main plugin file
├── luna.incallide-terminal.json      # Plugin metadata
└── luna.incallide-terminal.mjs.map   # Source map
```

### Solution 5: Verify Server is Running

Check that the dev server is accessible:

```bash
# Check if server is running
curl http://localhost:8765/store.json

# Should return:
{
  "plugins": ["luna.incallide-terminal.mjs"]
}
```

### Solution 6: Check Browser Console

1. Open Tidal Luna
2. Press F12 to open DevTools
3. Go to Console tab
4. Look for errors related to:
   - CORS issues
   - Network failures
   - Module resolution

### Common Issues and Fixes

#### Issue: CORS Blocked
**Error**: "Access to fetch at 'http://localhost:8765' from origin 'tidal://' has been blocked by CORS"

**Fix**: The server is already configured with CORS. If still blocked:
```bash
# Restart server with explicit CORS
cd tidal_luna_plugin_proper
pkill -f http-server
pnpm run serve
```

#### Issue: Port Already in Use
**Error**: "EADDRINUSE: address already in use :::8765"

**Fix**: Kill the process using the port:
```bash
# Find process using port 8765
lsof -i :8765  # macOS/Linux
netstat -ano | findstr :8765  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

#### Issue: Plugin Not Showing in Store
**Fix**: Ensure the store.json is properly formatted:
```bash
curl http://localhost:8765/store.json | jq '.'
```

#### Issue: WebSocket Connection Failed
**Error**: "WebSocket connection to 'ws://localhost:9876' failed"

**Fix**: This is expected if the terminal player isn't running. The plugin will retry automatically.

### Testing the Plugin

1. **Check if plugin loaded**:
   - Open DevTools Console (F12)
   - Look for: `[IncallideTerminal] Incallide Terminal Player plugin loaded!`

2. **Test the Terminal button**:
   - Look for "Terminal" button in player controls
   - Click it or press Ctrl/Cmd + Shift + T

3. **Launch terminal player manually**:
   ```bash
   cd ~/incallide
   ./run_mini_player.sh
   ```

### Plugin Architecture

The plugin uses a client-server architecture:

```
Tidal Luna (Browser)          Terminal (Python)
┌─────────────────┐           ┌─────────────────┐
│  Plugin (JS)    │           │  Mini Player    │
│                 │           │                 │
│  WebSocket      │◄─────────►│  WebSocket      │
│  Client         │   :9876   │  Server         │
│                 │           │                 │
│  HTTP Request   │──────────►│  HTTP Server    │
│  (Launch)       │   :9877   │  (Launcher)     │
└─────────────────┘           └─────────────────┘
```

### Debug Mode

To enable verbose logging:

1. In the browser console:
   ```javascript
   localStorage.setItem('luna.debug', 'true');
   ```

2. Reload the plugin

3. Check console for detailed logs

### Getting Help

If issues persist:

1. Check the build output:
   ```bash
   cd tidal_luna_plugin_proper
   pnpm run build
   ```

2. Verify TypeScript compilation:
   ```bash
   npx tsc --noEmit
   ```

3. Check the plugin hash matches:
   ```bash
   curl http://localhost:8765/luna.incallide-terminal.json | jq '.hash'
   ```

### Clean Rebuild

For a complete clean rebuild:

```bash
cd tidal_luna_plugin_proper

# Stop all processes
pkill -f http-server
pkill -f "pnpm run watch"

# Clean build artifacts
rm -rf dist/ node_modules/.cache/

# Reinstall and rebuild
pnpm install
pnpm run build

# Start fresh
pnpm run watch
```

This should resolve most plugin loading issues!