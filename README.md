# Pic Resizer

Batch image resizer and rotator with a tkinter GUI. Resizes JPEGs to a target file size and max dimension, preserving EXIF data. Also supports batch rotation. Works on Linux, macOS, and Windows.

## Features

- **Batch resize** -- Scale JPEG images so their longest dimension fits within a configurable frame size, then iteratively reduce JPEG quality to meet a target file size (in KB).
- **Batch rotate** -- Rotate JPEG images by 90, 180, or 270 degrees.
- **EXIF preservation** -- EXIF metadata is preserved through both resize and rotate operations. Orientation tags are applied and then removed so images display correctly everywhere.
- **Configurable settings** -- Max frame size, target file size, file suffix, and rotation angle are all configurable and persisted between sessions via `pic_resizer.ini`.
- **Cross-platform** -- Runs on Linux, macOS, and Windows.

## Requirements

- Python 3.7+
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

Double-click `dist/pic_resizer.exe`, or run from the command line:

```cmd
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

## Building a Windows Executable

See [BUILDING.md](BUILDING.md) for instructions on creating a standalone `.exe` with PyInstaller.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE) -- Copyright 2025 Stephane Belliveau
