#!/usr/bin/env python3
"""
Tidal Terminal Player
A terminal-based music player for Tidal using Python.
"""

import os
import sys
import time
import threading
from typing import Optional, List, Dict, Any
import webbrowser
import vlc
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
import tidalapi
from dotenv import load_dotenv

load_dotenv()

class TidalPlayer:
    def __init__(self):
        self.console = Console()
        self.session = None
        self.current_track = None
        self.current_position = 0
        self.is_playing = False
        self.is_paused = False
        self.volume = 70
        self.search_results = []
        self.playlist = []
        self.current_index = 0
        
        # Initialize VLC player
        self.vlc_instance = vlc.Instance()
        self.vlc_player = self.vlc_instance.media_player_new()
        
        # Session file for persistence
        self.session_file = os.path.expanduser("~/.tidal_session.json")
        
    def authenticate(self) -> bool:
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
                                self.console.print("✓ Logged in using saved session", style="green")
                                return True
                except Exception:
                    pass
            
            # If no valid session exists, perform login
            self.console.print("🔐 Tidal Authentication Required", style="bold blue")
            login, future = self.session.login_oauth()
            
            self.console.print(f"Visit: {login.verification_uri_complete}", style="cyan")
            self.console.print("Or go to: {} and enter code: {}".format(
                login.verification_uri, login.user_code), style="cyan")
            
            # Auto-open browser
            webbrowser.open(login.verification_uri_complete)
            
            # Wait for authentication
            future.result()
            
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
                self.console.print(f"Warning: Could not save session: {e}", style="yellow")
            
            self.console.print("✓ Authentication successful!", style="green")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Authentication failed: {e}", style="red")
            return False
    
    def search_tracks(self, query: str) -> List[Dict]:
        """Search for tracks on Tidal"""
        try:
            if not self.session:
                self.console.print("❌ Not authenticated", style="red")
                return []
            
            search_results = self.session.search(query)
            tracks = search_results.get('tracks', [])
            
            self.search_results = []
            for i, track in enumerate(tracks[:20]):  # Limit to 20 results
                self.search_results.append({
                    'number': i + 1,
                    'title': track.name,
                    'artist': track.artist.name if track.artist else 'Unknown',
                    'album': track.album.name if track.album else 'Unknown',
                    'duration': self._format_duration(track.duration),
                    'track_obj': track
                })
            
            return self.search_results
            
        except Exception as e:
            self.console.print(f"❌ Search failed: {e}", style="red")
            return []
    
    def display_search_results(self):
        """Display search results in a formatted table"""
        if not self.search_results:
            self.console.print("No search results to display", style="yellow")
            return
        
        table = Table(title="🎵 Search Results")
        table.add_column("#", style="cyan", width=3)
        table.add_column("Title", style="white")
        table.add_column("Artist", style="green")
        table.add_column("Album", style="blue")
        table.add_column("Duration", style="magenta", width=8)
        
        for result in self.search_results:
            table.add_row(
                str(result['number']),
                result['title'],
                result['artist'],
                result['album'],
                result['duration']
            )
        
        self.console.print(table)
    
    def play_track(self, track_number: int):
        """Play a track by number from search results"""
        try:
            if not self.search_results:
                self.console.print("❌ No search results available", style="red")
                return
            
            if track_number < 1 or track_number > len(self.search_results):
                self.console.print("❌ Invalid track number", style="red")
                return
            
            track_info = self.search_results[track_number - 1]
            track = track_info['track_obj']
            
            # Get stream URL
            stream_url = track.get_url()
            if not stream_url:
                self.console.print("❌ Unable to get stream URL", style="red")
                return
            
            # Stop current playback
            self.stop()
            
            self.console.print(f"🔄 Loading: {track_info['title']}...", style="yellow")
            
            # Create VLC media and play
            media = self.vlc_instance.media_new(stream_url)
            self.vlc_player.set_media(media)
            self.vlc_player.audio_set_volume(self.volume)
            self.vlc_player.play()
            
            self.current_track = track_info
            self.is_playing = True
            self.is_paused = False
            
            self.console.print(f"🎵 Playing: {track_info['title']} by {track_info['artist']}", style="green")
            
        except Exception as e:
            self.console.print(f"❌ Playback failed: {e}", style="red")
    
    def pause_resume(self):
        """Toggle pause/resume"""
        if self.is_playing:
            if self.is_paused:
                self.vlc_player.play()
                self.is_paused = False
                self.console.print("▶️  Resumed", style="green")
            else:
                self.vlc_player.pause()
                self.is_paused = True
                self.console.print("⏸️  Paused", style="yellow")
        else:
            self.console.print("❌ No track playing", style="red")
    
    def stop(self):
        """Stop playback"""
        self.vlc_player.stop()
        self.is_playing = False
        self.is_paused = False
        self.current_track = None
        self.console.print("⏹️  Stopped", style="red")
    
    def set_volume(self, volume: int):
        """Set volume (0-100)"""
        volume = max(0, min(100, volume))
        self.volume = volume
        self.vlc_player.audio_set_volume(volume)
        self.console.print(f"🔊 Volume: {volume}%", style="blue")
    
    def show_now_playing(self):
        """Display current track information"""
        if not self.current_track:
            self.console.print("❌ No track playing", style="red")
            return
        
        status = "⏸️  Paused" if self.is_paused else "▶️  Playing"
        
        panel = Panel(
            f"[bold white]{self.current_track['title']}[/bold white]\n"
            f"[green]Artist:[/green] {self.current_track['artist']}\n"
            f"[blue]Album:[/blue] {self.current_track['album']}\n"
            f"[magenta]Duration:[/magenta] {self.current_track['duration']}\n"
            f"[cyan]Status:[/cyan] {status}\n"
            f"[yellow]Volume:[/yellow] {self.volume}%",
            title="🎵 Now Playing",
            border_style="green"
        )
        
        self.console.print(panel)
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration in MM:SS format"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    def show_help(self):
        """Display help information"""
        help_text = """
[bold cyan]🎵 Tidal Terminal Player Commands:[/bold cyan]

[yellow]search <query>[/yellow]     - Search for tracks
[yellow]play <number>[/yellow]      - Play track by number from search results
[yellow]pause[/yellow] or [yellow]resume[/yellow]   - Pause/resume playback
[yellow]stop[/yellow]               - Stop playback
[yellow]vol <0-100>[/yellow]        - Set volume
[yellow]np[/yellow]                 - Show now playing
[yellow]results[/yellow]            - Show last search results
[yellow]help[/yellow]               - Show this help
[yellow]quit[/yellow] or [yellow]exit[/yellow]      - Exit the player

[bold green]Example usage:[/bold green]
• search daft punk
• play 1
• vol 80
• pause
        """
        self.console.print(Panel(help_text, title="Help", border_style="blue"))
    
    def run(self):
        """Main application loop"""
        self.console.clear()
        self.console.print(Panel(
            "[bold blue]🎵 Tidal Terminal Player[/bold blue]\n"
            "Terminal-based music player for Tidal\n"
            "Type 'help' for commands",
            title="Welcome",
            border_style="blue"
        ))
        
        # Authenticate
        if not self.authenticate():
            return
        
        # Main command loop
        while True:
            try:
                command = Prompt.ask("\n[bold cyan]tidal>[/bold cyan]").strip().lower()
                
                if command in ['quit', 'exit']:
                    self.stop()
                    break
                elif command == 'help':
                    self.show_help()
                elif command.startswith('search '):
                    query = command[7:].strip()
                    if query:
                        self.console.print(f"🔍 Searching for: {query}", style="yellow")
                        results = self.search_tracks(query)
                        if results:
                            self.display_search_results()
                        else:
                            self.console.print("No results found", style="red")
                elif command.startswith('play '):
                    try:
                        track_num = int(command[5:].strip())
                        self.play_track(track_num)
                    except ValueError:
                        self.console.print("❌ Invalid track number", style="red")
                elif command in ['pause', 'resume']:
                    self.pause_resume()
                elif command == 'stop':
                    self.stop()
                elif command.startswith('vol '):
                    try:
                        volume = int(command[4:].strip())
                        self.set_volume(volume)
                    except ValueError:
                        self.console.print("❌ Invalid volume level", style="red")
                elif command == 'np':
                    self.show_now_playing()
                elif command == 'results':
                    self.display_search_results()
                elif command == '':
                    continue
                else:
                    self.console.print("❌ Unknown command. Type 'help' for available commands.", style="red")
                    
            except KeyboardInterrupt:
                self.console.print("\n👋 Goodbye!", style="blue")
                self.stop()
                break
            except Exception as e:
                self.console.print(f"❌ Error: {e}", style="red")

def main():
    """Main entry point"""
    player = TidalPlayer()
    player.run()

if __name__ == "__main__":
    main()