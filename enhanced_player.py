#!/usr/bin/env python3
"""
Enhanced Tidal Terminal Player
Command-line music player for Tidal with enhanced features.
"""

import os
import sys
import time
import threading
import asyncio
from typing import Optional, List, Dict, Any
import webbrowser
import vlc
import tidalapi
from dotenv import load_dotenv
import requests
from io import BytesIO
import tempfile

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, ProgressColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich import print as rprint

load_dotenv()

class EnhancedTidalPlayer:
    def __init__(self):
        self.console = Console()
        self.session = None
        self.current_track = None
        self.is_playing = False
        self.is_paused = False
        self.volume = 70
        self.search_results = []
        self.queue = []
        self.current_index = 0
        self.current_playlist = []
        self.playlist_index = 0
        self.auto_play_next = True
        
        # Initialize VLC player
        self.vlc_instance = vlc.Instance()
        self.vlc_player = self.vlc_instance.media_player_new()
        
        # Session file
        self.session_file = os.path.expanduser("~/.tidal_session.json")
        
        # Progress tracking
        self.position = 0
        self.duration = 0
        self.update_thread = None
        self.running = True
        
    def display_logo(self):
        """Display cool ASCII logo"""
        logo = """
╔══════════════════════════════════════════════════════════════╗
║  ████████╗██╗██████╗  █████╗ ██╗         ██████╗ ██╗  ██╗    ║
║  ╚══██╔══╝██║██╔══██╗██╔══██╗██║         ██╔══██╗██║  ██║    ║
║     ██║   ██║██║  ██║███████║██║         ██████╔╝██║  ██║    ║
║     ██║   ██║██║  ██║██╔══██║██║         ██╔═══╝ ██║  ██║    ║
║     ██║   ██║██████╔╝██║  ██║███████╗    ██║     ███████║    ║
║     ╚═╝   ╚═╝╚═════╝ ╚═╝  ╚═╝╚══════╝    ╚═╝     ╚══════╝    ║
║                                                              ║
║                🎵 Enhanced Terminal Player 🎵                ║
╚══════════════════════════════════════════════════════════════╝
        """
        self.console.print(logo, style="bold blue")
        
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
                        self.console.print(f"📁 Found session file: {self.session_file}", style="blue")
                        
                        if session_data.get('access_token'):
                            self.console.print("🔄 Loading saved session...", style="yellow")
                            
                            # Set session attributes directly
                            self.session.access_token = session_data.get('access_token')
                            self.session.refresh_token = session_data.get('refresh_token')
                            self.session.user_id = session_data.get('user_id')
                            self.session.country_code = session_data.get('country_code', 'US')
                            self.session.session_id = session_data.get('session_id')
                            self.session.token_type = session_data.get('token_type', 'Bearer')
                            
                            # Test if the session works
                            try:
                                # Try a simple API call to test the session
                                test_search = self.session.search("test")
                                self.console.print("✓ Logged in using saved session", style="green")
                                return True
                            except Exception as e:
                                self.console.print(f"⚠️  Saved session expired ({e}), need to re-authenticate", style="yellow")
                        else:
                            self.console.print("⚠️  Invalid session data", style="yellow")
                except Exception as e:
                    self.console.print(f"⚠️  Error loading session: {e}", style="yellow")
                    # Remove corrupted session file
                    try:
                        os.remove(self.session_file)
                    except:
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
                
                # Get user info to ensure we have user_id
                try:
                    user = self.session.user
                    user_id = user.id if user else getattr(self.session, 'user_id', None)
                except:
                    user_id = getattr(self.session, 'user_id', None)
                
                session_data = {
                    'access_token': self.session.access_token,
                    'refresh_token': self.session.refresh_token,
                    'expires_in': getattr(self.session, 'expires_in', 3600),
                    'token_type': getattr(self.session, 'token_type', 'Bearer'),
                    'user_id': user_id,
                    'country_code': getattr(self.session, 'country_code', 'US'),
                    'session_id': getattr(self.session, 'session_id', None)
                }
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
                
                with open(self.session_file, 'w') as f:
                    json.dump(session_data, f, indent=2)
                
                self.console.print(f"💾 Session saved to: {self.session_file}", style="green")
                
            except Exception as e:
                self.console.print(f"Warning: Could not save session: {e}", style="yellow")
                self.console.print(f"Session file path: {self.session_file}", style="yellow")
            
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
            
            self.console.print(f"🔍 Searching for: {query}", style="yellow")
            search_results = self.session.search(query)
            tracks = search_results.get('tracks', [])
            
            self.search_results = []
            for i, track in enumerate(tracks[:30]):  # Limit to 30 results
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
    
    def search_artists(self, query: str) -> List[Dict]:
        """Search for artists on Tidal"""
        try:
            if not self.session:
                self.console.print("❌ Not authenticated", style="red")
                return []
            
            self.console.print(f"🔍 Searching artists for: {query}", style="yellow")
            search_results = self.session.search(query)
            artists = search_results.get('artists', [])
            
            artist_results = []
            for i, artist in enumerate(artists[:20]):
                artist_results.append({
                    'number': i + 1,
                    'name': artist.name,
                    'artist_obj': artist
                })
            
            return artist_results
            
        except Exception as e:
            self.console.print(f"❌ Artist search failed: {e}", style="red")
            return []
    
    def search_albums(self, query: str) -> List[Dict]:
        """Search for albums on Tidal"""
        try:
            if not self.session:
                self.console.print("❌ Not authenticated", style="red")
                return []
            
            self.console.print(f"🔍 Searching albums for: {query}", style="yellow")
            search_results = self.session.search(query)
            albums = search_results.get('albums', [])
            
            album_results = []
            for i, album in enumerate(albums[:20]):
                album_results.append({
                    'number': i + 1,
                    'title': album.name,
                    'artist': album.artist.name if album.artist else 'Unknown',
                    'year': album.year if hasattr(album, 'year') else 'Unknown',
                    'album_obj': album
                })
            
            return album_results
            
        except Exception as e:
            self.console.print(f"❌ Album search failed: {e}", style="red")
            return []
    
    def display_search_results(self):
        """Display search results in a beautiful table"""
        if not self.search_results:
            self.console.print("No search results to display", style="yellow")
            return
        
        table = Table(title="🎵 Search Results", show_header=True, header_style="bold magenta")
        table.add_column("#", style="cyan", width=4, justify="right")
        table.add_column("Title", style="white", max_width=35)
        table.add_column("Artist", style="green", max_width=25)
        table.add_column("Album", style="blue", max_width=25)
        table.add_column("Duration", style="magenta", width=8, justify="center")
        
        for result in self.search_results:
            # Highlight current track if playing
            if (self.current_track and 
                result['title'] == self.current_track['title'] and 
                result['artist'] == self.current_track['artist']):
                table.add_row(
                    f"▶ {result['number']}",
                    f"[bold]{result['title']}[/bold]",
                    f"[bold]{result['artist']}[/bold]",
                    f"[bold]{result['album']}[/bold]",
                    f"[bold]{result['duration']}[/bold]",
                    style="on bright_black"
                )
            else:
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
            self.console.print("🔄 Getting stream URL...", style="yellow")
            stream_url = track.get_url()
                
            if not stream_url:
                self.console.print("❌ Unable to get stream URL", style="red")
                return
            
            # Stop current playback
            self.stop()
            
            self.console.print(f"🔄 Loading: {track_info['title']} by {track_info['artist']}", style="yellow")
            
            # Create VLC media and play
            media = self.vlc_instance.media_new(stream_url)
            self.vlc_player.set_media(media)
            self.vlc_player.audio_set_volume(self.volume)
            self.vlc_player.play()
            
            self.current_track = track_info
            self.is_playing = True
            self.is_paused = False
            
            # Start update thread
            if self.update_thread is None or not self.update_thread.is_alive():
                self.update_thread = threading.Thread(target=self._update_progress, daemon=True)
                self.update_thread.start()
            
            self.console.print(f"🎵 Now Playing: {track_info['title']} by {track_info['artist']}", style="bold green")
            
            # Download and display album cover
            self._display_album_cover(track)
            
        except Exception as e:
            self.console.print(f"❌ Playback failed: {e}", style="red")
    
    def play_artist_radio(self, artist_name: str):
        """Play artist radio/mix"""
        try:
            if not self.session:
                self.console.print("❌ Not authenticated", style="red")
                return
            
            self.console.print(f"🔄 Creating radio for: {artist_name}", style="yellow")
            # Search for the artist first
            search_results = self.session.search(artist_name)
            artists = search_results.get('artists', [])
            
            if not artists:
                self.console.print(f"❌ Artist '{artist_name}' not found", style="red")
                return
            
            artist = artists[0]
            
            # Get artist's top tracks
            top_tracks = artist.get_top_tracks()
            
            if not top_tracks:
                self.console.print(f"❌ No tracks found for {artist_name}", style="red")
                return
            
            # Create playlist from top tracks
            self.current_playlist = []
            for i, track in enumerate(top_tracks[:50]):  # Limit to 50 tracks
                self.current_playlist.append({
                    'number': i + 1,
                    'title': track.name,
                    'artist': track.artist.name if track.artist else 'Unknown',
                    'album': track.album.name if track.album else 'Unknown',
                    'duration': self._format_duration(track.duration),
                    'track_obj': track
                })
            
            self.playlist_index = 0
            self.console.print(f"🎵 Created radio with {len(self.current_playlist)} tracks from {artist_name}", style="green")
            
            # Start playing first track
            if self.current_playlist:
                self._play_from_playlist(0)
                    
        except Exception as e:
            self.console.print(f"❌ Failed to create artist radio: {e}", style="red")
    
    def play_album(self, album_obj):
        """Play entire album"""
        try:
            self.console.print("🔄 Loading album tracks...", style="yellow")
            tracks = album_obj.tracks()
            
            if not tracks:
                self.console.print("❌ No tracks found in album", style="red")
                return
            
            # Create playlist from album tracks
            self.current_playlist = []
            for i, track in enumerate(tracks):
                self.current_playlist.append({
                    'number': i + 1,
                    'title': track.name,
                    'artist': track.artist.name if track.artist else 'Unknown',
                    'album': track.album.name if track.album else 'Unknown',
                    'duration': self._format_duration(track.duration),
                    'track_obj': track
                })
            
            self.playlist_index = 0
            self.console.print(f"🎵 Loaded album: {album_obj.name} ({len(self.current_playlist)} tracks)", style="green")
            
            # Start playing first track
            if self.current_playlist:
                self._play_from_playlist(0)
                    
        except Exception as e:
            self.console.print(f"❌ Failed to play album: {e}", style="red")
    
    def _play_from_playlist(self, index: int):
        """Play track from current playlist"""
        if not self.current_playlist or index >= len(self.current_playlist):
            return
        
        track_info = self.current_playlist[index]
        track = track_info['track_obj']
        
        try:
            # Get stream URL
            self.console.print("🔄 Getting stream URL...", style="yellow")
            stream_url = track.get_url()
                
            if not stream_url:
                self.console.print("❌ Unable to get stream URL", style="red")
                self.next_track()  # Try next track
                return
            
            # Stop current playback
            self.vlc_player.stop()
            
            self.console.print(f"🔄 Loading: {track_info['title']} by {track_info['artist']}", style="yellow")
            
            # Create VLC media and play
            media = self.vlc_instance.media_new(stream_url)
            self.vlc_player.set_media(media)
            self.vlc_player.audio_set_volume(self.volume)
            self.vlc_player.play()
            
            self.current_track = track_info
            self.playlist_index = index
            self.is_playing = True
            self.is_paused = False
            
            # Start update thread
            if self.update_thread is None or not self.update_thread.is_alive():
                self.update_thread = threading.Thread(target=self._update_progress, daemon=True)
                self.update_thread.start()
            
            self.console.print(f"🎵 Now Playing ({index + 1}/{len(self.current_playlist)}): {track_info['title']} by {track_info['artist']}", style="bold green")
            
            # Download and display album cover
            self._display_album_cover(track)
            
        except Exception as e:
            self.console.print(f"❌ Playback failed: {e}", style="red")
            self.next_track()  # Try next track
    
    def next_track(self):
        """Play next track in playlist"""
        if not self.current_playlist:
            self.console.print("❌ No playlist active", style="red")
            return
        
        next_index = self.playlist_index + 1
        if next_index >= len(self.current_playlist):
            self.console.print("🔚 End of playlist reached", style="yellow")
            return
        
        self._play_from_playlist(next_index)
    
    def prev_track(self):
        """Play previous track in playlist"""
        if not self.current_playlist:
            self.console.print("❌ No playlist active", style="red")
            return
        
        prev_index = self.playlist_index - 1
        if prev_index < 0:
            self.console.print("🔚 Already at first track", style="yellow")
            return
        
        self._play_from_playlist(prev_index)
    
    def show_playlist(self):
        """Display current playlist"""
        if not self.current_playlist:
            self.console.print("❌ No playlist active", style="red")
            return
        
        table = Table(title="🎵 Current Playlist", show_header=True, header_style="bold magenta")
        table.add_column("#", style="cyan", width=4, justify="right")
        table.add_column("Title", style="white", max_width=35)
        table.add_column("Artist", style="green", max_width=25)
        table.add_column("Album", style="blue", max_width=25)
        table.add_column("Duration", style="magenta", width=8, justify="center")
        
        for i, track in enumerate(self.current_playlist):
            # Highlight current track
            if i == self.playlist_index and self.is_playing:
                table.add_row(
                    f"▶ {track['number']}",
                    f"[bold]{track['title']}[/bold]",
                    f"[bold]{track['artist']}[/bold]",
                    f"[bold]{track['album']}[/bold]",
                    f"[bold]{track['duration']}[/bold]",
                    style="on bright_black"
                )
            else:
                table.add_row(
                    str(track['number']),
                    track['title'],
                    track['artist'],
                    track['album'],
                    track['duration']
                )
        
        self.console.print(table)
    
    def _display_album_cover(self, track):
        """Display album cover as terminal image"""
        try:
            if hasattr(track, 'album') and track.album:
                # Get the album cover URL - it might be a method or property
                try:
                    if hasattr(track.album, 'image'):
                        cover_url = track.album.image() if callable(track.album.image) else track.album.image
                    elif hasattr(track.album, 'cover'):
                        cover_url = track.album.cover() if callable(track.album.cover) else track.album.cover
                    else:
                        cover_url = None
                    
                    self.console.print(f"🖼️  Album cover URL: {cover_url}", style="blue")
                except Exception as e:
                    self.console.print(f"⚠️  Error getting cover URL: {e}", style="yellow")
                    cover_url = None
                
                if cover_url:
                    # Try to display actual album cover
                    try:
                        self.console.print("📥 Downloading album cover...", style="yellow")
                        # Download album cover
                        response = requests.get(cover_url, timeout=10)
                        if response.status_code == 200:
                            self.console.print("✓ Downloaded successfully", style="green")
                            
                            # Save to temporary file
                            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                            temp_file.write(response.content)
                            temp_file.close()
                            self.console.print(f"💾 Saved to: {temp_file.name}", style="blue")
                            
                            # Try simple ASCII art conversion first
                            try:
                                from PIL import Image
                                img = Image.open(temp_file.name)
                                img = img.resize((80, 40), Image.Resampling.LANCZOS)
                                img = img.convert('L')  # Convert to grayscale
                                
                                # Convert to ASCII art
                                ascii_chars = ["█", "▉", "▊", "▋", "▌", "▍", "▎", "▏", " "]
                                ascii_art = ""
                                
                                for y in range(0, img.height, 2):  # Skip every other row for better aspect ratio
                                    for x in range(img.width):
                                        pixel = img.getpixel((x, y))
                                        ascii_art += ascii_chars[pixel // 32]  # Map 0-255 to 0-8
                                    ascii_art += "\n"
                                
                                self.console.print(Panel(ascii_art, title=f"🎵 {track.album.name}", border_style="blue"))
                                
                                # Clean up
                                os.unlink(temp_file.name)
                                return
                                
                            except Exception as ascii_error:
                                self.console.print(f"⚠️  ASCII conversion failed: {ascii_error}", style="yellow")
                                
                                # Try term-image as fallback
                                try:
                                    from term_image.image import from_file
                                    self.console.print("🔄 Trying term-image display...", style="yellow")
                                    
                                    # Resize for term-image
                                    img = Image.open(temp_file.name)
                                    img = img.resize((60, 30), Image.Resampling.LANCZOS)
                                    resized_path = temp_file.name + '_resized.jpg'
                                    img.save(resized_path)
                                    
                                    term_img = from_file(resized_path)
                                    self.console.print(Panel(str(term_img), title=f"🎵 {track.album.name}", border_style="blue"))
                                    
                                    # Clean up
                                    os.unlink(temp_file.name)
                                    os.unlink(resized_path)
                                    return
                                    
                                except Exception as term_error:
                                    self.console.print(f"⚠️  Term-image failed: {term_error}", style="yellow")
                                    # Clean up and fall through to ASCII art
                                    try:
                                        os.unlink(temp_file.name)
                                        if 'resized_path' in locals():
                                            os.unlink(resized_path)
                                    except:
                                        pass
                        else:
                            self.console.print(f"❌ Failed to download: HTTP {response.status_code}", style="red")
                            
                    except Exception as e:
                        self.console.print(f"❌ Download error: {e}", style="red")
            else:
                self.console.print("⚠️  No album cover URL available", style="yellow")
            
            # Fallback ASCII art
            art = """
╔═══════════════════════════════╗
║           🎵 🎶 🎵           ║
║         ♪ ALBUM ART ♪        ║
║           🎵 🎶 🎵           ║
╚═══════════════════════════════╝
            """
            album_name = track.album.name if hasattr(track, 'album') and track.album else "Unknown Album"
            self.console.print(Panel(art, title=f"🎵 {album_name}", border_style="blue"))
            
        except Exception as e:
            self.console.print(f"❌ Album cover error: {e}", style="red")
            # Minimal fallback
            self.console.print(Panel("🎵 Album Art", border_style="blue"))
    
    def _update_progress(self):
        """Update progress in background thread"""
        track_ended = False
        while self.running and self.is_playing:
            if not self.is_paused:
                position = self.vlc_player.get_position()
                length = self.vlc_player.get_length()
                state = self.vlc_player.get_state()
                
                if position >= 0 and length > 0:
                    self.position = position
                    self.duration = length / 1000  # Convert to seconds
                
                # Auto-play next track when current track ends (only once per track)
                if (state == vlc.State.Ended and not track_ended and self.auto_play_next and 
                    self.current_playlist and self.playlist_index < len(self.current_playlist) - 1):
                    track_ended = True
                    time.sleep(1)  # Small delay before next track
                    self.next_track()
                elif state != vlc.State.Ended:
                    track_ended = False  # Reset for next track
            
            time.sleep(0.5)
    
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
        """Display current track information with progress"""
        if not self.current_track:
            self.console.print("❌ No track playing", style="red")
            return
        
        status = "⏸️  Paused" if self.is_paused else "▶️  Playing"
        
        # Get current position for progress bar
        position = self.vlc_player.get_position()
        length = self.vlc_player.get_length()
        
        progress_text = ""
        if position >= 0 and length > 0:
            current_time = int(position * length / 1000)
            total_time = int(length / 1000)
            progress_text = f"{self._format_duration(current_time)} / {self._format_duration(total_time)}"
            
            # Create progress bar
            progress_width = 40
            filled = int(position * progress_width)
            bar = "█" * filled + "░" * (progress_width - filled)
            progress_text += f"\n{bar}"
        
        panel_content = (
            f"[bold white]{self.current_track['title']}[/bold white]\n"
            f"[green]Artist:[/green] {self.current_track['artist']}\n"
            f"[blue]Album:[/blue] {self.current_track['album']}\n"
            f"[magenta]Duration:[/magenta] {self.current_track['duration']}\n"
            f"[cyan]Status:[/cyan] {status}\n"
            f"[yellow]Volume:[/yellow] {self.volume}%"
        )
        
        if progress_text:
            panel_content += f"\n[bright_black]{progress_text}[/bright_black]"
        
        panel = Panel(
            panel_content,
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
        """Display enhanced help information"""
        help_text = """
[bold cyan]🎵 Enhanced Tidal Terminal Player Commands:[/bold cyan]

[yellow]🔍 SEARCH & PLAYBACK[/yellow]
• [bold]search <query>[/bold]     - Search for tracks
• [bold]s <query>[/bold]          - Quick search
• [bold]play <number>[/bold]      - Play track by number
• [bold]p <number>[/bold]         - Quick play

[yellow]🎧 ARTIST & ALBUM PLAYBACK[/yellow]
• [bold]radio <artist>[/bold]     - Play artist radio (top tracks)
• [bold]artist <artist>[/bold]    - Search and play artist radio
• [bold]album <query>[/bold]      - Search for albums
• [bold]playalbum <number>[/bold] - Play entire album from search

[yellow]⏯️  PLAYBACK CONTROLS[/yellow]
• [bold]pause[/bold] / [bold]resume[/bold]     - Pause/resume playback
• [bold]stop[/bold]               - Stop playback
• [bold]next[/bold] / [bold]n[/bold]          - Next track in playlist
• [bold]prev[/bold] / [bold]previous[/bold]   - Previous track in playlist
• [bold]np[/bold] / [bold]nowplaying[/bold]   - Show now playing with progress

[yellow]📋 PLAYLIST & DISPLAY[/yellow]
• [bold]playlist[/bold] / [bold]pl[/bold]     - Show current playlist
• [bold]results[/bold] / [bold]r[/bold]       - Show last search results
• [bold]cover[/bold]              - Show current album cover
• [bold]clear[/bold]              - Clear screen

[yellow]🔊 AUDIO CONTROLS[/yellow]
• [bold]vol <0-100>[/bold]        - Set volume
• [bold]volume <0-100>[/bold]     - Set volume (alias)

[yellow]🚪 EXIT[/yellow]
• [bold]quit[/bold] / [bold]exit[/bold] / [bold]q[/bold] - Exit the player

[bold green]💡 Tips:[/bold green]
• [bold]radio daft punk[/bold] - Plays 50 top tracks from Daft Punk
• [bold]album dark side[/bold] - Search for albums, then [bold]playalbum 1[/bold]
• Playlists auto-advance to next track when songs end
• Use [bold]next[/bold]/[bold]prev[/bold] to navigate playlists manually
        """
        self.console.print(Panel(help_text, title="Help & Commands", border_style="blue"))
    
    def run(self):
        """Main application loop with enhanced features"""
        self.console.clear()
        self.display_logo()
        
        # Authenticate
        if not self.authenticate():
            return
        
        self.console.print("\n" + "="*60)
        self.console.print("🎵 Welcome to Enhanced Tidal Player! Type 'help' for commands.", style="bold green")
        self.console.print("="*60 + "\n")
        
        # Main command loop
        while True:
            try:
                command = Prompt.ask("\n[bold cyan]🎵 tidal>[/bold cyan]").strip()
                
                # Parse command and arguments
                parts = command.split(maxsplit=1)
                cmd = parts[0].lower() if parts else ""
                args = parts[1] if len(parts) > 1 else ""
                
                if cmd in ['quit', 'exit', 'q']:
                    self.running = False
                    self.stop()
                    self.console.print("👋 Thanks for using Enhanced Tidal Player!", style="bold blue")
                    break
                    
                elif cmd in ['help', 'h']:
                    self.show_help()
                    
                elif cmd in ['search', 's']:
                    if args:
                        results = self.search_tracks(args)
                        if results:
                            self.display_search_results()
                        else:
                            self.console.print("No results found", style="yellow")
                    else:
                        self.console.print("Usage: search <query>", style="yellow")
                        
                elif cmd in ['play', 'p']:
                    if args.isdigit():
                        track_num = int(args)
                        self.play_track(track_num)
                    else:
                        self.console.print("Usage: play <track_number>", style="yellow")
                        
                elif cmd in ['pause', 'resume']:
                    self.pause_resume()
                    
                elif cmd == 'stop':
                    self.stop()
                    
                elif cmd in ['vol', 'volume']:
                    if args.isdigit():
                        volume = int(args)
                        self.set_volume(volume)
                    else:
                        self.console.print("Usage: vol <0-100>", style="yellow")
                        
                elif cmd in ['np', 'nowplaying']:
                    self.show_now_playing()
                    
                elif cmd in ['results', 'r']:
                    self.display_search_results()
                    
                elif cmd in ['radio', 'artist']:
                    if args:
                        self.play_artist_radio(args)
                    else:
                        self.console.print("Usage: radio <artist_name>", style="yellow")
                        
                elif cmd == 'album':
                    if args:
                        album_results = self.search_albums(args)
                        if album_results:
                            # Display album search results
                            table = Table(title="🎵 Album Search Results", show_header=True, header_style="bold magenta")
                            table.add_column("#", style="cyan", width=4, justify="right")
                            table.add_column("Album", style="white", max_width=35)
                            table.add_column("Artist", style="green", max_width=25)
                            table.add_column("Year", style="blue", width=8, justify="center")
                            
                            for album in album_results:
                                table.add_row(
                                    str(album['number']),
                                    album['title'],
                                    album['artist'],
                                    str(album['year'])
                                )
                            
                            self.console.print(table)
                            self.album_results = album_results  # Store for playalbum command
                        else:
                            self.console.print("No albums found", style="yellow")
                    else:
                        self.console.print("Usage: album <search_query>", style="yellow")
                        
                elif cmd == 'playalbum':
                    if args.isdigit() and hasattr(self, 'album_results'):
                        album_num = int(args)
                        if 1 <= album_num <= len(self.album_results):
                            album_obj = self.album_results[album_num - 1]['album_obj']
                            self.play_album(album_obj)
                        else:
                            self.console.print("Invalid album number", style="red")
                    else:
                        self.console.print("Usage: playalbum <album_number> (search albums first)", style="yellow")
                        
                elif cmd in ['next', 'n']:
                    self.next_track()
                    
                elif cmd in ['prev', 'previous']:
                    self.prev_track()
                    
                elif cmd in ['playlist', 'pl']:
                    self.show_playlist()
                    
                elif cmd == 'session':
                    # Show session status
                    if os.path.exists(self.session_file):
                        try:
                            import json
                            with open(self.session_file, 'r') as f:
                                session_data = json.load(f)
                            self.console.print(f"📁 Session file: {self.session_file}", style="blue")
                            self.console.print(f"🔑 Has access token: {'Yes' if session_data.get('access_token') else 'No'}", style="green" if session_data.get('access_token') else "red")
                            if self.session and hasattr(self.session, 'user_id'):
                                self.console.print(f"👤 User ID: {self.session.user_id}", style="cyan")
                        except Exception as e:
                            self.console.print(f"❌ Error reading session: {e}", style="red")
                    else:
                        self.console.print("❌ No session file found", style="red")
                        
                elif cmd == 'cover':
                    # Show current album cover
                    if self.current_track:
                        self._display_album_cover(self.current_track['track_obj'])
                    else:
                        self.console.print("❌ No track playing", style="red")
                    
                elif cmd == 'clear':
                    self.console.clear()
                    self.display_logo()
                    
                elif cmd == '':
                    continue
                    
                else:
                    self.console.print("❌ Unknown command. Type 'help' for available commands.", style="red")
                    
            except KeyboardInterrupt:
                self.console.print("\n👋 Goodbye!", style="blue")
                self.running = False
                self.stop()
                break
            except Exception as e:
                self.console.print(f"❌ Error: {e}", style="red")

def main():
    """Main entry point"""
    player = EnhancedTidalPlayer()
    player.run()

if __name__ == "__main__":
    main()