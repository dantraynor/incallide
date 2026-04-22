#!/usr/bin/env python3
"""
Simple Tidal TUI Player
A working keyboard-driven terminal player for Tidal.
"""

import os
import asyncio
import webbrowser
import vlc
import tidalapi
from dotenv import load_dotenv

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, DataTable, Input, ProgressBar, RichLog
from textual.binding import Binding
from rich.text import Text
from rich.panel import Panel

load_dotenv()

class SimpleTidalTUI(App):
    """Simple Tidal TUI Application"""
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+q", "quit", "Quit"),
        Binding("/", "focus_search", "Search"),
        Binding("s", "focus_search", "Search"),
        Binding("p", "play_pause", "Play/Pause"),
        Binding("space", "play_pause", "Play/Pause"),
        Binding("enter", "play_selected", "Play Selected"),
        Binding("plus", "volume_up", "Vol+"),
        Binding("minus", "volume_down", "Vol-"),
        Binding("j", "cursor_down", "Down"),
        Binding("k", "cursor_up", "Up"),
        Binding("down", "cursor_down", "Down"),
        Binding("up", "cursor_up", "Up"),
    ]
    
    def __init__(self):
        super().__init__()
        self.session = None
        self.current_track = None
        self.is_playing = False
        self.is_paused = False
        self.volume = 70
        self.search_results = []
        
        # Initialize VLC player
        self.vlc_instance = vlc.Instance()
        self.vlc_player = self.vlc_instance.media_player_new()
        
        # Session file
        self.session_file = os.path.expanduser("~/.tidal_session.json")
        
    def compose(self) -> ComposeResult:
        """Create the UI layout"""
        yield Header()
        
        with Vertical():
            # Search input
            yield Input(placeholder="Search tracks... (Ctrl+S to focus)", id="search-input")
            
            # Search results table
            yield DataTable(id="search-table")
            
            # Now playing info
            yield Static("Nothing playing", id="now-playing")
            
            # Progress bar
            yield ProgressBar(total=100, id="progress-bar")
            
            # Controls info
            yield Static("Controls: S=Search, Space/P=Play/Pause, Enter=Play Selected, J/K/↑/↓=Navigate, +/-=Volume", id="controls")
            
            # Status log
            yield RichLog(id="status-log", max_lines=5)
        
        yield Footer()
    
    async def on_mount(self):
        """Initialize the app"""
        # Setup search table
        table = self.query_one("#search-table", DataTable)
        table.add_columns("Track", "Artist", "Album", "Duration")
        table.cursor_type = "row"
        
        # Authenticate
        await self.authenticate()
        
        # Focus search input
        search_input = self.query_one("#search-input", Input)
        search_input.focus()
        
        # Log ready message
        self.log_message("🎵 Tidal TUI Player Ready!")
        self.log_message("Press S to search, use J/K/arrows to navigate, Enter to play")
        
        # Start progress update timer
        self.set_interval(1.0, self.update_progress)
    
    def log_message(self, message: str):
        """Log a message"""
        log_widget = self.query_one("#status-log", RichLog)
        log_widget.write(message)
    
    async def authenticate(self):
        """Authenticate with Tidal"""
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
                                return
                except Exception:
                    pass
            
            # Perform login
            self.log_message("🔐 Tidal Authentication Required")
            login, future = self.session.login_oauth()
            
            self.log_message(f"Visit: {login.verification_uri_complete}")
            webbrowser.open(login.verification_uri_complete)
            
            # Wait for auth in background
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
            
        except Exception as e:
            self.log_message(f"❌ Authentication failed: {e}")
    
    async def on_input_submitted(self, event: Input.Submitted):
        """Handle search input"""
        if event.input.id == "search-input":
            query = event.value.strip()
            if query:
                await self.search_tracks(query)
    
    async def search_tracks(self, query: str):
        """Search for tracks"""
        try:
            if not self.session:
                self.log_message("❌ Not authenticated")
                return
            
            self.log_message(f"🔍 Searching for: {query}")
            
            # Search in background
            search_results = await asyncio.get_event_loop().run_in_executor(
                None, self.session.search, query
            )
            
            tracks = search_results.get('tracks', [])
            self.search_results = []
            
            # Clear table
            table = self.query_one("#search-table", DataTable)
            table.clear()
            
            # Add tracks to table
            for i, track in enumerate(tracks[:20]):
                track_info = {
                    'number': i + 1,
                    'title': track.name,
                    'artist': track.artist.name if track.artist else 'Unknown',
                    'album': track.album.name if track.album else 'Unknown',
                    'duration': self._format_duration(track.duration),
                    'track_obj': track
                }
                self.search_results.append(track_info)
                
                # Add to table
                table.add_row(
                    track.name[:40],
                    track.artist.name[:25] if track.artist else 'Unknown',
                    track.album.name[:25] if track.album else 'Unknown',
                    self._format_duration(track.duration)
                )
            
            # Focus table for navigation
            table.focus()
            
            self.log_message(f"✓ Found {len(self.search_results)} tracks")
            
        except Exception as e:
            self.log_message(f"❌ Search failed: {e}")
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    async def play_selected(self):
        """Play selected track"""
        table = self.query_one("#search-table", DataTable)
        
        if not self.search_results:
            self.log_message("❌ No search results")
            return
        
        cursor_row = table.cursor_row
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
            
            # Play with VLC
            media = self.vlc_instance.media_new(stream_url)
            self.vlc_player.set_media(media)
            self.vlc_player.audio_set_volume(self.volume)
            self.vlc_player.play()
            
            self.current_track = track_info
            self.is_playing = True
            self.is_paused = False
            
            # Update now playing
            now_playing = self.query_one("#now-playing", Static)
            now_playing.update(f"🎵 {track_info['title']} - {track_info['artist']}")
            
            self.log_message(f"🎵 Playing: {track_info['title']}")
            
        except Exception as e:
            self.log_message(f"❌ Playback failed: {e}")
    
    def update_progress(self):
        """Update progress bar"""
        if self.is_playing and not self.is_paused:
            position = self.vlc_player.get_position()
            if position >= 0:
                progress_bar = self.query_one("#progress-bar", ProgressBar)
                progress_bar.update(progress=position * 100)
    
    # Actions
    def action_focus_search(self):
        """Focus search input"""
        search_input = self.query_one("#search-input", Input)
        search_input.focus()
    
    def action_play_pause(self):
        """Toggle play/pause"""
        if self.is_playing:
            if self.is_paused:
                self.vlc_player.play()
                self.is_paused = False
                self.log_message("▶️ Resumed")
            else:
                self.vlc_player.pause()
                self.is_paused = True
                self.log_message("⏸️ Paused")
        else:
            self.log_message("❌ No track playing")
    
    async def action_play_selected(self):
        """Play selected track"""
        await self.play_selected()
    
    def action_volume_up(self):
        """Volume up"""
        self.volume = min(100, self.volume + 10)
        self.vlc_player.audio_set_volume(self.volume)
        self.log_message(f"🔊 Volume: {self.volume}%")
    
    def action_volume_down(self):
        """Volume down"""
        self.volume = max(0, self.volume - 10)
        self.vlc_player.audio_set_volume(self.volume)
        self.log_message(f"🔉 Volume: {self.volume}%")
    
    def action_cursor_down(self):
        """Move cursor down"""
        table = self.query_one("#search-table", DataTable)
        if not table.has_focus:
            table.focus()
        table.action_cursor_down()
    
    def action_cursor_up(self):
        """Move cursor up"""
        table = self.query_one("#search-table", DataTable)
        if not table.has_focus:
            table.focus()
        table.action_cursor_up()
    
    def action_quit(self):
        """Quit"""
        self.vlc_player.stop()
        self.exit()

def main():
    """Main entry point"""
    app = SimpleTidalTUI()
    app.run()

if __name__ == "__main__":
    main()