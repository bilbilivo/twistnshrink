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

install() {
    setup_venv

    ICON_PNG="$SCRIPT_DIR/pic_resizer.png"
    if [ ! -f "$ICON_PNG" ] && [ -f "$SCRIPT_DIR/pic_resizer.ico" ]; then
        echo "Converting icon to PNG..."
        "$VENV_DIR/bin/python" -c "
from PIL import Image
Image.open('$SCRIPT_DIR/pic_resizer.ico').save('$ICON_PNG', 'PNG')
"
    fi

    APPS_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
    mkdir -p "$APPS_DIR"
    DESKTOP_FILE="$APPS_DIR/pic-resizer.desktop"

    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=Pic Resizer
Comment=Batch image resizer and rotator
Icon=$ICON_PNG
Exec=$SCRIPT_DIR/launch.sh
Terminal=false
Categories=Graphics;
StartupWMClass=pic_resizer
EOF

    # Refresh the desktop database so the launcher picks up the new entry
    if command -v update-desktop-database &>/dev/null; then
        update-desktop-database "$APPS_DIR" 2>/dev/null || true
    fi

    echo "Installed: $DESKTOP_FILE"
    echo "Search 'Pic Resizer' in your application launcher to start."
}

uninstall() {
    APPS_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
    DESKTOP_FILE="$APPS_DIR/pic-resizer.desktop"

    if [ -f "$DESKTOP_FILE" ]; then
        rm "$DESKTOP_FILE"
        if command -v update-desktop-database &>/dev/null; then
            update-desktop-database "$APPS_DIR" 2>/dev/null || true
        fi
        echo "Removed: $DESKTOP_FILE"
    else
        echo "Nothing to remove (not installed)."
    fi
}

ACTION="${1:-launch}"
case "$ACTION" in
    launch)
        setup_venv
        exec "$VENV_DIR/bin/python" pic_resizer.py
        ;;
    install)
        install
        ;;
    uninstall)
        uninstall
        ;;
    *)
        echo "Usage: $0 {launch|install|uninstall}"
        echo "       launch      Start pic_resizer (default)"
        echo "       install     Add to application launcher"
        echo "       uninstall   Remove from application launcher"
        exit 2
        ;;
esac
