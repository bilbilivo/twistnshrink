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
        with open(CONFIG_FILE, "w") as fh:
            config.write(fh)

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
        exif = image._getexif()
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
    except (AttributeError, KeyError, IndexError):
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

    suffix = suffix_entry.get() or "_resize"

    # Save current values to config
    config["DEFAULT"]["MaxFrameSize"] = str(max_frame_size)
    config["DEFAULT"]["TargetSizeKB"] = str(target_size_kb)
    config["DEFAULT"]["FileSuffix"] = suffix
    with open(CONFIG_FILE, "w") as configfile:
        config.write(configfile)

    # Create and show progress window
    progress_window = tk.Toplevel(root)
    progress_window.title("Processing Images")
    progress_window.geometry("300x100")
    progress_label = ttk.Label(progress_window, text="Processing images...")
    progress_label.pack(pady=10)
    progress_bar = ttk.Progressbar(progress_window, length=200, mode="determinate")
    progress_bar.pack(pady=10)

    def process_images() -> None:
        count = 0
        total = len(input_files)
        failures: list[str] = []
        for img_path in input_files:
            try:
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

                    filename = os.path.basename(img_path)
                    name, ext = os.path.splitext(filename)
                    new_filename = f"{name}{suffix}{ext}"
                    output_path = os.path.join(output_dir, new_filename)

                    with open(output_path, "wb") as f:
                        f.write(img_data)
                count += 1
                c, t = count, total
                progress_window.after(
                    0,
                    lambda c=c, t=t: (
                        progress_bar.__setitem__("value", (c / t) * 100),
                        progress_label.config(text=f"Processing image {c} of {t}"),
                    ),
                )
            except Exception as e:
                failures.append(f"{img_path}: {e}")

        def finish() -> None:
            progress_window.destroy()
            if failures:
                failure_report = "\n".join(failures)
                messagebox.showwarning(
                    "Processing Complete",
                    f"Processed {count}/{total} images successfully.\n\n"
                    f"The following images failed:\n{failure_report}",
                )
            else:
                messagebox.showinfo(
                    "Complete", f"Successfully resized {count}/{total} images!"
                )

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

    suffix = suffix_entry.get() or "_rotate"

    # Save current rotation angle to config
    config["DEFAULT"]["RotateAngle"] = str(rotate_angle)
    with open(CONFIG_FILE, "w") as configfile:
        config.write(configfile)

    # Create and show progress window
    progress_window = tk.Toplevel(root)
    progress_window.title("Rotating Images")
    progress_window.geometry("300x100")
    progress_label = ttk.Label(progress_window, text="Rotating images...")
    progress_label.pack(pady=10)
    progress_bar = ttk.Progressbar(progress_window, length=200, mode="determinate")
    progress_bar.pack(pady=10)

    def process_images() -> None:
        count = 0
        total = len(input_files)
        failures: list[str] = []
        for img_path in input_files:
            try:
                with Image.open(img_path) as img:
                    img = fix_orientation(img)

                    # Preserve EXIF data through rotation
                    exif_bytes = _load_exif_safe(img)

                    rotated_img = rotate_image(img, rotate_angle)

                    filename = os.path.basename(img_path)
                    name, ext = os.path.splitext(filename)
                    new_filename = f"{name}{suffix}{ext}"
                    output_path = os.path.join(output_dir, new_filename)

                    if exif_bytes:
                        rotated_img.save(output_path, format="JPEG", exif=exif_bytes)
                    else:
                        rotated_img.save(output_path, format="JPEG")
                count += 1
                c, t = count, total
                progress_window.after(
                    0,
                    lambda c=c, t=t: (
                        progress_bar.__setitem__("value", (c / t) * 100),
                        progress_label.config(text=f"Rotating image {c} of {t}"),
                    ),
                )
            except Exception as e:
                failures.append(f"{img_path}: {e}")

        def finish() -> None:
            progress_window.destroy()
            if failures:
                failure_report = "\n".join(failures)
                messagebox.showwarning(
                    "Rotation Complete",
                    f"Rotated {count}/{total} images successfully.\n\n"
                    f"The following images failed:\n{failure_report}",
                )
            else:
                messagebox.showinfo(
                    "Complete", f"Rotated {count}/{total} images successfully!"
                )

        progress_window.after(0, finish)

    threading.Thread(target=process_images, daemon=True).start()


# ---------------------------------------------------------------------------
# GUI setup
# ---------------------------------------------------------------------------


def main() -> None:
    """Build the GUI and start the tkinter event loop."""
    global root, config, max_frame_size_entry, target_size_entry, suffix_entry
    global rotate_angle_var

    config = load_config()

    root = tk.Tk()
    root.title("Batch Image Resizer and Rotator")

    # Configure style
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", font=("Arial", 12, "bold"), padding=10)

    # Create and pack widgets
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Resize section
    ttk.Label(frame, text="Max Frame Size:").grid(row=0, column=0, sticky=tk.W, pady=5)
    max_frame_size_entry = ttk.Entry(frame, width=20)
    max_frame_size_entry.insert(0, config["DEFAULT"]["MaxFrameSize"])
    max_frame_size_entry.grid(row=0, column=1, pady=5)

    ttk.Label(frame, text="Target Size (KB):").grid(
        row=1, column=0, sticky=tk.W, pady=5
    )
    target_size_entry = ttk.Entry(frame, width=20)
    target_size_entry.insert(0, config["DEFAULT"]["TargetSizeKB"])
    target_size_entry.grid(row=1, column=1, pady=5)

    ttk.Label(frame, text="File Suffix:").grid(row=2, column=0, sticky=tk.W, pady=5)
    suffix_entry = ttk.Entry(frame, width=20)
    suffix_entry.insert(0, config["DEFAULT"]["FileSuffix"])
    suffix_entry.grid(row=2, column=1, pady=5)

    resize_button = ttk.Button(
        frame,
        text="Select and Resize Images",
        command=resize_images,
        style="TButton",
    )
    resize_button.grid(row=3, column=0, columnspan=2, pady=20)

    # Rotate section
    rotate_frame = ttk.Frame(root, padding="10")
    rotate_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    ttk.Label(rotate_frame, text="Rotate Angle:").grid(
        row=0, column=0, sticky=tk.W, pady=5
    )
    rotate_angle_var = tk.StringVar(value=config["DEFAULT"]["RotateAngle"])
    ttk.Radiobutton(
        rotate_frame, text="90\u00b0", variable=rotate_angle_var, value="90"
    ).grid(row=0, column=1, pady=5)
    ttk.Radiobutton(
        rotate_frame, text="180\u00b0", variable=rotate_angle_var, value="180"
    ).grid(row=0, column=2, pady=5)
    ttk.Radiobutton(
        rotate_frame, text="270\u00b0", variable=rotate_angle_var, value="270"
    ).grid(row=0, column=3, pady=5)

    rotate_button = ttk.Button(
        rotate_frame,
        text="Select and Rotate Images",
        command=rotate_images,
        style="TButton",
    )
    rotate_button.grid(row=1, column=0, columnspan=4, pady=20)

    # Configure grid expansion
    for child in frame.winfo_children():
        child.grid_configure(padx=5)
    for child in rotate_frame.winfo_children():
        child.grid_configure(padx=5)

    root.mainloop()


if __name__ == "__main__":
    main()
