// Incallide Terminal Player Plugin for Tidal Luna
// Ultra-minimal version with no dependencies

(() => {
    // Use IIFE to avoid any module issues
    const pluginName = "[IncallideTerminal]";
    
    // Simple logging that won't fail
    function log(...args) {
        try {
            console.log(pluginName, ...args);
        } catch (e) {
            // Silently fail if console is not available
        }
    }
    
    function error(...args) {
        try {
            console.error(pluginName, ...args);
        } catch (e) {
            // Silently fail
        }
    }
    
    log("Plugin starting...");
    
    // Global state
    let ws = null;
    let reconnectTimeout = null;
    
    // WebSocket connection
    function connectWebSocket() {
        if (ws && ws.readyState === WebSocket.OPEN) return;
        
        try {
            ws = new WebSocket("ws://localhost:9876");
            
            ws.onopen = () => {
                log("Connected to terminal player");
                if (reconnectTimeout) {
                    clearTimeout(reconnectTimeout);
                    reconnectTimeout = null;
                }
            };
            
            ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    handleTerminalMessage(message);
                } catch (err) {
                    error("Error handling message:", err);
                }
            };
            
            ws.onclose = () => {
                log("Disconnected from terminal player");
                ws = null;
                reconnectTimeout = setTimeout(() => connectWebSocket(), 5000);
            };
            
            ws.onerror = (err) => {
                error("WebSocket error:", err);
            };
        } catch (err) {
            error("Failed to connect:", err);
            reconnectTimeout = setTimeout(() => connectWebSocket(), 5000);
        }
    }
    
    // Handle terminal messages
    function handleTerminalMessage(message) {
        const { type, data } = message;
        log("Received:", type, data);
        
        // Try to dispatch Redux actions if available
        try {
            const w = window;
            const dispatch = w.redux?.store?.dispatch;
            
            if (dispatch && type === "command") {
                switch (data) {
                    case "play_pause":
                        dispatch({ type: "playback/TOGGLE_PLAY_PAUSE" });
                        break;
                    case "next":
                        dispatch({ type: "playback/NEXT_TRACK" });
                        break;
                    case "previous":
                        dispatch({ type: "playback/PREVIOUS_TRACK" });
                        break;
                }
            }
        } catch (err) {
            error("Error dispatching:", err);
        }
    }
    
    // Launch terminal player
    function launchTerminalPlayer() {
        connectWebSocket();
        
        // Show instructions
        const existing = document.getElementById("incallide-modal");
        if (existing) existing.remove();
        
        const modal = document.createElement("div");
        modal.id = "incallide-modal";
        modal.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
            z-index: 10000;
            max-width: 500px;
            color: white;
            font-family: -apple-system, sans-serif;
        `;
        
        modal.innerHTML = `
            <h3 style="margin-top: 0;">Launch Terminal Player</h3>
            <p>Run in terminal:</p>
            <pre style="background: #000; padding: 10px; border-radius: 4px;">
python3 ~/incallide/mini_player.py
            </pre>
            <button onclick="this.parentElement.remove()" style="
                background: #333;
                border: 1px solid #555;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
            ">Close</button>
        `;
        
        document.body.appendChild(modal);
        setTimeout(() => {
            const m = document.getElementById("incallide-modal");
            if (m) m.remove();
        }, 10000);
    }
    
    // Add button to UI
    function addButton() {
        try {
            // Remove existing button
            const existing = document.getElementById("incallide-btn");
            if (existing) existing.remove();
            
            // Create button
            const button = document.createElement("button");
            button.id = "incallide-btn";
            button.innerHTML = "Terminal";
            button.title = "Open Terminal Player (Ctrl+Shift+T)";
            button.style.cssText = `
                padding: 8px 16px;
                margin: 0 8px;
                background: transparent;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 4px;
                color: inherit;
                cursor: pointer;
            `;
            button.onclick = launchTerminalPlayer;
            
            // Try to find player controls
            const selectors = [
                ".player-controls",
                ".playback-controls",
                "[data-test='player-controls']",
                ".now-playing-bar__center",
                ".player-bar"
            ];
            
            let added = false;
            const interval = setInterval(() => {
                for (const sel of selectors) {
                    const controls = document.querySelector(sel);
                    if (controls && !document.getElementById("incallide-btn")) {
                        controls.appendChild(button);
                        log("Button added to:", sel);
                        added = true;
                        clearInterval(interval);
                        break;
                    }
                }
            }, 1000);
            
            setTimeout(() => {
                clearInterval(interval);
                if (!added) error("Could not find player controls");
            }, 30000);
            
        } catch (err) {
            error("Failed to add button:", err);
        }
    }
    
    // Add keyboard shortcut
    function addShortcut() {
        document.addEventListener("keydown", (e) => {
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === "T") {
                e.preventDefault();
                launchTerminalPlayer();
            }
        });
    }
    
    // Initialize
    function init() {
        log("Initializing...");
        connectWebSocket();
        addButton();
        addShortcut();
        log("Initialized!");
    }
    
    // Start after delay
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        setTimeout(init, 1000);
    }
    
    // Export minimal interface for Luna
    window.__incallideTerminalPlugin = {
        unload: () => {
            log("Unloading...");
            if (reconnectTimeout) clearTimeout(reconnectTimeout);
            if (ws) ws.close();
            const btn = document.getElementById("incallide-btn");
            if (btn) btn.remove();
            const modal = document.getElementById("incallide-modal");
            if (modal) modal.remove();
        }
    };
})();

// Export empty object to satisfy Luna's module requirements
export default {};