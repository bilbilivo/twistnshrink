"""Batch Image Resizer and Rotator.

A tkinter GUI application for batch processing JPEG images.
Supports resizing to a target file size / max dimension and rotating
by 90, 180, or 270 degrees.  EXIF metadata is preserved in both
operations.
"""

import configparser
import io
import os
import threading
import webbrowser
from typing import Optional

import piexif
from PIL import ExifTags, Image

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
except ImportError:  # allow importing image-processing helpers without tkinter
    tk = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Directory that contains this script (used to resolve config path etc.)
SCRIPT_DIR: str = os.path.dirname(os.path.abspath(__file__))

#: Path to the configuration file (always next to the script).
CONFIG_FILE: str = os.path.join(SCRIPT_DIR, "pic_resizer.ini")

#: Default configuration values (single source of truth).
DEFAULT_CONFIG: dict[str, str] = {
    "MaxFrameSize": "900",
    "TargetSizeKB": "200",
    "FileSuffix": "_resize",
    "RotateAngle": "90",
}

# JPEG quality parameters used by the iterative resize loop.
QUALITY_INITIAL: int = 95
QUALITY_FLOOR: int = 20
QUALITY_STEP: int = 5

# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------


def load_config() -> configparser.ConfigParser:
    """Load (or create) the application configuration file.

    Missing keys are filled in from *DEFAULT_CONFIG* and the file is only
    rewritten when a change was actually needed.
    """
    config = configparser.ConfigParser()
    changed = False

    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        for key, value in DEFAULT_CONFIG.items():
            if key not in config["DEFAULT"]:
                config["DEFAULT"][key] = value
                changed = True
    else:
        config["DEFAULT"] = dict(DEFAULT_CONFIG)
        changed = True

    if changed:
        try:
            with open(CONFIG_FILE, "w") as fh:
                config.write(fh)
        except OSError:
            pass  # Non-fatal: config directory may be read-only

    return config


# ---------------------------------------------------------------------------
# Image processing helpers
# ---------------------------------------------------------------------------


def resize_image(
    img: Image.Image, target_size_kb: float, exif_bytes: Optional[bytes]
) -> bytes:
    """Iteratively reduce JPEG quality until the image is within *target_size_kb*.

    Starts at ``QUALITY_INITIAL`` and decreases in steps of ``QUALITY_STEP``
    until the file size is at or below *target_size_kb* or the quality floor
    (``QUALITY_FLOOR``) is reached.

    Returns the raw JPEG bytes.
    """
    quality = QUALITY_INITIAL
    output = io.BytesIO()
    while True:
        if exif_bytes:
            img.save(output, format="JPEG", quality=quality, exif=exif_bytes)
        else:
            img.save(output, format="JPEG", quality=quality)
        size_kb = len(output.getvalue()) / 1024
        if size_kb <= target_size_kb or quality <= QUALITY_FLOOR:
            break
        quality -= QUALITY_STEP
        output.seek(0)
        output.truncate()
    return output.getvalue()


def fix_orientation(image: Image.Image) -> Image.Image:
    """Apply the EXIF orientation tag and return the corrected image.

    All eight EXIF orientation values are handled.  If the image has no
    EXIF data or no orientation tag the image is returned unchanged.
    """
    try:
        exif = image.getexif()
        if exif:
            orientation_key = next(
                (k for k, v in ExifTags.TAGS.items() if v == "Orientation"), None
            )
            if orientation_key and orientation_key in exif:
                orientation = exif[orientation_key]
                if orientation == 2:
                    image = image.transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 3:
                    image = image.transpose(Image.ROTATE_180)
                elif orientation == 4:
                    image = image.transpose(Image.FLIP_TOP_BOTTOM)
                elif orientation == 5:
                    image = image.transpose(Image.FLIP_LEFT_RIGHT).transpose(
                        Image.ROTATE_90
                    )
                elif orientation == 6:
                    image = image.transpose(Image.ROTATE_270)
                elif orientation == 7:
                    image = image.transpose(Image.FLIP_LEFT_RIGHT).transpose(
                        Image.ROTATE_270
                    )
                elif orientation == 8:
                    image = image.transpose(Image.ROTATE_90)
    except Exception:
        pass
    return image


