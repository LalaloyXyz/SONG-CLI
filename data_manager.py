import json
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
import tempfile
import requests
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch

DATA_FILE = Path("songs.json")
console = Console()

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"groups": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def add_song(group_name, preset_url=None):
    url = preset_url if preset_url else Prompt.ask("Enter YouTube URL (or search term)")
    if "youtube.com" not in url and "youtu.be" not in url:
        search = VideosSearch(url, limit=1).result()
        if not search["result"]:
            console.print("[red]No results found.[/red]")
            return
        url = search["result"][0]["link"]

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    title = info.get("title", "Unknown title")
    uploader = info.get("uploader") or info.get("uploader_id") or ""
    thumbnail_url = info.get("thumbnail", "")
    thumb_path = Path(tempfile.gettempdir()) / f"{info['id']}.jpg"

    if thumbnail_url:
        try:
            r = requests.get(thumbnail_url, timeout=10)
            with open(thumb_path, "wb") as f:
                f.write(r.content)
        except Exception:
            thumb_path = None

    data = load_data()
    if group_name not in data["groups"]:
        data["groups"][group_name] = []

    data["groups"][group_name].append({
        "title": title,
        "url": url,
        "thumb": str(thumb_path) if thumb_path else "",
        "uploader": uploader
    })
    save_data(data)
    console.print(f"[green]Added:[/green] {title} to group '{group_name}'")

def delete_song(group_name, index=None):
    from display import list_songs   # Prevent circular import
    clear_screen = None
    try:
        from utils import clear_screen
    except ImportError:
        pass
    clear_screen() if clear_screen else None
    data = load_data()
    if group_name not in data["groups"]:
        console.print("[red]Group not found.[/red]")
        return
    songs = data["groups"][group_name]
    if not songs:
        console.print("[yellow]No songs in this group.[/yellow]")
        return
    if index is None:
        list_songs(group_name=group_name)
        try:
            num = int(Prompt.ask("Enter song number to delete")) - 1
        except Exception:
            console.print("[red]Invalid input.[/red]")
            return
    else:
        num = int(index)
    if 0 <= num < len(songs):
        removed = songs.pop(num)
        save_data(data)
        console.print(f"[red]Deleted:[/red] {removed['title']}")
    else:
        console.print("[red]Invalid number.[/red]")
