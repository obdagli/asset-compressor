# High-Performance Asset Compressor

A multi-threaded Python utility designed to optimize website assets for production. It uses industry-standard compression algorithms to significantly reduce file sizes while maintaining high visual quality.

## Features

- **Multi-threaded Processing**: Utilizes concurrent execution to process multiple assets in parallel, maximizing performance on modern CPUs.
- **Next-Gen Image Formats**: Automatically converts heavy PNG and JPEG images to WebP, providing superior compression ratios.
- **Video Optimization**: Re-encodes MP4 videos using H.264 (CRF 26) with optimized presets for web delivery.
- **Static Compression**: Generates Brotli (.br) and Gzip (.gz) versions of text assets (HTML, CSS, JS) for efficient server-side delivery.
- **Reference Updating**: Automatically updates project code files (HTML, CSS, JS) to point to the newly optimized asset filenames.
- **Benchmarking**: Provides a detailed report of size reductions and total space saved.

## Technical Specifications

### Image Compression
- **Algorithm**: WebP
- **Quality**: 75 (Variable)
- **Method**: 6 (Best compression effort)
- **Target Width**: 1920px (Max)

### Video Compression
- **Algorithm**: H.264 (libx264)
- **Rate Control**: CRF 26
- **Preset**: Medium
- **Audio**: AAC

### Text Compression
- **Algorithms**: Brotli, Gzip
- **Compatibility**: Standard browser-side decompression supported by modern browsers and servers (Nginx, Apache, Netlify).

## Setup and Usage

1. **Requirements**: Python 3.10+
2. **Installation**:
   ```bash
   pip install Pillow moviepy brotli tqdm
   ```
3. **Execution**:
   Configure the `PROJECT_ROOT` and `ASSETS_DIR` paths in `compressor.py`, then run:
   ```bash
   python compressor.py
   ```

## Performance Benchmark

In a recent deployment, this tool achieved:
- **Total Size Reduction**: 12.01 MB
- **Highest Single-File Reduction**: 97.0%
- **Average Image Reduction**: ~90%

## License

MIT License
