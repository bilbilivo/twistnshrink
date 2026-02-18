# Pic Resizer

[![CI](https://github.com/bilbilivo/pic_resizer/actions/workflows/ci.yml/badge.svg)](https://github.com/bilbilivo/pic_resizer/actions/workflows/ci.yml)

Batch image resizer and rotator with a tkinter GUI. Resizes JPEGs to a target file size and max dimension, preserving EXIF data. Also supports batch rotation. Works on Linux, macOS, and Windows.

## Download

**Windows** -- Download the latest `pic_resizer.exe` from the [Releases page](https://github.com/bilbilivo/pic_resizer/releases).

**Linux / macOS** -- Run from source (see [Installation](#installation) below).

## Features

- **Batch resize** -- Scale JPEG images so their longest dimension fits within a configurable frame size, then iteratively reduce JPEG quality to meet a target file size (in KB).
- **Batch rotate** -- Rotate JPEG images by 90, 180, or 270 degrees.
- **EXIF preservation** -- EXIF metadata is preserved through both resize and rotate operations. Orientation tags are applied and then removed so images display correctly everywhere.
- **Configurable settings** -- Max frame size, target file size, file suffix, and rotation angle are all configurable and persisted between sessions via `pic_resizer.ini`.
- **Cross-platform** -- Runs on Linux, macOS, and Windows.

## Requirements

- Python 3.9+
- `python3-tk` (system package -- see installation below)

## Installation

Clone the repository:

```bash
git clone https://github.com/bilbilivo/pic_resizer.git
cd pic_resizer
```

On Linux/macOS, install the `tkinter` system package if you don't already have it:

```bash
# Ubuntu / Debian
sudo apt install python3-tk

# Fedora / RHEL
sudo dnf install python3-tkinter

# macOS (Homebrew)
brew install python-tk
```

The launcher handles virtual environment creation and dependency installation automatically on first run.

## Usage

### Linux / macOS

```bash
./launch.sh
```

The launcher will:
1. Create a Python virtual environment (first run only)
2. Install dependencies from `requirements.txt`
3. Launch the GUI

### Windows

Download the `.exe` from the [Releases page](https://github.com/bilbilivo/pic_resizer/releases), or run from source:

```cmd
python -m venv venv
venv\Scripts\activate
pip install .
python pic_resizer.py
```

### Desktop Shortcut (Linux)

Create a double-clickable desktop shortcut:

```bash
./launch.sh setup
```

This converts the icon and generates a `.desktop` file in the repo folder.

## Configuration

Settings are stored in `pic_resizer.ini` (created automatically on first run):

| Setting | Default | Description |
|---|---|---|
| `MaxFrameSize` | `900` | Maximum dimension (px) for the longest side |
| `TargetSizeKB` | `200` | Target file size in kilobytes |
| `FileSuffix` | `_resize` | Suffix appended to output filenames |
| `RotateAngle` | `90` | Default rotation angle (90, 180, or 270) |

## Development

```bash
python3 -m venv venv
source venv/bin/activate
pip install ".[dev]"

# Lint
ruff check .

# Run tests
pytest -v
```

## Building a Windows Executable

See [BUILDING.md](BUILDING.md) for instructions on creating a standalone `.exe` with PyInstaller.

Releases are also built automatically via GitHub Actions when a version tag is pushed.

**Release workflow best practice:**
- Before pushing a version tag, always push your changes to `main` and wait for all CI checks (GitHub Actions) to pass.
- Only after verifying that `main` is green, create and push the version tag (see [CONTRIBUTING.md](CONTRIBUTING.md) for details).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE) -- Copyright 2025 Stephane Belliveau
