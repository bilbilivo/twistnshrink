#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

VENV_DIR="$SCRIPT_DIR/venv"
PYTHON=${PYTHON:-python3}

# Verify tkinter is available (system package, not pip-installable)
if ! "$PYTHON" -c "import tkinter" 2>/dev/null; then
    echo "Error: tkinter is not installed." >&2
    echo "Install it with your system package manager:" >&2
    echo "  Ubuntu/Debian:  sudo apt install python3-tk" >&2
    echo "  Fedora/RHEL:    sudo dnf install python3-tkinter" >&2
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "First run — creating virtual environment..."
    "$PYTHON" -m venv "$VENV_DIR"
    echo "Installing dependencies..."
    "$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
fi

exec "$VENV_DIR/bin/python" pic_resizer.py
