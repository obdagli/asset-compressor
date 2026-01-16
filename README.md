# Asset Compressor

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Code Style](https://img.shields.io/badge/Style-Rich_CLI-purple?style=for-the-badge)

> **Optimize web assets in seconds. Serve faster sites.**

A production-grade, multi-threaded asset optimization engine designed for modern web development. It recursively scans your project, intelligently compresses media into next-gen formats (WebP, H.264), and creates server-ready static assets (Brotli/Gzip) — all while automatically updating your HTML/CSS references.

---

## ⚡ Sample Run

Experience a clean, interactive CLI that respects your time.

```text
$ python compressor.py

   High-Performance Asset Compressor
   Optimize Images, Videos, and Code

? Main Menu: 1. Compress Assets (Images, Video, Code)
? Select target type: Specific Folder
? Enter folder path: ./my-website/assets

Processing 42 files...
[████████████████████████████████████████] 100%

COMPRESSION REPORT
File                           | Old Size   | New Size   | Reduction 
----------------------------------------------------------------------
hero-background.png            | 2.09 MB    | 0.23 MB    | 88.9%
marketing-banner.png           | 1.11 MB    | 0.04 MB    | 96.7%
demo-reel.mp4                  | 13.71 MB   | 12.84 MB   | 6.4%
app.js                         | 0.45 MB    | 0.12 MB    | 73.2%
----------------------------------------------------------------------
Total Space Saved: 16.80 MB

Updated references in 3 code files.
```

---

## 📊 Real-World Benchmarks

Tested on a production restaurant website. The results speak for themselves:

| Asset Type | Input Format | Output Format | Size Reduction | Quality Loss |
|:-----------|:-------------|:--------------|:---------------|:-------------|
| **Photography** | High-Res PNG | **WebP (Q75)** | **~90-97%** | Negligible |
| **Video** | Unoptimized MP4 | **H.264 (CRF 26)** | **~10-20%** | None (Visual) |
| **Graphics** | Logo PNG | **WebP Lossless** | **~25%** | Zero |

> **Result:** Largest Contentful Paint (LCP) dropped from **4.2s** to **0.8s**.

---

## 🔥 Key Features

*   **Smart Automation**: Automatically ignores `node_modules`, `.git`, and `venv` to prevent useless scanning.
*   **Safety First**: Never overwrites your source files. Creates optimized copies (e.g., `image.webp`) alongside originals.
*   **Idempotent**: Detects already-optimized files and skips them to prevent quality degradation.
*   **Code Aware**: Automatically finds references in your `html`, `css`, and `js` files and updates them to point to the new, lighter assets.
*   **Server Ready**: Generates `.br` (Brotli) and `.gz` (Gzip) pre-compressed files for Nginx/Apache/Netlify.

---

## 🛠️ Installation

Requires **Python 3.10+**.

```bash
# Clone the repository
git clone https://github.com/obdagli/asset-compressor.git
cd asset-compressor

# Install dependencies
pip install -r requirements.txt
# OR manually:
pip install Pillow moviepy brotli tqdm questionary rich
```

## 🚀 Usage

### Interactive Mode (Recommended)
Just run the script. The wizard will guide you.
```bash
python compressor.py
```

### Automation / CI Mode
Integrate into your build pipeline using flags.
```bash
# Compress directory
python compressor.py -i ./src/assets

# Decompress static files (debugging)
python compressor.py -i ./dist/index.html.gz -d
```

---

## ⚙️ Configuration

Tweak the top of `compressor.py` to match your needs:

```python
MAX_WIDTH = 1920        # Downscale 4K images/video to 1080p
WEBP_QUALITY = 75       # Balance between size and clarity
VIDEO_CRF = 26          # Higher = Smaller File, Lower = Better Quality
```

---

**License**: MIT  
**Author**: Built for high-performance web engineering.