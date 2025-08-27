#!/usr/bin/env python3
"""
Incallide Mini Terminal Player
A compact terminal player that connects to Tidal Luna via WebSocket
"""

import os
import sys
import json
import asyncio
import threading
from datetime import datetime
from typing import Optional, Dict, Any

import websockets
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.align import Align
from rich import box
from pynput import keyboard

class MiniTerminalPlayer:
    """Compact terminal player for Tidal Luna"""
    
    def __init__(self):
        self.console = Console()
        self.current_track = None
        self.is_playing = False
        self.volume = 70
        self.position = 0
        self.duration = 0
        self.ws = None
        self.running = True
        self.last_update = datetime.now()
        
        # Layout components
        self.layout = Layout()
        self.setup_layout()
        
    def setup_layout(self):
        """Setup the terminal UI layout"""
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", size=10),
            Layout(name="progress", size=3),
            Layout(name="controls", size=5),
            Layout(name="footer", size=2)
        )
        
    def create_header(self) -> Panel:
        """Create header panel"""
        return Panel(
            Align.center(
                Text("🎵 Incallide Mini Player for Tidal Luna 🎵", style="bold cyan"),
                vertical="middle"
            ),
            border_style="cyan",
            box=box.DOUBLE
        )
    
    def create_now_playing(self) -> Panel:
        """Create now playing panel"""
        if not self.current_track:
            content = Align.center(
                Text("No track playing\n\nWaiting for Tidal Luna...", style="dim"),
                vertical="middle"
            )
        else:
            lines = []
            lines.append(Text(self.current_track.get('title', 'Unknown'), style="bold white"))
            lines.append(Text(f"by {self.current_track.get('artist', 'Unknown')}", style="green"))
            lines.append(Text(f"from {self.current_track.get('album', 'Unknown')}", style="blue"))
            
            # Add play state
            state = "▶️  Playing" if self.is_playing else "⏸  Paused"
            lines.append(Text(""))
            lines.append(Text(state, style="yellow"))
            
            content = Align.center(
                Text.from_markup("\n".join(str(line) for line in lines)),
                vertical="middle"
            )
        
        return Panel(
            content,
            title="Now Playing",
            border_style="green" if self.is_playing else "yellow"
        )
    
    def create_progress(self) -> Panel:
        """Create progress bar panel"""
        if self.current_track and self.duration > 0:
            # Calculate progress percentage
            progress_pct = (self.position / self.duration) * 100 if self.duration > 0 else 0
            
            # Create progress bar
            bar_width = 40
            filled = int((progress_pct / 100) * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)
            
            # Format times
            current_time = self.format_time(self.position)
            total_time = self.format_time(self.duration)
            
            progress_text = f"{current_time} {bar} {total_time}"
            
            content = Align.center(Text(progress_text, style="cyan"))
        else:
            content = Align.center(Text("──────────────────────────────────", style="dim"))
        
        return Panel(content, border_style="blue")
    
    def create_controls(self) -> Panel:
        """Create controls panel"""
        table = Table(show_header=False, box=None, padding=1)
        table.add_column(justify="center")
        
        controls = [
            "[bold cyan]Controls:[/bold cyan]",
            "Space - Play/Pause    N - Next    P - Previous",
            "+ Volume Up    - Volume Down    Q - Quit",
            f"Volume: {self.volume}%"
        ]
        
        for control in controls:
            table.add_row(control)
        
        return Panel(
            Align.center(table),
            border_style="magenta"
        )
    
    def create_footer(self) -> Panel:
        """Create footer panel"""
        status = "🟢 Connected" if self.ws else "🔴 Disconnected"
        return Panel(
            Align.center(
                Text(f"{status} | Press Q to quit | Ctrl+C to force quit", style="dim")
            ),
            border_style="dim"
        )
    
    def format_time(self, seconds: float) -> str:
        """Format seconds to MM:SS"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def update_display(self):
        """Update the display"""
        self.layout["header"].update(self.create_header())
        self.layout["main"].update(self.create_now_playing())
        self.layout["progress"].update(self.create_progress())
        self.layout["controls"].update(self.create_controls())
        self.layout["footer"].update(self.create_footer())
    
    async def connect_websocket(self):
        """Connect to Tidal Luna WebSocket"""
        while self.running:
            try:
                self.console.print("[dim]Connecting to Tidal Luna...[/dim]")
                async with websockets.connect("ws://localhost:9876") as websocket:
                    self.ws = websocket
                    self.console.print("[green]Connected to Tidal Luna![/green]")
                    
                    # Request current track info
                    await websocket.send(json.dumps({"type": "request_info"}))
                    
                    # Listen for messages
                    while self.running:
                        try:
                            message = await asyncio.wait_for(
                                websocket.recv(),
                                timeout=1.0
                            )
                            await self.handle_message(json.loads(message))
                        except asyncio.TimeoutError:
                            # Send ping to keep connection alive
                            await websocket.send(json.dumps({"type": "ping"}))
                        except websockets.exceptions.ConnectionClosed:
                            break
                            
            except Exception as e:
                self.ws = None
                self.console.print(f"[red]Connection error: {e}[/red]")
                await asyncio.sleep(5)  # Retry after 5 seconds
    
    async def handle_message(self, message: Dict[str, Any]):
        """Handle WebSocket message"""
        msg_type = message.get('type')
        
        if msg_type == 'track_update':
            data = message.get('data', {})
            self.current_track = data
            self.is_playing = data.get('isPlaying', False)
            self.position = data.get('position', 0)
            self.duration = data.get('duration', 0)
            self.volume = data.get('volume', 70)
            self.last_update = datetime.now()
            
        elif msg_type == 'pong':
            pass  # Connection is alive
    
    async def send_command(self, command: str):
        """Send command to Tidal Luna"""
        if self.ws:
            try:
                await self.ws.send(json.dumps({
                    "type": "command",
                    "data": command
                }))
            except Exception as e:
                self.console.print(f"[red]Error sending command: {e}[/red]")
    
    def on_key_press(self, key):
        """Handle key press"""
        try:
            if hasattr(key, 'char'):
                if key.char == ' ':  # Space - Play/Pause
                    asyncio.create_task(self.send_command('play_pause'))
                elif key.char == 'n':  # Next
                    asyncio.create_task(self.send_command('next'))
                elif key.char == 'p':  # Previous
                    asyncio.create_task(self.send_command('previous'))
                elif key.char == '+':  # Volume up
                    asyncio.create_task(self.send_command('volume_up'))
                elif key.char == '-':  # Volume down
                    asyncio.create_task(self.send_command('volume_down'))
                elif key.char == 'q':  # Quit
                    self.running = False
                    return False  # Stop listener
        except AttributeError:
            pass
    
    def start_keyboard_listener(self):
        """Start keyboard listener in background"""
        listener = keyboard.Listener(on_press=self.on_key_press)
        listener.daemon = True
        listener.start()
    
    async def update_position_loop(self):
        """Update position while playing"""
        while self.running:
            if self.is_playing and self.current_track:
                # Estimate position based on time elapsed
                elapsed = (datetime.now() - self.last_update).total_seconds()
                self.position = min(self.position + elapsed, self.duration)
                self.last_update = datetime.now()
            
            await asyncio.sleep(1)
    
    async def run(self):
        """Main run loop"""
        self.console.clear()
        
        # Start keyboard listener
        self.start_keyboard_listener()
        
        # Create tasks
        tasks = [
            asyncio.create_task(self.connect_websocket()),
            asyncio.create_task(self.update_position_loop())
        ]
        
        # Run display loop
        with Live(self.layout, refresh_per_second=2, screen=True) as live:
            while self.running:
                self.update_display()
                await asyncio.sleep(0.5)
        
        # Cancel tasks
        for task in tasks:
            task.cancel()
        
        self.console.print("\n[bold green]Thanks for using Incallide Mini Player![/bold green]")


def main():
    """Main entry point"""
    print("""
╔════════════════════════════════════════════╗
║   🎵 Incallide Mini Player for Tidal Luna  ║
╚════════════════════════════════════════════╝
    """)
    
    player = MiniTerminalPlayer()
    
    try:
        asyncio.run(player.run())
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())