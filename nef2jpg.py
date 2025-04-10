import flet as ft
import rawpy
from PIL import Image
from io import BytesIO
import base64
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# A 1×1 transparent PNG in base64; used as a placeholder preview.
TRANSPARENT_1X1_PNG = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAD0lEQVR4nGMAAQAFAAAB"
    "BAAWB+keAAAAAElFTkSuQmCC"
)

# Use LANCZOS if available; otherwise fall back.
try:
    RESAMPLE_FILTER = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE_FILTER = Image.ANTIALIAS

def generate_preview(full_input_path, max_size=(500, 500)):
    """Load a NEF file via rawpy, create a thumbnail JPEG, return as base64 string."""
    with rawpy.imread(full_input_path) as raw:
        rgb = raw.postprocess()
    img = Image.fromarray(rgb)
    img.thumbnail(max_size, RESAMPLE_FILTER)
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def process_file(filename, input_dir, output_dir, quality, resize, width, height, should_stop, page):
    """Process one NEF file: generate preview and perform conversion."""
    if should_stop():
        return None  # Abort processing for this file

    full_input_path = os.path.join(input_dir, filename)

    # Generate preview and update UI (note: these may arrive out-of-order).
    try:
        preview_b64 = generate_preview(full_input_path)
        page.pubsub.send_all(("preview", preview_b64))
    except Exception as e:
        page.pubsub.send_all(("status", f"Error generating preview for {filename}: {e}"))

    # Convert NEF → JPG conversion.
    try:
        with rawpy.imread(full_input_path) as raw:
            rgb = raw.postprocess()
        img = Image.fromarray(rgb)
        if resize:
            img = img.resize((width, height), RESAMPLE_FILTER)
        out_name = os.path.splitext(filename)[0] + ".jpg"
        out_path = os.path.join(output_dir, out_name)
        img.save(out_path, format="JPEG", quality=quality)
    except Exception as e:
        page.pubsub.send_all(("status", f"Error processing {filename}: {e}"))

    return filename

def convert_images(page, input_dir, output_dir, quality, resize, width, height, should_stop, max_workers):
    """Process all NEF files concurrently using a thread pool."""
    nef_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".nef")]
    total = len(nef_files)
    completed = 0

    # Display initial status including how many threads will be used.
    page.pubsub.send_all(f"Found {total} NEF files. Using {max_workers} threads.")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all files to the pool.
        future_to_file = {
            executor.submit(
                process_file,
                filename,
                input_dir,
                output_dir,
                quality,
                resize,
                width,
                height,
                should_stop,
                page,
            ): filename
            for filename in nef_files
        }
        # Process futures as they complete.
        for future in as_completed(future_to_file):
            if should_stop():
                page.pubsub.send_all("Aborted by user.")
                break
            completed += 1
            page.pubsub.send_all(("progress", completed, total))
    page.pubsub.send_all(("status", "Conversion complete."))

def main(page: ft.Page):
    # Fixed window, not resizable.
    page.title = "NEF → JPG Converter"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 900
    page.window_height = 600
    page.window_resizable = False
    page.padding = 10
    page.spacing = 10

    # Left-side controls (1/3 width).
    input_dir = ft.TextField(label="Input Folder", width=250)
    output_dir = ft.TextField(label="Output Folder", width=250)
    quality = ft.TextField(value="85", width=60)
    thread_count = ft.TextField(value="4", width=60)
    resize_switch = ft.Switch(label="Resize?")
    width_field = ft.TextField(value="800", width=60)
    height_field = ft.TextField(value="600", width=60)

    progress_bar = ft.ProgressBar(value=0, width=250)
    console_text = ft.Text(value="", selectable=True)

    # Right-side preview (2/3 width) – larger and centered.
    preview_image = ft.Image(
        width=500,
        height=500,
        fit=ft.ImageFit.CONTAIN,
        src_base64=TRANSPARENT_1X1_PNG,
    )

    # Shared abort flag.
    stop_requested = [False]

    # Directory pickers.
    input_picker = ft.FilePicker()
    output_picker = ft.FilePicker()

    def input_picker_result(e: ft.FilePickerResultEvent):
        if e.path:
            input_dir.value = e.path
            page.update()

    def output_picker_result(e: ft.FilePickerResultEvent):
        if e.path:
            output_dir.value = e.path
            page.update()

    input_picker.on_result = input_picker_result
    output_picker.on_result = output_picker_result
    page.overlay.append(input_picker)
    page.overlay.append(output_picker)

    def pick_input(e):
        input_picker.get_directory_path()

    def pick_output(e):
        output_picker.get_directory_path()

    def run_conversion(e):
        console_text.value = "Starting conversion..."
        progress_bar.value = 0
        preview_image.src_base64 = TRANSPARENT_1X1_PNG
        page.update()

        stop_requested[0] = False  # Reset abort flag
        try:
            q = int(quality.value)
            w = int(width_field.value)
            h = int(height_field.value)
            t = int(thread_count.value)
        except ValueError:
            console_text.value = "Quality, Width, Height, and Thread Count must be integers."
            page.update()
            return

        def do_convert():
            convert_images(
                page,
                input_dir.value,
                output_dir.value,
                q,
                resize_switch.value,
                w,
                h,
                lambda: stop_requested[0],
                t,  # number of threads specified by the user.
            )
        threading.Thread(target=do_convert, daemon=True).start()

    def stop_conversion(e):
        stop_requested[0] = True
        abort_button.text = "Aborting..."
        abort_button.disabled = True
        page.update()

    def on_message(msg):
        if isinstance(msg, tuple):
            kind = msg[0]
            if kind == "status":
                console_text.value = msg[1]
            elif kind == "progress":
                _, completed, total = msg
                if total > 0:
                    progress_bar.value = completed / total
                    console_text.value = f"{completed}/{total} converted..."
            elif kind == "preview":
                preview_image.src_base64 = msg[1]
            page.update()
        else:
            console_text.value = str(msg)
            page.update()

    page.pubsub.subscribe(on_message)

    convert_button = ft.ElevatedButton("Convert", on_click=run_conversion)
    abort_button = ft.ElevatedButton(
        "Abort",
        on_click=stop_conversion,
        bgcolor=ft.Colors.RED_200,
        color=ft.Colors.WHITE,
    )
    pick_input_button = ft.IconButton(icon=ft.Icons.FOLDER_OPEN, on_click=pick_input)
    pick_output_button = ft.IconButton(icon=ft.Icons.FOLDER_OPEN, on_click=pick_output)

    # Build left controls column.
    left_column = ft.Column(
        [
            ft.Text("NEF → JPG Converter", style="titleMedium"),
            ft.Row([input_dir, pick_input_button], spacing=5),
            ft.Row([output_dir, pick_output_button], spacing=5),
            ft.Text("JPEG Quality:"),
            quality,
            ft.Text("Thread Count:"),
            thread_count,
            ft.Row([resize_switch, ft.Text("W:"), width_field, ft.Text("H:"), height_field], spacing=5),
            ft.Row([convert_button, abort_button], spacing=10),
            progress_bar,
            console_text,
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        expand=1,  # 1/3 of the horizontal space.
        spacing=10,
    )

    # Right column: preview image centered in its 2/3 space.
    right_column = ft.Column(
        [preview_image],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=2,  # 2/3 of horizontal space.
    )

    main_row = ft.Row(
        [left_column, right_column],
        expand=True,
        spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    page.add(main_row)

ft.app(target=main)
