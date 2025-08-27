/**
 * Incallide Terminal Player Plugin for Tidal Luna
 * Adds a button to launch the terminal-based mini player
 */

class IncallideTerminalPlugin {
    constructor() {
        this.name = 'Incallide Terminal Player';
        this.version = '1.0.0';
        this.ws = null;
        this.isConnected = false;
        this.currentTrack = null;
        this.terminalLaunched = false;
        
        // Get settings from plugin config
        this.settings = {
            serverPort: window.TidalLuna?.plugins?.getSettings?.('incallide-terminal')?.serverPort || 9876,
            autoLaunch: window.TidalLuna?.plugins?.getSettings?.('incallide-terminal')?.autoLaunch ?? true,
            terminalCommand: window.TidalLuna?.plugins?.getSettings?.('incallide-terminal')?.terminalCommand || 
                "osascript -e 'tell application \"Terminal\" to do script \"cd ~/incallide && ./run_mini_player.sh\"'"
        };
        
        console.log('[Incallide] Plugin initialized', this.settings);
    }
    
    /**
     * Initialize the plugin
     */
    async init() {
        console.log('[Incallide] Initializing plugin...');
        
        // Add button to UI
        this.addTerminalButton();
        
        // Connect to WebSocket server if available
        this.connectWebSocket();
        
        // Listen for track changes
        this.listenForTrackChanges();
        
        // Add keyboard shortcut
        this.addKeyboardShortcut();
        
        console.log('[Incallide] Plugin initialized successfully');
    }
    
    /**
     * Add terminal button to player controls
     */
    addTerminalButton() {
        // Wait for player controls to be available
        const checkInterval = setInterval(() => {
            // Try different possible selectors for Tidal Luna's player controls
            const playerControls = document.querySelector(
                '.player-controls, .playback-controls, .media-controls, [data-test="player-controls"]'
            );
            
            if (playerControls && !document.getElementById('incallide-terminal-btn')) {
                clearInterval(checkInterval);
                
                // Create button
                const button = document.createElement('button');
                button.id = 'incallide-terminal-btn';
                button.className = 'control-button incallide-terminal-button';
                button.innerHTML = `
                    <span class="button-icon">🖥️</span>
                    <span class="button-text">Terminal</span>
                `;
                button.title = 'Open Incallide Terminal Player';
                
                // Add styles
                button.style.cssText = `
                    background: transparent;
                    border: none;
                    color: inherit;
                    cursor: pointer;
                    padding: 8px 12px;
                    margin: 0 4px;
                    border-radius: 4px;
                    display: inline-flex;
                    align-items: center;
                    gap: 4px;
                    transition: background-color 0.2s;
                `;
                
                // Add hover effect
                button.addEventListener('mouseenter', () => {
                    button.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
                });
                button.addEventListener('mouseleave', () => {
                    button.style.backgroundColor = 'transparent';
                });
                
                // Add click handler
                button.addEventListener('click', () => this.launchTerminalPlayer());
                
                // Insert button into controls
                playerControls.appendChild(button);
                
                console.log('[Incallide] Terminal button added to player controls');
            }
        }, 1000);
        
        // Stop checking after 30 seconds
        setTimeout(() => clearInterval(checkInterval), 30000);
    }
    
    /**
     * Launch the terminal player
     */
    async launchTerminalPlayer() {
        console.log('[Incallide] Launching terminal player...');
        
        try {
            // First, ensure WebSocket server is running
            if (!this.isConnected) {
                await this.startTerminalServer();
            }
            
            // Get current track info
            const trackInfo = this.getCurrentTrackInfo();
            
            // Send track info if connected
            if (this.ws && this.isConnected && trackInfo) {
                this.ws.send(JSON.stringify({
                    type: 'track_update',
                    data: trackInfo
                }));
            }
            
            // Launch terminal if auto-launch is enabled
            if (this.settings.autoLaunch && !this.terminalLaunched) {
                this.executeTerminalCommand();
                this.terminalLaunched = true;
            }
            
            // Show notification
            this.showNotification('Terminal Player Launched', 'The Incallide terminal player is now running');
            
        } catch (error) {
            console.error('[Incallide] Error launching terminal player:', error);
            this.showNotification('Launch Failed', 'Could not launch terminal player. Check console for details.');
        }
    }
    
    /**
     * Start the terminal server
     */
    async startTerminalServer() {
        // Send message to Tidal Luna to start the server
        // This would typically be handled by the Electron main process
        if (window.TidalLuna?.ipc) {
            window.TidalLuna.ipc.send('incallide:start-server', {
                port: this.settings.serverPort
            });
        } else {
            console.warn('[Incallide] IPC not available, cannot start server');
        }
    }
    
