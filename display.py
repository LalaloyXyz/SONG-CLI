import os
import subprocess
import shutil
from rich.console import Console

console = Console()

def is_kitty_terminal():
    """Check if running in Kitty terminal. Only possible on Unix."""
    return os.name != 'nt' and bool(os.environ.get("KITTY_WINDOW_ID") and shutil.which("kitty"))

def list_songs(current_index=None, group_name=None):
    from data_manager import load_data
    from utils import clear_screen
    clear_screen()
    data = load_data()
    if not data["groups"]:
        console.print("[yellow]No songs yet. Add with 'add'.[/yellow]")
        return
    has_kitty = is_kitty_terminal()
    for group, songs in data["groups"].items():
        if group_name and group != group_name:
            continue
        console.print(f"\n[bold orange_red1]{group}[/bold orange_red1]")
        y_offset = 0
        for i, song in enumerate(songs, 1):
            thumb = song.get("thumb", "")
            shown_img = False
            if has_kitty and thumb and os.path.exists(thumb):
                try:
                    subprocess.run([
                        "kitty", "+kitten", "icat",
                        "--silent",
                        "--align", "left",
                        f"--place", f"10x10@0x{y_offset}",
                        thumb
                    ])
                    shown_img = True
                except Exception:
                    pass
            elif os.name == 'nt' and thumb:
                # Thumbnail not supported, print alt
                if i == 1:
                    console.print("[dim]Thumbnail images not supported in this terminal.[/dim]")
            if has_kitty:
                console.print()
            uploader = song.get("uploader", "")
            padding = "            " if has_kitty else ""
            if current_index is not None and i - 1 == current_index:
                console.print(f"{padding}[bold white]{i}.[/bold white] [bold green]Now Playing:[/bold green] {song['title']}")
            else:
                console.print(f"{padding}[bold white]{i}.[/bold white] {song['title']}")
            if uploader:
                console.print(f"{padding}[dim]Creator: {uploader}[/dim]")
            y_offset += 4
        console.print()