def rotate_image(image: Image.Image, angle: int) -> Image.Image:
    """Rotate *image* by *angle* degrees (90, 180, or 270).

    Returns the original image unchanged for unrecognised angles.
    """
    if angle == 90:
        return image.transpose(Image.ROTATE_90)
    elif angle == 180:
        return image.transpose(Image.ROTATE_180)
    elif angle == 270:
        return image.transpose(Image.ROTATE_270)
    return image


def _load_exif_safe(img: Image.Image) -> Optional[bytes]:
    """Load EXIF data from *img*, returning ``None`` if unavailable.

    Handles images that have no EXIF data (or corrupt EXIF) without
    raising an exception.
    """
    raw_exif = img.info.get("exif")
    if not raw_exif:
        return None
    try:
        exif_dict = piexif.load(raw_exif)
        # Remove orientation tag (we already applied it via fix_orientation)
        if "0th" in exif_dict and piexif.ImageIFD.Orientation in exif_dict["0th"]:
            del exif_dict["0th"][piexif.ImageIFD.Orientation]
        return piexif.dump(exif_dict)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# GUI actions
# ---------------------------------------------------------------------------


def resize_images() -> None:
    """Open file/directory pickers and batch-resize the selected images."""
    input_files = filedialog.askopenfilenames(
        title="Select Images to Resize",
        filetypes=[("JPEG files", "*.jpg *.jpeg")],
    )
    if not input_files:
        return

    output_dir = filedialog.askdirectory(title="Select Output Directory")
    if not output_dir:
        return

    try:
        target_size_kb = float(target_size_entry.get())
        max_frame_size = int(max_frame_size_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric values.")
        return

    if max_frame_size < 1 or target_size_kb <= 0:
        messagebox.showerror(
            "Error", "Max Frame Size must be >= 1 and Target Size must be > 0."
        )
        return

    # Strip path separators from suffix to prevent directory traversal
    raw_suffix = suffix_entry.get() or "_resize"
    suffix = raw_suffix.replace("/", "").replace("\\", "")

    # Save current values to config
    config["DEFAULT"]["MaxFrameSize"] = str(max_frame_size)
    config["DEFAULT"]["TargetSizeKB"] = str(target_size_kb)
    config["DEFAULT"]["FileSuffix"] = suffix
    try:
        with open(CONFIG_FILE, "w") as configfile:
            config.write(configfile)
    except OSError:
        pass  # Non-fatal: settings will not persist this session

    # Create and show progress window
    progress_window = tk.Toplevel(root)
    progress_window.title("Processing Images")
    progress_window.geometry("300x100")
    # Disable the close button so the user cannot dismiss it mid-processing
    progress_window.protocol("WM_DELETE_WINDOW", lambda: None)
    progress_label = ttk.Label(progress_window, text="Processing images...")
    progress_label.pack(pady=10)
    progress_bar = ttk.Progressbar(progress_window, length=200, mode="determinate")
    progress_bar.pack(pady=10)

    def process_images() -> None:
        count = 0
        total = len(input_files)
        failures: list[str] = []
        skipped: list[str] = []
        for img_path in input_files:
            try:
                filename = os.path.basename(img_path)
                name, ext = os.path.splitext(filename)
                new_filename = f"{name}{suffix}{ext}"
                output_path = os.path.join(output_dir, new_filename)

                if os.path.exists(output_path):
                    skipped.append(new_filename)
                    continue

                with Image.open(img_path) as img:
                    img = fix_orientation(img)

                    exif_bytes = _load_exif_safe(img)

                    # Resize
                    if img.width > img.height:
                        new_width = min(img.width, max_frame_size)
                        new_height = int(new_width * img.height / img.width)
                    else:
                        new_height = min(img.height, max_frame_size)
                        new_width = int(new_height * img.width / img.height)

                    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                    img_data = resize_image(resized_img, target_size_kb, exif_bytes)

                with open(output_path, "wb") as f:
                    f.write(img_data)
                count += 1
                c, t = count, total

                def _update_progress(c: int = c, t: int = t) -> None:
                    progress_bar.configure(value=(c / t) * 100)
                    progress_label.configure(text=f"Processing image {c} of {t}")

                progress_window.after(0, _update_progress)
            except Exception as e:
                failures.append(f"{img_path}: {e}")

        def finish() -> None:
            progress_window.destroy()
            parts = [f"Processed {count}/{total} images successfully."]
            if skipped:
                parts.append(
                    f"\nSkipped {len(skipped)} already-existing file(s):\n"
                    + "\n".join(skipped)
                )
            if failures:
                parts.append(
                    f"\nFailed {len(failures)} file(s):\n" + "\n".join(failures)
                )
            if skipped or failures:
                messagebox.showwarning("Processing Complete", "".join(parts))
            else:
                messagebox.showinfo("Complete", parts[0])

        progress_window.after(0, finish)

    threading.Thread(target=process_images, daemon=True).start()


def rotate_images() -> None:
    """Open file/directory pickers and batch-rotate the selected images."""
    input_files = filedialog.askopenfilenames(
        title="Select Images to Rotate",
        filetypes=[("JPEG files", "*.jpg *.jpeg")],
    )
    if not input_files:
        return

    output_dir = filedialog.askdirectory(title="Select Output Directory")
    if not output_dir:
        return

    try:
        rotate_angle = int(rotate_angle_var.get())
    except ValueError:
        messagebox.showerror("Error", "Please select a valid rotation angle.")
        return

    # Strip path separators from suffix to prevent directory traversal
    raw_suffix = suffix_entry.get() or "_rotate"
    suffix = raw_suffix.replace("/", "").replace("\\", "")

    # Save current rotation angle to config
    config["DEFAULT"]["RotateAngle"] = str(rotate_angle)
    try:
        with open(CONFIG_FILE, "w") as configfile:
            config.write(configfile)
    except OSError:
        pass  # Non-fatal: settings will not persist this session

    # Create and show progress window
    progress_window = tk.Toplevel(root)
    progress_window.title("Rotating Images")
    progress_window.geometry("300x100")
    # Disable the close button so the user cannot dismiss it mid-processing
    progress_window.protocol("WM_DELETE_WINDOW", lambda: None)
    progress_label = ttk.Label(progress_window, text="Rotating images...")
    progress_label.pack(pady=10)
    progress_bar = ttk.Progressbar(progress_window, length=200, mode="determinate")
    progress_bar.pack(pady=10)

    def process_images() -> None:
        count = 0
        total = len(input_files)
        failures: list[str] = []
        skipped: list[str] = []
        for img_path in input_files:
            try:
                filename = os.path.basename(img_path)
                name, ext = os.path.splitext(filename)
                new_filename = f"{name}{suffix}{ext}"
                output_path = os.path.join(output_dir, new_filename)

                if os.path.exists(output_path):
                    skipped.append(new_filename)
                    continue

                with Image.open(img_path) as img:
                    img = fix_orientation(img)

                    # Preserve EXIF data through rotation
                    exif_bytes = _load_exif_safe(img)
                    rotated_img = rotate_image(img, rotate_angle)

                if exif_bytes:
                    rotated_img.save(output_path, format="JPEG", exif=exif_bytes)
                else:
                    rotated_img.save(output_path, format="JPEG")
                count += 1
                c, t = count, total

                def _update_progress(c: int = c, t: int = t) -> None:
                    progress_bar.configure(value=(c / t) * 100)
                    progress_label.configure(text=f"Rotating image {c} of {t}")

                progress_window.after(0, _update_progress)
            except Exception as e:
                failures.append(f"{img_path}: {e}")

        def finish() -> None:
            progress_window.destroy()
            parts = [f"Rotated {count}/{total} images successfully."]
            if skipped:
                parts.append(
                    f"\nSkipped {len(skipped)} already-existing file(s):\n"
                    + "\n".join(skipped)
                )
            if failures:
                parts.append(
                    f"\nFailed {len(failures)} file(s):\n" + "\n".join(failures)
                )
            if skipped or failures:
                messagebox.showwarning("Rotation Complete", "".join(parts))
            else:
                messagebox.showinfo("Complete", parts[0])

        progress_window.after(0, finish)

    threading.Thread(target=process_images, daemon=True).start()


# ---------------------------------------------------------------------------
# Menu actions
# ---------------------------------------------------------------------------

PAYPAL_URL = "https://paypal.me/bilbilivo"
APP_VERSION = "2026.6"


def open_donate() -> None:
    """Open the PayPal donation page in the default web browser."""
    webbrowser.open(PAYPAL_URL)


def show_about() -> None:
    """Show the About dialog with a clickable PayPal link."""
    win = tk.Toplevel(root)
    win.title("About Batch Pic Resizer")
    win.resizable(False, False)

    frame = ttk.Frame(win, padding=20)
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text=f"Batch Pic Resizer  v{APP_VERSION}",
              font=("Arial", 13, "bold")).pack(anchor=tk.W)
    ttk.Label(frame, text="Batch resize and rotate JPEG images.\n"
              "EXIF metadata is preserved.").pack(anchor=tk.W, pady=(8, 0))
    ttk.Label(frame, text="Author: Stephane Belliveau\n"
              "License: MIT").pack(anchor=tk.W, pady=(8, 0))

    ttk.Separator(frame, orient="horizontal").pack(fill=tk.X, pady=12)

    ttk.Label(frame, text="If you find this tool useful, consider buying me a coffee!",
              wraplength=300).pack(anchor=tk.W)

    link = tk.Label(frame, text=PAYPAL_URL, fg="blue", cursor="hand2",
                    font=("Arial", 10, "underline"))
    link.pack(anchor=tk.W, pady=(4, 0))
    link.bind("<Button-1>", lambda _e: webbrowser.open(PAYPAL_URL))

    ttk.Button(frame, text="Close", command=win.destroy).pack(pady=(16, 0))


