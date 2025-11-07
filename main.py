import os
import json
import tempfile
import requests
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch
import subprocess
import shutil
import subprocess
import time
import pyfiglet

from data_manager import load_data, save_data, add_song, delete_song
from player import play_song
from display import list_songs, is_kitty_terminal
from utils import clear_screen
from searcher import search_and_handle

console = Console()

def handle_playlist_menu(group, songs):
    """Handle playlist menu in a loop."""
    while True:
        list_songs(group_name=group)
        if not songs:
            return

        # show available quick commands for clarity
        console.print("[dim]Commands: [bold]play[/bold] | [bold]play N[/bold] | [bold]delete[/bold] | [bold]delete N[/bold] | [bold]back[/bold][/dim]")
        raw_action = Prompt.ask("[bold cornflower_blue]▶ Enter Commands:[/bold cornflower_blue] ").strip()
        la = raw_action.lower()

        if la.startswith("play"):
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
            play_song(group, start_index=start_idx)
            # After playback ends, continue showing playlist
            continue

        elif la.startswith("delete"):
            parts = raw_action.split()
            if len(parts) >= 2:
                try:
                    num = int(parts[1])
                    delete_song(group, index=num-1)
                except Exception:
                    console.print("[red]Invalid number format.[/red]")
            else:
                delete_song(group)
            continue

        elif la == "back":
            break
        else:
            console.print("[red]Unknown action[/red]")
            continue

def main():
    while True:
        clear_screen()
        ascii_art = pyfiglet.figlet_format("SONG-CLI !", font="slant")
        lines = ascii_art.splitlines()
        colors = [21, 27, 33, 39, 45, 51]
        for i, line in enumerate(lines):
            color_code = colors[i % len(colors)]
            print(f"\033[38;5;{color_code}m{line}\033[0m")
        
        console.print("[bold blue]Start with:[/bold blue] [bold white]search[/bold white] | [bold white]list[/bold white] | [bold white]exit[/bold white]")
        cmd = Prompt.ask("Enter command").strip().lower()

        if cmd == "search":
            clear_screen()
            search_and_handle()
        elif cmd == "list":
            while True:  # Add loop for playlist selection
                clear_screen()
                groups = load_data()["groups"]
                if not groups:
                    console.print("[yellow]No playlists yet. Search and add songs first.[/yellow]")
                    break

                console.print("\n[bold]Available playlists:[/bold]")
                for group in groups:
                    console.print(f"  • {group}")

                group = Prompt.ask("Enter playlist name (or 'back' to return)").strip()
                if group.lower() == "back":
                    break

                if group in groups:
                    handle_playlist_menu(group, groups[group])
                else:
                    console.print("[red]Playlist not found.[/red]")
                    continue

        elif cmd == "exit":
            break
        else:
            console.print("[red]Unknown command[/red]")

if __name__ == "__main__":
    main()
