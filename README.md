# TwistnShrink

[![CI](https://github.com/bilbilivo/twistnshrink/actions/workflows/ci.yml/badge.svg)](https://github.com/bilbilivo/twistnshrink/actions/workflows/ci.yml)
[![Donate](https://img.shields.io/badge/Donate-PayPal-blue.svg)](https://paypal.me/bilbilivo)

A simple desktop app for batch resizing and rotating JPEG images. Shrinks photos to a target file size while preserving EXIF metadata. Cross-platform (Windows, Linux, macOS).

## Quick Start

### Windows (recommended)

1. Download **`twistnshrink.exe`** from the [latest release](https://github.com/bilbilivo/twistnshrink/releases/latest).
2. Double-click to run -- no installation or Python required.

### Linux / macOS

```bash
git clone https://github.com/bilbilivo/twistnshrink.git
cd twistnshrink
./launch.sh
```

The launcher creates a virtual environment and installs dependencies automatically on first run.

> **Prerequisite:** `python3-tk` must be installed via your system package manager:
>
> | Distro | Command |
> |---|---|
> | Ubuntu / Debian | `sudo apt install python3-tk` |
> | Fedora / RHEL | `sudo dnf install python3-tkinter` |
> | macOS (Homebrew) | `brew install python-tk` |

## How to Use

1. Launch the app (`.exe` on Windows, `./launch.sh` on Linux/macOS).
2. **To resize** -- Set the *Max Frame Size* (longest side in pixels) and *Target Size* (in KB), then click **Select and Resize Images**. Pick your JPEG files, then choose an output folder.
3. **To rotate** -- Select a rotation angle (90, 180, or 270), then click **Select and Rotate Images**. Pick your JPEG files, then choose an output folder.
4. Output files are saved with a configurable suffix (default `_resize` / `_rotate`). Existing files in the output folder are skipped, never overwritten.

Settings are remembered between sessions.

---

## Features

- **Batch resize** -- Scale JPEGs so the longest side fits within a configurable frame size, then iteratively reduce JPEG quality to meet a target file size (KB).
- **Batch rotate** -- Rotate JPEGs by 90, 180, or 270 degrees.
- **EXIF preservation** -- Metadata is preserved. Orientation tags are applied and then stripped so images display correctly everywhere.
- **Configurable** -- Max frame size, target file size, file suffix, and rotation angle are persisted between sessions via `twistnshrink.ini`.
- **Cross-platform** -- Runs on Windows (standalone `.exe`), Linux, and macOS.

## Configuration

Settings are stored in `twistnshrink.ini` (created automatically on first run):

| Setting | Default | Description |
|---|---|---|
| `MaxFrameSize` | `900` | Maximum dimension (px) for the longest side |
| `TargetSizeKB` | `200` | Target file size in kilobytes |
| `FileSuffix` | `_resize` | Suffix appended to output filenames |
| `RotateAngle` | `90` | Default rotation angle (90, 180, or 270) |

## Linux Desktop Launcher

Add TwistnShrink to your application menu (GNOME, KDE, etc.):

```bash
./launch.sh install
```

Then search for **TwistnShrink** in your launcher. To remove:

```bash
./launch.sh uninstall
```

## Advanced: Running from Source on Windows

If you prefer not to use the `.exe`, you can run from source:

```cmd
python -m venv venv
venv\Scripts\activate
pip install .
python twistnshrink.py
```

Requires Python 3.9+.

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

See [BUILDING.md](BUILDING.md) for instructions on creating a standalone `.exe` with PyInstaller. Releases are also built automatically via GitHub Actions when a version tag is pushed.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

If you find this tool useful, consider [buying me a coffee](https://paypal.me/bilbilivo).

## License

[MIT](LICENSE) -- Copyright 2025-2026 Stephane Belliveau

Application icon derived from [Google Material Icons](https://github.com/google/material-design-icons) (Apache 2.0).
