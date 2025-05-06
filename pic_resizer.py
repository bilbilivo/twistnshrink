import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ExifTags
import io
import piexif
import threading
import configparser

# Load configuration
config = configparser.ConfigParser()
config_file = 'pic_resizer.ini'

if os.path.exists(config_file):
    config.read(config_file)
    # Check if all settings exist, if not, add them
    if 'MaxFrameSize' not in config['DEFAULT']:
        config['DEFAULT']['MaxFrameSize'] = '900'
    if 'TargetSizeKB' not in config['DEFAULT']:
        config['DEFAULT']['TargetSizeKB'] = '200'
    if 'FileSuffix' not in config['DEFAULT']:
        config['DEFAULT']['FileSuffix'] = '_resize'
    if 'RotateAngle' not in config['DEFAULT']:
        config['DEFAULT']['RotateAngle'] = '90'
    with open(config_file, 'w') as configfile:
        config.write(configfile)
else:
    # Create default configuration
    config['DEFAULT'] = {
        'MaxFrameSize': '900',
        'TargetSizeKB': '200',
        'FileSuffix': '_resize',
        'RotateAngle': '90'
    }
    with open(config_file, 'w') as configfile:
        config.write(configfile)

def resize_image(img, target_size_kb, exif_bytes):
    quality = 95
    output = io.BytesIO()
    while True:
        if exif_bytes:
            img.save(output, format='JPEG', quality=quality, exif=exif_bytes)
        else:
            img.save(output, format='JPEG', quality=quality)
        size_kb = len(output.getvalue()) / 1024
        if size_kb <= target_size_kb or quality <= 20:
            break
        quality -= 5
        output.seek(0)
        output.truncate()
    return output.getvalue()

def fix_orientation(image):
    try:
        exif = image._getexif()
        if exif:
            orientation_key = next((k for k, v in ExifTags.TAGS.items() if v == 'Orientation'), None)
            if orientation_key and orientation_key in exif:
                orientation = exif[orientation_key]
                if orientation == 2:
                    image = image.transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 3:
                    image = image.transpose(Image.ROTATE_180)
                elif orientation == 4:
                    image = image.transpose(Image.FLIP_TOP_BOTTOM)
                elif orientation == 5:
                    image = image.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_90)
                elif orientation == 6:
                    image = image.transpose(Image.ROTATE_270)
                elif orientation == 7:
                    image = image.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
                elif orientation == 8:
                    image = image.transpose(Image.ROTATE_90)
    except (AttributeError, KeyError, IndexError):
        # No EXIF orientation info, or it couldn't be applied
        pass
    return image

def rotate_image(image, angle):
    if angle == 90:
        return image.transpose(Image.ROTATE_90)
    elif angle == 180:
        return image.transpose(Image.ROTATE_180)
    elif angle == 270:
        return image.transpose(Image.ROTATE_270)
    else:
        return image

