# Asset Compressor

A multi-threaded Python utility designed to optimize website assets for production. It uses industry-standard compression algorithms to reduce file sizes while maintaining visual quality.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

## Overview

This tool recursively scans a project directory, compresses images and videos into next-generation formats, and generates pre-compressed text assets for server-side delivery. It is designed for CI/CD pipelines and local development workflows.

## Key Features

*   **Multi-threaded Processing**: Uses concurrent execution to process assets in parallel.
*   **Smart Filtering**: Automatically ignores system directories (node_modules, venv, .git).
*   **Image Optimization**: Converts PNG and JPEG images to WebP format (Quality 75).
*   **Video Optimization**: Re-encodes MP4 videos to H.264 (CRF 26) with optimized presets.
*   **Text Compression**: Generates Brotli (.br) and Gzip (.gz) versions of HTML, CSS, and JS files.
*   **Reference Updating**: Automatically updates file references in source code to point to the new optimized assets.
*   **Idempotency**: Skips files that have already been optimized to prevent processing loops.

## Installation

Requires Python 3.10 or higher.

```bash
pip install Pillow moviepy brotli tqdm questionary rich
```

## Usage

### Interactive Mode
Run the script without arguments to start the interactive wizard:

```bash
python compressor.py
```

### CLI Mode
Run with arguments for batch processing or automation:

```bash
# Compress directory
python compressor.py -i ./src/assets

# Decompress specific file
python compressor.py -i ./dist/index.html.gz -d
```

## Technical Specifications

| Asset Type | Input Format | Output Format | Settings |
|:-----------|:-------------|:--------------|:---------|
| Image | PNG, JPEG | WebP | Quality: 75, Method: 6 |
| Video | MP4 | H.264 (MP4) | CRF: 26, Preset: Medium |
| Text | HTML, CSS, JS | Brotli, Gzip | Standard Compression |

## Benchmarks

Tested on production assets:

*   **Images**: ~90% reduction (High-Res PNG to WebP).
*   **Videos**: ~10-20% reduction (Re-encoding).
*   **Total Savings**: 12.01 MB reduced on the sample project.

## License

MIT License