    /**
     * Execute terminal command to launch the player
     */
    executeTerminalCommand() {
        // Send command to main process to execute
        if (window.TidalLuna?.ipc) {
            window.TidalLuna.ipc.send('incallide:execute-command', {
                command: this.settings.terminalCommand
            });
        } else {
            // Fallback: try to open via URL scheme if available
            const terminalUrl = `terminal://run?command=${encodeURIComponent('cd ~/incallide && ./run_mini_player.sh')}`;
            window.open(terminalUrl, '_blank');
        }
    }
    
    /**
     * Connect to WebSocket server
     */
    connectWebSocket() {
        try {
            this.ws = new WebSocket(`ws://localhost:${this.settings.serverPort}`);
            
            this.ws.onopen = () => {
                console.log('[Incallide] WebSocket connected');
                this.isConnected = true;
                
                // Send initial track info
                const trackInfo = this.getCurrentTrackInfo();
                if (trackInfo) {
                    this.ws.send(JSON.stringify({
                        type: 'track_update',
                        data: trackInfo
                    }));
                }
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    this.handleWebSocketMessage(message);
                } catch (error) {
                    console.error('[Incallide] Error parsing WebSocket message:', error);
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('[Incallide] WebSocket error:', error);
            };
            
            this.ws.onclose = () => {
                console.log('[Incallide] WebSocket disconnected');
                this.isConnected = false;
                
                // Try to reconnect after 5 seconds
                setTimeout(() => this.connectWebSocket(), 5000);
            };
            
        } catch (error) {
            console.error('[Incallide] Error connecting to WebSocket:', error);
        }
    }
    
    /**
     * Handle WebSocket messages from terminal player
     */
    handleWebSocketMessage(message) {
        console.log('[Incallide] Received message:', message);
        
        switch (message.type) {
            case 'command':
                this.handlePlayerCommand(message.data);
                break;
            case 'request_info':
                this.sendCurrentTrackInfo();
                break;
            case 'ping':
                this.ws.send(JSON.stringify({ type: 'pong' }));
                break;
        }
    }
    
    /**
     * Handle player commands from terminal
     */
    handlePlayerCommand(command) {
        switch (command) {
            case 'play_pause':
                this.triggerPlayPause();
                break;
            case 'next':
                this.triggerNext();
                break;
            case 'previous':
                this.triggerPrevious();
                break;
            case 'volume_up':
                this.adjustVolume(10);
                break;
            case 'volume_down':
                this.adjustVolume(-10);
                break;
        }
    }
    
    /**
     * Get current track information
     */
    getCurrentTrackInfo() {
        try {
            // Try to get track info from Tidal Luna's player API
            if (window.TidalLuna?.player) {
                const player = window.TidalLuna.player;
                return {
                    title: player.getCurrentTrack()?.title || 'Unknown',
                    artist: player.getCurrentTrack()?.artist || 'Unknown',
                    album: player.getCurrentTrack()?.album || 'Unknown',
                    duration: player.getDuration() || 0,
                    position: player.getPosition() || 0,
                    isPlaying: player.isPlaying() || false,
                    volume: player.getVolume() || 70,
                    coverUrl: player.getCurrentTrack()?.coverUrl || null
                };
            }
            
            // Fallback: try to scrape from DOM
            const titleElement = document.querySelector('[data-test="track-title"], .track-title, .now-playing-title');
            const artistElement = document.querySelector('[data-test="track-artist"], .track-artist, .now-playing-artist');
            const albumElement = document.querySelector('[data-test="track-album"], .track-album, .now-playing-album');
            
            return {
                title: titleElement?.textContent || 'Unknown',
                artist: artistElement?.textContent || 'Unknown',
                album: albumElement?.textContent || 'Unknown',
                duration: 0,
                position: 0,
                isPlaying: this.isCurrentlyPlaying(),
                volume: 70,
                coverUrl: this.getCurrentCoverUrl()
            };
            
        } catch (error) {
            console.error('[Incallide] Error getting track info:', error);
            return null;
        }
    }
    
    /**
     * Check if currently playing
     */
    isCurrentlyPlaying() {
        // Check play button state
        const playButton = document.querySelector('[data-test="play-button"], .play-button, button[aria-label*="Play"], button[aria-label*="Pause"]');
        if (playButton) {
            return playButton.getAttribute('aria-label')?.includes('Pause') || 
                   playButton.classList.contains('playing') ||
                   playButton.classList.contains('is-playing');
        }
        return false;
    }
    
    /**
     * Get current cover URL
     */
    getCurrentCoverUrl() {
        const coverImg = document.querySelector('[data-test="now-playing-cover"], .now-playing-cover img, .track-cover img');
        return coverImg?.src || null;
    }
    