# ---------------------------------------------------------------------------
# GUI setup
# ---------------------------------------------------------------------------


def main() -> None:
    """Build the GUI and start the tkinter event loop."""
    global root, config, max_frame_size_entry, target_size_entry, suffix_entry
    global rotate_angle_var

    config = load_config()

    root = tk.Tk()
    root.title("Batch Pic Resizer")

    # Configure style
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", font=("Arial", 12, "bold"), padding=10)

    # Menu bar
    menubar = tk.Menu(root)
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="Donate via PayPal", command=open_donate)
    help_menu.add_separator()
    help_menu.add_command(label="About", command=show_about)
    menubar.add_cascade(label="Help", menu=help_menu)
    root.config(menu=menubar)

    # Create and pack widgets
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    # Make both columns expandable for button alignment
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)

    # Resize section
    ttk.Label(frame, text="Max Frame Size:").grid(row=0, column=0, sticky=tk.W, pady=5)
    max_frame_size_entry = ttk.Entry(frame, width=20)
    max_frame_size_entry.insert(0, config["DEFAULT"]["MaxFrameSize"])
    max_frame_size_entry.grid(row=0, column=1, pady=5, sticky=(tk.W, tk.E))

    ttk.Label(frame, text="Target Size (KB):").grid(
        row=1, column=0, sticky=tk.W, pady=5
    )
    target_size_entry = ttk.Entry(frame, width=20)
    target_size_entry.insert(0, config["DEFAULT"]["TargetSizeKB"])
    target_size_entry.grid(row=1, column=1, pady=5, sticky=(tk.W, tk.E))

    ttk.Label(frame, text="File Suffix:").grid(row=2, column=0, sticky=tk.W, pady=5)
    suffix_entry = ttk.Entry(frame, width=20)
    suffix_entry.insert(0, config["DEFAULT"]["FileSuffix"])
    suffix_entry.grid(row=2, column=1, pady=5, sticky=(tk.W, tk.E))

    resize_button = ttk.Button(
        frame,
        text="Select and Resize Images",
        command=resize_images,
        style="TButton",
    )
    resize_button.grid(row=3, column=0, columnspan=2, pady=20, sticky=(tk.W, tk.E))

    # Rotate section (now inside same frame)
    ttk.Label(frame, text="Rotate Angle:").grid(
        row=4, column=0, sticky=tk.W, pady=5
    )
    rotate_angle_var = tk.StringVar(value=config["DEFAULT"]["RotateAngle"])
    ttk.Radiobutton(
        frame, text="90\u00b0", variable=rotate_angle_var, value="90"
    ).grid(row=4, column=1, sticky=tk.W, pady=5)
    ttk.Radiobutton(
        frame, text="180\u00b0", variable=rotate_angle_var, value="180"
    ).grid(row=4, column=1, sticky=tk.N, pady=5, padx=(75,0))
    ttk.Radiobutton(
        frame, text="270\u00b0", variable=rotate_angle_var, value="270"
    ).grid(row=4, column=1, sticky=tk.E, pady=5)

    rotate_button = ttk.Button(
        frame,
        text="Select and Rotate Images",
        command=rotate_images,
        style="TButton",
    )
    rotate_button.grid(row=5, column=0, columnspan=2, pady=20, sticky=(tk.W, tk.E))

    # Configure grid spacing
    for child in frame.winfo_children():
        child.grid_configure(padx=5)

    root.mainloop()


if __name__ == "__main__":
    main()
