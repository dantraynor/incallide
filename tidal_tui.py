#!/usr/bin/env python3
"""
Tidal Terminal UI Player
A keyboard-driven TUI music player for Tidal with album covers and visuals.
"""

import os
import sys
import time
import threading
import asyncio
from typing import Optional, List, Dict, Any
import webbrowser
import requests
from io import BytesIO
import tempfile
from pathlib import Path

import vlc
import tidalapi
from dotenv import load_dotenv
from PIL import Image
from term_image.image import from_file

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Header, Footer, Static, DataTable, Input, Button, 
    ProgressBar, Label, RichLog, Tabs, Tab, TabPane
)
from textual.reactive import reactive
from textual.binding import Binding
from textual.message import Message
from textual.timer import Timer
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich.align import Align

load_dotenv()

class AlbumCover(Static):
    """Widget to display album cover art"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cover_path = None
        self.ascii_art = "🎵\n\nNo Cover\nAvailable"
    
    def render(self) -> str:
        if self.cover_path and os.path.exists(self.cover_path):
            try:
                # Convert image to terminal display
                img = from_file(self.cover_path)
                img.set_size(width=40, height=20)
                return str(img)
            except Exception:
                pass
        return self.ascii_art
    
    async def set_cover(self, url: str):
        """Download and set album cover"""
        try:
            if url:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # Save to temp file
                    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                    temp_file.write(response.content)
                    temp_file.close()
                    
                    # Resize image for terminal display
                    img = Image.open(temp_file.name)
                    img = img.resize((120, 80), Image.Resampling.LANCZOS)
                    
                    # Save resized image
                    cover_path = temp_file.name + '_resized.jpg'
                    img.save(cover_path)
                    
                    # Clean up original temp file
                    os.unlink(temp_file.name)
                    
                    # Update display
                    if self.cover_path and os.path.exists(self.cover_path):
                        os.unlink(self.cover_path)
                    
                    self.cover_path = cover_path
                    self.refresh()
        except Exception as e:
            self.ascii_art = f"🎵\n\nCover\nError:\n{str(e)[:20]}..."
            self.refresh()

class Visualizer(Static):
    """Audio visualizer widget"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bars = [0] * 20
        self.timer = None
    
    def render(self) -> str:
        # Create simple ASCII visualizer
        viz_lines = []
        for i in range(8, 0, -1):
            line = ""
            for bar in self.bars:
                if bar >= i:
                    line += "█"
                else:
                    line += " "
            viz_lines.append(line)
        
        return "\n".join(viz_lines)
    
    def start_animation(self):
        """Start visualizer animation"""
        if self.timer:
            self.timer.stop()
        self.timer = self.set_interval(0.1, self.update_bars)
    
    def stop_animation(self):
        """Stop visualizer animation"""
        if self.timer:
            self.timer.stop()
        self.bars = [0] * 20
        self.refresh()
    
    def update_bars(self):
        """Update visualizer bars with random animation"""
        import random
        for i in range(len(self.bars)):
            # Simple random animation for now
            if random.random() < 0.3:
                self.bars[i] = random.randint(0, 8)
        self.refresh()

