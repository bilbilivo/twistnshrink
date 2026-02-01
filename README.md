# PIC RESIZER

Batch image resizer and rotator with a tkinter GUI. Resizes JPEGs to a target file size and max dimension, preserving EXIF data. Works on Linux, macOS, and Windows.

**Quick overview**
- Clone the repo and run the launcher. It creates the virtual environment and installs dependencies automatically on first run.

**Requirements**
- Python 3.7+
- `python3-tk` (system package — see installation below)

Installation
------------
Clone the repository:

```bash
git clone https://github.com/bilbilivo/pic_resizer.git
cd pic_resizer
```

On Linux/macOS, install the `tkinter` system package if you don't already have it:

```bash
sudo apt install python3-tk          # Ubuntu / Debian
sudo dnf install python3-tkinter     # Fedora / RHEL
```

The launcher handles virtual environment creation and dependency installation automatically on first run.

Running the app
---------------

Unix / macOS:

```bash
./launch.sh
```

Windows:

Double-click `dist/pic_resizer.exe`.

Desktop shortcut
----------------

Create a double-clickable desktop shortcut (Unix / macOS only):

```bash
./launch.sh setup
```

This converts the icon and generates a `.desktop` file in the repo folder.
