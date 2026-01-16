# High-Performance Asset Compressor

A multi-threaded Python utility designed to optimize website assets (Images & Videos) for production.

## Features

- **Multi-threaded Execution**: Fast parallel processing.
- **Auto-Ignore**: Smartly skips system folders like `node_modules`, `venv`, and `.git`.
- **Media Optimization**:
  - Images: Converted to WebP (Q75) with best-effort compression.
  - Videos: Re-encoded to H.264 (CRF 26) for optimal web delivery.
- **Smart Skipping**: Prevents re-compression loss by skipping already optimized files.
- **Rich TUI**: Beautiful terminal interface with progress bars and reports.

## Installation

```bash
pip install Pillow moviepy tqdm questionary rich
```

## Usage

```bash
# Interactive mode
python compressor.py

# CLI mode
python compressor.py -i ./path/to/assets
```

## License
MIT
