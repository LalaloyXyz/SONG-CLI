import subprocess
import time
import sys
import os
import shutil
from rich.console import Console
from data_manager import load_data
from display import list_songs
from utils import clear_screen

# Only import msvcrt on Windows
if os.name == 'nt':
    import msvcrt
else:
    import select

console = Console()

def play_song(group_name, start_index: int = 0):
    """Play songs in a group with auto-next and manual controls. start_index is 0-based."""
    data = load_data()
    if group_name not in data["groups"]:
        console.print("[red]Group not found.[/red]")
        return
    songs = data["groups"][group_name]
    if not songs:
        console.print("[yellow]No songs in this group.[/yellow]")
        return
    index = max(0, min(start_index, len(songs) - 1))
    n = len(songs)
    while True:
        clear_screen()
        list_songs(current_index=index, group_name=group_name)
        console.print("[green]▶ Auto-playing playlist[/green]")
        console.print("[dim]Commands: next / back / stop / exit[/dim]")
        # start mpv process
        mpv_cmd = ["mpv", "--no-video", "--quiet", "--no-terminal", songs[index]["url"]]
        if os.name == 'nt':
            mpv_cmd[0] = 'mpv.exe' if not shutil.which('mpv') or shutil.which('mpv.exe') else 'mpv'
        process = subprocess.Popen(
            mpv_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        while True:
            retcode = process.poll()
            if retcode is not None:
                index = (index + 1) % n
                break
            cmd = None
            if os.name == 'nt':
                # Use msvcrt polling for input
                if msvcrt.kbhit():
                    raw = input("[▶ Control:] ").strip().lower()
                    cmd = raw
            else:
                # Use select for unix
                if select.select([sys.stdin], [], [], 0.5)[0]:
                    try:
                        cmd = console.input("[bold cornflower_blue]▶ Control:[/bold cornflower_blue] ").strip().lower()
                    except (EOFError, KeyboardInterrupt):
                        cmd = "exit"
            if cmd:
                if cmd == "next":
                    process.terminate()
                    index = (index + 1) % n
                    break
                elif cmd == "back":
                    process.terminate()
                    index = (index - 1) % n
                    break
                elif cmd == "stop":
                    process.terminate()
                    console.print("[red]Stopped playback.[/red]")
                    return
                elif cmd == "exit":
                    process.terminate()
                    console.print("[yellow]Exited playlist loop.[/yellow]")
                    return
                else:
                    console.print("[dim]Unknown command. Use: next / back / stop / exit[/dim]")
                    time.sleep(0.5)
