import os
import glob
import time
import gzip
import shutil
import brotli
import concurrent.futures
from PIL import Image
from moviepy import VideoFileClip
from tqdm import tqdm

# ==========================================
# CONFIGURATION
# ==========================================
PROJECT_ROOT = r"C:\Users\omerb\.gemini\antigravity\scratch\selanikli"
ASSETS_DIR = os.path.join(PROJECT_ROOT, "images")
OUTPUT_DIR = ASSETS_DIR # Saving alongside for easier linking, or could use 'dist'
MAX_WIDTH = 1920

# Compression Settings
WEBP_QUALITY = 75   # Comparable to Squoosh default
WEBP_METHOD = 6     # 6 = Best compression (slowest)
VIDEO_CRF = 26      # Constant Rate Factor (18-28 is good range, higher = smaller)
VIDEO_PRESET = 'medium' # Balance between speed and compression

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

# ==========================================
# COMPRESSION LOGIC
# ==========================================
def process_image(file_path):
    """
    Compresses image to WebP format.
    """
    try:
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        
        # Skip existing webp
        if ext.lower() == '.webp': 
            return None

        # Target filename
        new_filename = f"{name}.webp"
        new_file_path = os.path.join(os.path.dirname(file_path), new_filename)

        img = Image.open(file_path)
        
        # Resize if huge
        if img.width > MAX_WIDTH:
            ratio = MAX_WIDTH / img.width
            new_height = int(img.height * ratio)
            img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
            
        # Save as WebP
        img.save(new_file_path, "WEBP", quality=WEBP_QUALITY, method=WEBP_METHOD)
        
        old_size, new_size, ratio = benchmark(file_path, new_file_path)
        
        return {
            "type": "image",
            "original": filename,
            "new": new_filename,
            "old_size": old_size,
            "new_size": new_size,
            "ratio": ratio
        }
    except Exception as e:
        return {"error": str(e), "file": file_path}

def process_video(file_path):
    """
    Re-encodes video using H.264 with optimized settings.
    """
    try:
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        
        if ext.lower() not in ['.mp4', '.mov', '.avi']:
            return None
            
        if "optimized" in name:
            return None

        new_filename = f"{name}.optimized.mp4"
        new_file_path = os.path.join(os.path.dirname(file_path), new_filename)
        
        temp_path = os.path.join(os.path.dirname(file_path), f"temp_{new_filename}")

        clip = VideoFileClip(file_path)
        
        if clip.w > MAX_WIDTH:
            clip = clip.resized(width=MAX_WIDTH)
            
        clip.write_videofile(
            temp_path, 
            codec="libx264", 
            audio_codec="aac", 
            preset=VIDEO_PRESET, 
            ffmpeg_params=["-crf", str(VIDEO_CRF)],
            logger=None
        )
        clip.close()
        
        if os.path.exists(new_file_path):
            os.remove(new_file_path)
        os.rename(temp_path, new_file_path)
        
        old_size, new_size, ratio = benchmark(file_path, new_file_path)
        
        return {
            "type": "video",
            "original": filename,
            "new": new_filename,
            "old_size": old_size,
            "new_size": new_size,
            "ratio": ratio
        }
    except Exception as e:
        return {"error": str(e), "file": file_path}

def process_text(file_path):
    """
    Compresses text files (HTML, CSS, JS) with Gzip and Brotli.
    """
    try:
        if not os.path.exists(file_path): return None
        
        with open(file_path, 'rb') as f:
            data = f.read()
            
        with gzip.open(file_path + '.gz', 'wb') as f_out:
            f_out.write(data)
            
        with open(file_path + '.br', 'wb') as f_out:
            f_out.write(brotli.compress(data))
            
        return {"type": "text", "file": os.path.basename(file_path)}
    except Exception as e:
        return {"error": str(e), "file": file_path}

# ==========================================
# ORCHESTRATOR
# ==========================================
def update_code_references(replacements):
    """
    Updates HTML/CSS/JS files to point to new optimized assets.
    """
    target_files = [
        os.path.join(PROJECT_ROOT, "index.html"),
        os.path.join(PROJECT_ROOT, "styles.css"),
        os.path.join(PROJECT_ROOT, "script.js")
    ]
    
    count = 0
    for file_path in target_files:
        if not os.path.exists(file_path): continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        for rep in replacements:
            if rep['type'] in ['image', 'video']:
                old_ref = f"images/{rep['original']}"
                new_ref = f"images/{rep['new']}"
                content = content.replace(old_ref, new_ref)
                
                if rep['original'] in content and rep['new'] not in content:
                     content = content.replace(rep['original'], rep['new'])

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            count += 1
            
    print(f"\nUpdated references in {count} code files.")

def main():
    print("Starting High-Performance Asset Compression")
    print(f"Target: {ASSETS_DIR}")
    print(f"Settings: WebP Q{WEBP_QUALITY}, H.264 CRF{VIDEO_CRF}, Multi-threaded")
    
    images = []
    videos = []
    for ext in ['*.png', '*.jpg', '*.jpeg']:
        images.extend(glob.glob(os.path.join(ASSETS_DIR, ext)))
    
    for ext in ['*.mp4']:
        videos.extend(glob.glob(os.path.join(ASSETS_DIR, ext)))
        
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_file = {executor.submit(process_image, img): img for img in images}
        
        for vid in videos:
             future_to_file[executor.submit(process_video, vid)] = vid

        for future in tqdm(concurrent.futures.as_completed(future_to_file), total=len(future_to_file), unit="file"):
            res = future.result()
            if res:
                if "error" in res:
                    print(f"Error: {res['error']}")
                else:
                    results.append(res)

    text_files = [
        os.path.join(PROJECT_ROOT, "index.html"),
        os.path.join(PROJECT_ROOT, "styles.css"),
        os.path.join(PROJECT_ROOT, "script.js")
    ]
    for txt in text_files:
        process_text(txt)

    print("\n" + "="*50)
    print("COMPRESSION REPORT")
    print("="*50)
    print(f"{'File':<30} | {'Old Size':<10} | {'New Size':<10} | {'Reduction':<10}")
    print("-" * 70)
    
    replacements = []
    total_saved = 0
    
    for res in sorted(results, key=lambda x: x['ratio'], reverse=True):
        print(f"{res['original']:<30} | {format_size(res['old_size']):<10} | {format_size(res['new_size']):<10} | {res['ratio']:.1f}%")
        replacements.append(res)
        total_saved += (res['old_size'] - res['new_size'])

    print("-" * 70)
    print(f"Total Space Saved: {format_size(total_saved)}")
    
    update_code_references(replacements)
    print("\nCompression & Deployment Prep Complete!")

if __name__ == "__main__":
    main()