def resize_images():
    input_files = filedialog.askopenfilenames(
        title="Select Images to Resize",
        filetypes=[("JPEG files", "*.jpg *.jpeg")]
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
    config['DEFAULT']['MaxFrameSize'] = str(max_frame_size)
    config['DEFAULT']['TargetSizeKB'] = str(target_size_kb)
    config['DEFAULT']['FileSuffix'] = suffix
    with open(config_file, 'w') as configfile:
        config.write(configfile)

    # Create and show progress window
    progress_window = tk.Toplevel(root)
    progress_window.title("Processing Images")
    progress_window.geometry("300x100")
    progress_label = ttk.Label(progress_window, text="Processing images...")
    progress_label.pack(pady=10)
    progress_bar = ttk.Progressbar(progress_window, length=200, mode='determinate')
    progress_bar.pack(pady=10)

    def process_images():
        count = 0
        total = len(input_files)
        failures = []  # Track failed images with error details
        for img_path in input_files:
            try:
                with Image.open(img_path) as img:
                    # Fix orientation
                    img = fix_orientation(img)

                    # Preserve EXIF data
                    exif_dict = piexif.load(img.info.get("exif", b""))
                    
                    # Remove orientation tag from EXIF
                    if piexif.ImageIFD.Orientation in exif_dict["0th"]:
                        del exif_dict["0th"][piexif.ImageIFD.Orientation]
                    
                    exif_bytes = piexif.dump(exif_dict)

                    # Resize
                    if img.width > img.height:
                        new_width = min(img.width, max_frame_size)
                        new_height = int(new_width * img.height / img.width)
                    else:
                        new_height = min(img.height, max_frame_size)
                        new_width = int(new_height * img.width / img.height)

                    resized_img = img.resize((new_width, new_height), Image.LANCZOS)

                    # Adjust quality to meet target size
                    img_data = resize_image(resized_img, target_size_kb, exif_bytes)

                    # Save the image
                    filename = os.path.basename(img_path)
                    name, ext = os.path.splitext(filename)
                    new_filename = f"{name}{suffix}{ext}"
                    output_path = os.path.join(output_dir, new_filename)
                    
                    with open(output_path, 'wb') as f:
                        f.write(img_data)
                count += 1
                progress_bar['value'] = (count / total) * 100
                progress_label['text'] = f"Processing image {count} of {total}"
                progress_window.update()
            except Exception as e:
                failures.append(f"{img_path}: {str(e)}")
                # print(f"Error processing {img_path}: {str(e)}")

        progress_window.destroy()
        
        
        # Generate message for completion
        # messagebox.showinfo("Complete", f"Resized {count} images successfully!")
        if failures:
            failure_report = "\n".join(failures)
            messagebox.showwarning(
                "Processing Complete", 
                f"Processed {count}/{total} images successfully.\n\n"
                f"The following images failed:\n{failure_report}"
            )
        else:
            messagebox.showinfo("Complete", f"Successfully resized {count}/{total} images!")

    # Run image processing in a separate thread
    threading.Thread(target=process_images, daemon=True).start()

def rotate_images():
    input_files = filedialog.askopenfilenames(
        title="Select Images to Rotate",
        filetypes=[("JPEG files", "*.jpg *.jpeg")]
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
    config['DEFAULT']['RotateAngle'] = str(rotate_angle)
    with open(config_file, 'w') as configfile:
        config.write(configfile)

    # Create and show progress window
    progress_window = tk.Toplevel(root)
    progress_window.title("Rotating Images")
    progress_window.geometry("300x100")
    progress_label = ttk.Label(progress_window, text="Rotating images...")
    progress_label.pack(pady=10)
    progress_bar = ttk.Progressbar(progress_window, length=200, mode='determinate')
    progress_bar.pack(pady=10)

    def process_images():
        count = 0
        total = len(input_files)
        for img_path in input_files:
            try:
                with Image.open(img_path) as img:
                    # Fix orientation
                    img = fix_orientation(img)

                    # Rotate the image
                    rotated_img = rotate_image(img, rotate_angle)

                    # Save the image
                    filename = os.path.basename(img_path)
                    name, ext = os.path.splitext(filename)
                    new_filename = f"{name}{suffix}{ext}"
                    output_path = os.path.join(output_dir, new_filename)
                    rotated_img.save(output_path)
                count += 1
                progress_bar['value'] = (count / total) * 100
                progress_label['text'] = f"Rotating image {count} of {total}"
                progress_window.update()
            except Exception as e:
                print(f"Error processing {img_path}: {str(e)}")

        progress_window.destroy()
        messagebox.showinfo("Complete", f"Rotated {count} images successfully!")

    # Run image rotation in a separate thread
    threading.Thread(target=process_images, daemon=True).start()

# Create main window
root = tk.Tk()
root.title("Batch Image Resizer and Rotator")

# Configure style
style = ttk.Style()
style.theme_use('clam')
style.configure('TButton', font=('Arial', 12, 'bold'), padding=10)

# Create and pack widgets
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Resize section
ttk.Label(frame, text="Max Frame Size:").grid(row=0, column=0, sticky=tk.W, pady=5)
max_frame_size_entry = ttk.Entry(frame, width=20)
max_frame_size_entry.insert(0, config['DEFAULT']['MaxFrameSize'])
max_frame_size_entry.grid(row=0, column=1, pady=5)

ttk.Label(frame, text="Target Size (KB):").grid(row=1, column=0, sticky=tk.W, pady=5)
target_size_entry = ttk.Entry(frame, width=20)
target_size_entry.insert(0, config['DEFAULT']['TargetSizeKB'])
target_size_entry.grid(row=1, column=1, pady=5)

ttk.Label(frame, text="File Suffix:").grid(row=2, column=0, sticky=tk.W, pady=5)
suffix_entry = ttk.Entry(frame, width=20)
suffix_entry.insert(0, config['DEFAULT']['FileSuffix'])
suffix_entry.grid(row=2, column=1, pady=5)

resize_button = ttk.Button(frame, text="Select and Resize Images", command=resize_images, style='TButton')
resize_button.grid(row=3, column=0, columnspan=2, pady=20)

# Rotate section
rotate_frame = ttk.Frame(root, padding="10")
rotate_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

ttk.Label(rotate_frame, text="Rotate Angle:").grid(row=0, column=0, sticky=tk.W, pady=5)
rotate_angle_var = tk.StringVar(value=config['DEFAULT']['RotateAngle'])
rotate_90_radio = ttk.Radiobutton(rotate_frame, text="90°", variable=rotate_angle_var, value="90")
rotate_90_radio.grid(row=0, column=1, pady=5)
rotate_180_radio = ttk.Radiobutton(rotate_frame, text="180°", variable=rotate_angle_var, value="180")
rotate_180_radio.grid(row=0, column=2, pady=5)
rotate_270_radio = ttk.Radiobutton(rotate_frame, text="270°", variable=rotate_angle_var, value="270")
rotate_270_radio.grid(row=0, column=3, pady=5)

rotate_button = ttk.Button(rotate_frame, text="Select and Rotate Images", command=rotate_images, style='TButton')
rotate_button.grid(row=1, column=0, columnspan=4, pady=20)

# Configure grid expansion
for child in frame.winfo_children(): 
    child.grid_configure(padx=5)
for child in rotate_frame.winfo_children():
    child.grid_configure(padx=5)

# Start the GUI event loop
root.mainloop()