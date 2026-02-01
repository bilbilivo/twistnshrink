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

setup_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        echo "First run — creating virtual environment..."
        "$PYTHON" -m venv "$VENV_DIR"
        echo "Installing dependencies..."
        "$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
    fi
}

setup() {
    setup_venv

    ICON_PNG="$SCRIPT_DIR/pic_resizer.png"
    if [ ! -f "$ICON_PNG" ] && [ -f "$SCRIPT_DIR/pic_resizer.ico" ]; then
        echo "Converting icon to PNG..."
        "$VENV_DIR/bin/python" -c "
from PIL import Image
Image.open('$SCRIPT_DIR/pic_resizer.ico').save('$ICON_PNG', 'PNG')
"
    fi

    DESKTOP_FILE="$SCRIPT_DIR/pic_resizer.desktop"
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=Pic Resizer
Comment=Batch image resizer and rotator
Icon=$ICON_PNG
Exec="$SCRIPT_DIR/launch.sh"
Terminal=false
EOF

    chmod +x "$DESKTOP_FILE"
    echo "Desktop shortcut created: $DESKTOP_FILE"
    echo "Double-click it from this folder to launch."
}

ACTION="${1:-launch}"
case "$ACTION" in
    launch)
        setup_venv
        exec "$VENV_DIR/bin/python" pic_resizer.py
        ;;
    setup)
        setup
        ;;
    *)
        echo "Usage: $0 {launch|setup}"
        echo "       launch   Start pic_resizer (default)"
        echo "       setup    Create a desktop shortcut"
        exit 2
        ;;
esac