class TidalTUI(App):
    """Main Tidal TUI Application"""
    
    CSS = """
    .main-container {
        layout: grid;
        grid-size: 3 4;
    }
    
    .cover-container {
        border: solid blue;
        padding: 1;
    }
    
    .search-container {
        border: solid green;
        padding: 1;
    }
    
    .viz-container {
        border: solid yellow;
        padding: 1;
    }
    
    .control-container {
        border: solid red;
        padding: 1;
        height: 8;
    }
    
    .now-playing {
        border: solid magenta;
        padding: 1;
    }
    
    .queue-container {
        border: solid cyan;
        padding: 1;
    }
    
    DataTable {
        height: 100%;
    }
    
    ProgressBar {
        margin: 1 0;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+s", "focus_search", "Search"),
        Binding("space", "play_pause", "Play/Pause"),
        Binding("n", "next_track", "Next"),
        Binding("p", "prev_track", "Previous"),
        Binding("=", "volume_up", "Vol+"),
        Binding("-", "volume_down", "Vol-"),
        Binding("enter", "play_selected", "Play Selected"),
        Binding("j", "down", "Down"),
        Binding("k", "up", "Up"),
        Binding("h", "left", "Left"),
        Binding("l", "right", "Right"),
    ]
    
    def __init__(self):
        super().__init__()
        self.session = None
        self.current_track = None
        self.is_playing = False
        self.is_paused = False
        self.volume = 70
        self.search_results = []
        self.position = 0
        self.duration = 0
        
        # Initialize VLC player
        self.vlc_instance = vlc.Instance()
        self.vlc_player = self.vlc_instance.media_player_new()
        
        # Session file
        self.session_file = os.path.expanduser("~/.tidal_session.json")
        
        # Widgets
        self.cover_widget = None
        self.search_table = None
        self.search_input = None
        self.progress_bar = None
        self.now_playing_label = None
        self.visualizer = None
        self.status_log = None
        
    def compose(self) -> ComposeResult:
        """Create the UI layout"""
        yield Header()
        
        with Container(classes="main-container"):
            # Album cover section
            with Container(classes="cover-container"):
                yield Label("🎵 Album Cover", id="cover-title")
                self.cover_widget = AlbumCover(id="album-cover")
                yield self.cover_widget
            
            # Search and results section
            with Container(classes="search-container"):
                yield Label("🔍 Search & Results", id="search-title")
                self.search_input = Input(placeholder="Search for tracks...", id="search-input")
                yield self.search_input
                self.search_table = DataTable(id="search-results")
                self.search_table.add_columns("Track", "Artist", "Album", "Duration")
                yield self.search_table
            
            # Visualizer section
            with Container(classes="viz-container"):
                yield Label("🎶 Visualizer", id="viz-title")
                self.visualizer = Visualizer(id="visualizer")
                yield self.visualizer
            
            # Now playing section
            with Container(classes="now-playing"):
                yield Label("🎵 Now Playing", id="np-title")
                self.now_playing_label = Label("Nothing playing", id="np-info")
                yield self.now_playing_label
            
            # Queue section
            with Container(classes="queue-container"):
                yield Label("📑 Queue", id="queue-title")
                yield Label("Empty", id="queue-info")
            
            # Control section
            with Container(classes="control-container"):
                self.progress_bar = ProgressBar(total=100, id="progress")
                yield self.progress_bar
                yield Label("⏸️ Stopped | Vol: 70% | Use Space to play/pause", id="controls-info")
                
                # Status log
                self.status_log = RichLog(id="status-log", max_lines=3)
                yield self.status_log
        
        yield Footer()
    
    async def on_mount(self):
        """Initialize the app"""
        await self.authenticate()
        self.search_input.focus()
        
        # Start update timer
        self.set_interval(1, self.update_progress)
        
        # Log welcome message
        self.log_message("🎵 Tidal TUI Player Ready! Press Ctrl+S to search.")
    
    async def authenticate(self) -> bool:
        """Authenticate with Tidal API"""
        try:
            config = tidalapi.Config(quality=tidalapi.Quality.hi_res)
            self.session = tidalapi.Session(config)
            
            # Try to load existing session
            if os.path.exists(self.session_file):
                try:
                    with open(self.session_file, 'r') as f:
                        import json
                        session_data = json.load(f)
                        if session_data.get('access_token'):
                            self.session.load_oauth_session(session_data)
                            if self.session.check_login():
                                self.log_message("✓ Logged in using saved session")
                                return True
                except Exception:
                    pass
            
            # If no valid session exists, perform login
            self.log_message("🔐 Tidal Authentication Required")
            login, future = self.session.login_oauth()
            
            self.log_message(f"Visit: {login.verification_uri_complete}")
            
            # Auto-open browser
            webbrowser.open(login.verification_uri_complete)
            
            # Wait for authentication
            await asyncio.get_event_loop().run_in_executor(None, future.result)
            
            # Save session
            try:
                import json
                session_data = {
                    'access_token': self.session.access_token,
                    'refresh_token': self.session.refresh_token,
                    'expires_in': getattr(self.session, 'expires_in', 3600),
                    'token_type': getattr(self.session, 'token_type', 'Bearer')
                }
                with open(self.session_file, 'w') as f:
                    json.dump(session_data, f)
            except Exception as e:
                self.log_message(f"Warning: Could not save session: {e}")
            
            self.log_message("✓ Authentication successful!")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Authentication failed: {e}")
            return False
    
    def log_message(self, message: str):
        """Log a message to the status log"""
        if self.status_log:
            self.status_log.write(message)
    
    async def on_input_submitted(self, event: Input.Submitted):
        """Handle search input submission"""
        if event.input.id == "search-input":
            query = event.value.strip()
            if query:
                await self.search_tracks(query)
    
    async def search_tracks(self, query: str):
        """Search for tracks on Tidal"""
        try:
            if not self.session:
                self.log_message("❌ Not authenticated")
                return
            
            self.log_message(f"🔍 Searching for: {query}")
            
            # Perform search in executor to avoid blocking
            search_results = await asyncio.get_event_loop().run_in_executor(
                None, self.session.search, query
            )
            
            tracks = search_results.get('tracks', [])
            self.search_results = []
            
            # Clear and populate table
            self.search_table.clear()
            
            for i, track in enumerate(tracks[:20]):  # Limit to 20 results
                self.search_results.append({
                    'number': i + 1,
                    'title': track.name,
                    'artist': track.artist.name if track.artist else 'Unknown',
                    'album': track.album.name if track.album else 'Unknown',
                    'duration': self._format_duration(track.duration),
                    'track_obj': track
                })
                
                # Add to table
                self.search_table.add_row(
                    track.name[:30],
                    track.artist.name[:20] if track.artist else 'Unknown',
                    track.album.name[:20] if track.album else 'Unknown',
                    self._format_duration(track.duration)
                )
            
            self.log_message(f"✓ Found {len(self.search_results)} tracks")
            
        except Exception as e:
            self.log_message(f"❌ Search failed: {e}")
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration in MM:SS format"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    async def play_selected_track(self):
        """Play the selected track from search results"""
        if not self.search_results:
            self.log_message("❌ No search results available")
            return
        
        # Get selected row
        cursor_row = self.search_table.cursor_row
        if cursor_row >= len(self.search_results):
            self.log_message("❌ Invalid selection")
            return
        
        track_info = self.search_results[cursor_row]
        await self.play_track(track_info)
    
    async def play_track(self, track_info: dict):
        """Play a track"""
        try:
            track = track_info['track_obj']
            
            # Get stream URL
            stream_url = await asyncio.get_event_loop().run_in_executor(
                None, track.get_url
            )
            
            if not stream_url:
                self.log_message("❌ Unable to get stream URL")
                return
            
            # Stop current playback
            self.vlc_player.stop()
            
            self.log_message(f"🔄 Loading: {track_info['title']}")
            
            # Create VLC media and play
            media = self.vlc_instance.media_new(stream_url)
            self.vlc_player.set_media(media)
            self.vlc_player.audio_set_volume(self.volume)
            self.vlc_player.play()
            
            self.current_track = track_info
            self.is_playing = True
            self.is_paused = False
            
            # Update now playing
            self.now_playing_label.update(
                f"{track_info['title']}\n{track_info['artist']}"
            )
            
            # Start visualizer
            self.visualizer.start_animation()
            
            # Set album cover
            if hasattr(track, 'album') and track.album:
                cover_url = track.album.image
                if cover_url:
                    await self.cover_widget.set_cover(cover_url)
            
            self.log_message(f"🎵 Playing: {track_info['title']}")
            
        except Exception as e:
            self.log_message(f"❌ Playback failed: {e}")
    
    def update_progress(self):
        """Update progress bar and controls info"""
        if self.is_playing and not self.is_paused:
            # Get current position from VLC
            position = self.vlc_player.get_position()
            if position >= 0:
                self.progress_bar.update(progress=position * 100)
        
        # Update controls info
        status = "▶️ Playing" if self.is_playing and not self.is_paused else "⏸️ Paused" if self.is_paused else "⏹️ Stopped"
        controls_info = f"{status} | Vol: {self.volume}% | Space: Play/Pause | Enter: Play Selected"
        
        controls_label = self.query_one("#controls-info", Label)
        controls_label.update(controls_info)
    
    # Keyboard Actions
    def action_focus_search(self):
        """Focus the search input"""
        self.search_input.focus()
    
    def action_play_pause(self):
        """Toggle play/pause"""
        if self.is_playing:
            if self.is_paused:
                self.vlc_player.play()
                self.is_paused = False
                self.visualizer.start_animation()
                self.log_message("▶️ Resumed")
            else:
                self.vlc_player.pause()
                self.is_paused = True
                self.visualizer.stop_animation()
                self.log_message("⏸️ Paused")
        else:
            self.log_message("❌ No track to play")
    
    def action_volume_up(self):
        """Increase volume"""
        self.volume = min(100, self.volume + 10)
        self.vlc_player.audio_set_volume(self.volume)
        self.log_message(f"🔊 Volume: {self.volume}%")
    
    def action_volume_down(self):
        """Decrease volume"""
        self.volume = max(0, self.volume - 10)
        self.vlc_player.audio_set_volume(self.volume)
        self.log_message(f"🔉 Volume: {self.volume}%")
    
    async def action_play_selected(self):
        """Play selected track"""
        await self.play_selected_track()
    
    def action_down(self):
        """Move down in search results"""
        if self.search_table.has_focus:
            self.search_table.action_cursor_down()
        else:
            self.search_table.focus()
    
    def action_up(self):
        """Move up in search results"""
        if self.search_table.has_focus:
            self.search_table.action_cursor_up()
        else:
            self.search_table.focus()
    
    def action_quit(self):
        """Quit the application"""
        self.vlc_player.stop()
        self.exit()

def main():
    """Main entry point"""
    app = TidalTUI()
    app.run()

if __name__ == "__main__":
    main()