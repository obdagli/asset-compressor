import os
import glob
import time
import gzip
import shutil
import brotli
import argparse
import logging
import concurrent.futures
import questionary
import sys
from PIL import Image
from moviepy import VideoFileClip
from tqdm import tqdm

# Rich UI Imports
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich import print as rprint

# ==========================================
# SETUP
# ==========================================
console = Console()
logging.basicConfig(level=logging.ERROR, format='%(levelname)s: %(message)s')

# ==========================================
# CONFIGURATION
# ==========================================
MAX_WIDTH = 1920
WEBP_QUALITY = 75
WEBP_METHOD = 6
VIDEO_CRF = 26
VIDEO_PRESET = 'medium'

# Folders to always ignore to prevent scanning 10k+ dependency files
IGNORE_DIRS = {
    'node_modules', 'venv', '.git', '.vscode', '__pycache__',
    'site-packages', 'dist', 'build', '.idea', '.gemini', 'env'
}

# ==========================================
# UTILITIES
# ==========================================
def get_size_mb(path):
    if not os.path.exists(path): return 0
    return os.path.getsize(path) / (1024 * 1024)

def format_size(mb):
    return f"{mb:.2f} MB"

def benchmark(old_path, new_path):
    old_size = get_size_mb(old_path)
    new_size = get_size_mb(new_path)
    ratio = (1 - (new_size / old_size)) * 100 if old_size > 0 else 0
    return old_size, new_size, ratio

def display_welcome():
    console.clear()
    title = Text("High-Performance Asset Compressor", style="bold cyan")
    subtitle = Text("Optimizing Images and Videos for Production", style="italic white")
    
    welcome_panel = Panel(
        Text.assemble(title, "\n", subtitle),
        border_style="cyan",
        expand=False,
        padding=(1, 2)
    )
    console.print(welcome_panel, justify="center")
    console.print("\n")

# ==========================================
# COMPATIBILITY HELPERS
# ==========================================
def safe_select(question, choices):
    if sys.stdin.isatty():
        return questionary.select(
            question,
            choices=choices,
            style=questionary.Style([
                ('qmark', 'fg:cyan bold'),
                ('question', 'fg:white bold'),
                ('answer', 'fg:cyan bold'),
                ('pointer', 'fg:cyan bold'),
            ])
        ).ask()
    else:
        print(f"\n? {question}")
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")
        try:
            line = sys.stdin.readline().strip()
            if line.isdigit():
                idx = int(line) - 1
                if 0 <= idx < len(choices): return choices[idx]
            return None
        except: return None

def safe_path_input(question):
    if sys.stdin.isatty():
        return questionary.path(question).ask()
    else:
        print(f"\n? {question}")
        return sys.stdin.readline().strip()

# ==========================================
# CORE LOGIC
# ==========================================
def compress_image(file_path):
    try:
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        if ext.lower() == '.webp': return None

        new_filename = f"{name}.webp"
        new_file_path = os.path.join(os.path.dirname(file_path), new_filename)

        if os.path.exists(new_file_path):
             return {"status": "skipped", "reason": "Target exists"}

        img = Image.open(file_path)
        if img.width > MAX_WIDTH:
            ratio = MAX_WIDTH / img.width
            new_height = int(img.height * ratio)
            img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
            
        img.save(new_file_path, "WEBP", quality=WEBP_QUALITY, method=WEBP_METHOD)
        old_size, new_size, ratio = benchmark(file_path, new_file_path)
        return {"status": "success", "original": filename, "new": new_filename, "old_size": old_size, "new_size": new_size, "ratio": ratio}
    except Exception as e:
        return {"status": "error", "error": str(e), "file": file_path}

def compress_video(file_path):
    try:
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        if ext.lower() not in ['.mp4', '.mov', '.avi']: return None
        if "optimized" in name: return None

        new_filename = f"{name}.optimized.mp4"
        new_file_path = os.path.join(os.path.dirname(file_path), new_filename)
        if os.path.exists(new_file_path): return None

        temp_path = os.path.join(os.path.dirname(file_path), f"temp_{new_filename}")
        clip = VideoFileClip(file_path)
        if clip.w > MAX_WIDTH: clip = clip.resized(width=MAX_WIDTH)
            
        clip.write_videofile(temp_path, codec="libx264", audio_codec="aac", preset=VIDEO_PRESET, 
                             ffmpeg_params=["-crf", str(VIDEO_CRF)], logger=None)
        clip.close()
        
        if os.path.exists(new_file_path): os.remove(new_file_path)
        os.rename(temp_path, new_file_path)
        old_size, new_size, ratio = benchmark(file_path, new_file_path)
        return {"status": "success", "original": filename, "new": new_filename, "old_size": old_size, "new_size": new_size, "ratio": ratio}
    except Exception as e:
        return {"status": "error", "error": str(e), "file": file_path}

# ==========================================
# FILE SEARCHING
# ==========================================
def find_files(start_path):
    found_files = []
    extensions = {'.png', '.jpg', '.jpeg', '.mp4'}
    
    for root, dirs, files in os.walk(start_path):
        # In-place modify dirs to skip ignored ones
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in extensions:
                found_files.append(os.path.join(root, file))
    return found_files

# ==========================================
# PROCESSOR
# ==========================================
def process_batch(files):
    results = []
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), TaskProgressColumn(), console=console) as progress:
        task = progress.add_task(f"[green]Optimizing {len(files)} assets...", total=len(files))
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in ['.png', '.jpg', '.jpeg']: futures.append(executor.submit(compress_image, f))
                elif ext == '.mp4': futures.append(executor.submit(compress_video, f))
            
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res: results.append(res)
                progress.advance(task)

    console.print("\n")
    table = Table(title="Optimization Report", border_style="cyan")
    table.add_column("File", style="white")
    table.add_column("Old Size", justify="right", style="red")
    table.add_column("New Size", justify="right", style="green")
    table.add_column("Reduction", justify="right", style="bold cyan")

    total_saved = 0
    count = 0
    for res in sorted([r for r in results if r['status'] == 'success'], key=lambda x: x.get('ratio', 0), reverse=True):
        table.add_row(res['original'], format_size(res['old_size']), format_size(res['new_size']), f"{res['ratio']:.1f}%")
        total_saved += (res['old_size'] - res['new_size'])
        count += 1
    
    if count > 0:
        console.print(table)
        console.print(f"\n[bold green]Total Space Saved: {format_size(total_saved)}[/bold green]")
    else:
        console.print("[yellow]No new assets needed optimization.[/yellow]")

# ==========================================
# MAIN
# ==========================================
def main():
    parser = argparse.ArgumentParser(description="Asset Compressor")
    parser.add_argument("-i", "--input", help="Path to images/videos")
    args = parser.parse_args()

    if args.input:
        files = find_files(args.input) if os.path.isdir(args.input) else [args.input]
        process_batch(files)
    else:
        display_welcome()
        choice = safe_select("Action:", ["1. Optimize Assets", "2. Exit"])
        if choice and "Optimize" in choice:
            path = safe_path_input("Target folder/file:")
            if path and os.path.exists(path):
                files = find_files(path) if os.path.isdir(path) else [path]
                process_batch(files)
            else:
                rprint("[red]Invalid path.[/red]")
        rprint("[bold cyan]Goodbye![/bold cyan]")

if __name__ == "__main__":
    main()