    /**
     * Send current track info via WebSocket
     */
    sendCurrentTrackInfo() {
        if (this.ws && this.isConnected) {
            const trackInfo = this.getCurrentTrackInfo();
            if (trackInfo) {
                this.ws.send(JSON.stringify({
                    type: 'track_update',
                    data: trackInfo
                }));
            }
        }
    }
    
    /**
     * Listen for track changes
     */
    listenForTrackChanges() {
        // Use MutationObserver to detect DOM changes
        const observer = new MutationObserver(() => {
            const newTrack = this.getCurrentTrackInfo();
            if (newTrack && this.hasTrackChanged(newTrack)) {
                this.currentTrack = newTrack;
                this.sendCurrentTrackInfo();
            }
        });
        
        // Observe the player area for changes
        const playerArea = document.querySelector('.player, .now-playing, [data-test="player"]');
        if (playerArea) {
            observer.observe(playerArea, {
                childList: true,
                subtree: true,
                characterData: true
            });
        }
        
        // Also listen for Tidal Luna events if available
        if (window.TidalLuna?.events) {
            window.TidalLuna.events.on('track:change', () => {
                this.sendCurrentTrackInfo();
            });
            
            window.TidalLuna.events.on('playback:change', () => {
                this.sendCurrentTrackInfo();
            });
        }
    }
    
    /**
     * Check if track has changed
     */
    hasTrackChanged(newTrack) {
        if (!this.currentTrack) return true;
        return this.currentTrack.title !== newTrack.title ||
               this.currentTrack.artist !== newTrack.artist;
    }
    
    /**
     * Trigger play/pause
     */
    triggerPlayPause() {
        // Try Tidal Luna API first
        if (window.TidalLuna?.player?.togglePlayPause) {
            window.TidalLuna.player.togglePlayPause();
            return;
        }
        
        // Fallback: click play button
        const playButton = document.querySelector('[data-test="play-button"], .play-button, button[aria-label*="Play"], button[aria-label*="Pause"]');
        if (playButton) {
            playButton.click();
        }
    }
    
    /**
     * Trigger next track
     */
    triggerNext() {
        // Try Tidal Luna API first
        if (window.TidalLuna?.player?.next) {
            window.TidalLuna.player.next();
            return;
        }
        
        // Fallback: click next button
        const nextButton = document.querySelector('[data-test="next-button"], .next-button, button[aria-label*="Next"]');
        if (nextButton) {
            nextButton.click();
        }
    }
    
    /**
     * Trigger previous track
     */
    triggerPrevious() {
        // Try Tidal Luna API first
        if (window.TidalLuna?.player?.previous) {
            window.TidalLuna.player.previous();
            return;
        }
        
        // Fallback: click previous button
        const prevButton = document.querySelector('[data-test="previous-button"], .previous-button, button[aria-label*="Previous"]');
        if (prevButton) {
            prevButton.click();
        }
    }
    
    /**
     * Adjust volume
     */
    adjustVolume(delta) {
        // Try Tidal Luna API first
        if (window.TidalLuna?.player?.setVolume) {
            const currentVolume = window.TidalLuna.player.getVolume() || 70;
            window.TidalLuna.player.setVolume(Math.max(0, Math.min(100, currentVolume + delta)));
        }
    }
    
    /**
     * Add keyboard shortcut
     */
    addKeyboardShortcut() {
        document.addEventListener('keydown', (event) => {
            // Ctrl/Cmd + Shift + T to open terminal player
            if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'T') {
                event.preventDefault();
                this.launchTerminalPlayer();
            }
        });
    }
    
    /**
     * Show notification
     */
    showNotification(title, message) {
        // Try Tidal Luna notification API
        if (window.TidalLuna?.notifications?.show) {
            window.TidalLuna.notifications.show({
                title: title,
                message: message,
                icon: '🖥️'
            });
            return;
        }
        
        // Fallback: browser notification
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🖥️</text></svg>'
            });
        }
    }
    
    /**
     * Cleanup on unload
     */
    destroy() {
        if (this.ws) {
            this.ws.close();
        }
        
        // Remove button
        const button = document.getElementById('incallide-terminal-btn');
        if (button) {
            button.remove();
        }
        
        console.log('[Incallide] Plugin destroyed');
    }
}

// Initialize plugin when Tidal Luna is ready
if (window.TidalLuna?.plugins?.register) {
    // Register with Tidal Luna plugin system
    window.TidalLuna.plugins.register({
        id: 'incallide-terminal',
        name: 'Incallide Terminal Player',
        version: '1.0.0',
        instance: new IncallideTerminalPlugin()
    });
} else {
    // Fallback: initialize directly
    const plugin = new IncallideTerminalPlugin();
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => plugin.init());
    } else {
        plugin.init();
    }
    
    // Store globally for debugging
    window.IncallidePlugin = plugin;
}

console.log('[Incallide] Plugin loaded');