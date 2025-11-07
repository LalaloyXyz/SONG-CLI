from rich.console import Console
from rich.prompt import Prompt
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch
import requests
from pathlib import Path
import tempfile
import subprocess
import os
from display import is_kitty_terminal
from data_manager import add_song
from utils import clear_screen

console = Console()

def search_and_handle():
    """Handle search flow: search -> show result -> play once or add to playlist."""
    query = Prompt.ask("Enter YouTube URL or search term")
    clear_screen()
    if "youtube.com" not in query and "youtu.be" not in query:
        search = VideosSearch(query, limit=1).result()
        if not search["result"]:
            console.print("[red]No results found.[/red]")
            return
        result = search["result"][0]
        url = result["link"]
        title = result["title"]
        uploader = result.get("channel", {}).get("name", "")
        thumb_url = result.get("thumbnails", [{}])[0].get("url", "")
    else:
        url = query
        with YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
        title = info.get("title", "Unknown title")
        uploader = info.get("uploader", "")
        thumb_url = info.get("thumbnail", "")
    thumb_path = ""
    if thumb_url:
        try:
            thumb_data = requests.get(thumb_url, timeout=10).content
            thumb_path = Path(tempfile.gettempdir()) / "yt_thumb.jpg"
            with open(thumb_path, "wb") as f:
                f.write(thumb_data)
        except Exception:
            thumb_path = ""
    has_kitty = is_kitty_terminal()
    clear_screen()
    console.print(f"\n[bold orange_red1]Search Result[/bold orange_red1]\n")
    y_offset = 0
    # Kitty preview skip if on Windows
    if has_kitty and thumb_path and os.path.exists(thumb_path):
        try:
            subprocess.run([
                "kitty", "+kitten", "icat",
                "--silent",
                "--align", "left",
                f"--place", f"10x10@0x{y_offset}",
                str(thumb_path)
            ], check=True)
        except Exception:
            pass
        console.print()
    elif os.name == 'nt' and thumb_url:
        console.print("[dim]Thumbnail preview not supported in this terminal.[/dim]")
    padding = "            " if has_kitty else ""
    console.print(f"{padding}[bold green]1. {title}[/bold green]")
    if uploader:
        console.print(f"{padding}[dim]Creator: {uploader}[/dim]\n")
    raw_action = Prompt.ask("What would you like to do ('play' or 'add' or 'cancel')").strip()
    if raw_action.lower().startswith("play"):
        parts = raw_action.split()
        start_idx = 0
        if len(parts) >= 2:
            try:
                num = int(parts[1])
                if num >= 1:
                    start_idx = num - 1
                else:
                    console.print("[red]Invalid number, starting from 1.[/red]")
            except Exception:
                console.print("[red]Invalid number format, starting from 1.[/red]")
        clear_screen()
        if has_kitty and thumb_path and os.path.exists(thumb_path):
            try:
                subprocess.run([
                    "kitty", "+kitten", "icat",
                    "--silent",
                    "--align", "left",
                    f"--place", f"10x10@0x{y_offset}",
                    str(thumb_path)
                ], check=True)
            except Exception:
                pass
            console.print()
        elif os.name == 'nt' and thumb_url:
            console.print("[dim]Thumbnail preview not supported in this terminal.[/dim]")
        console.print(f"{padding}[bold green]Now Playing:[/bold green] {title}")
        if uploader:
            console.print(f"{padding}[dim]Creator: {uploader}[/dim]\n")
        subprocess.run(["mpv", "--no-video", "--quiet", url])
        console.print("\n[bold yellow]Playback finished.[/bold yellow]")
        input("Press Enter to return...")
    elif raw_action.lower().startswith("add"):
        group = Prompt.ask("Enter playlist name to add to")
        add_song(group, url)
    else:
        console.print("[yellow]Cancelled search.[/yellow]")
