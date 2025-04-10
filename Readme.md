# NEF to JPG Converter

A Flet-based GUI tool for converting Nikon NEF (RAW) files to JPEG images. This converter offers a multi-threaded processing engine with a real-time preview, progress bar, and abort functionality to streamline and accelerate your conversion workflow.

## Overview

This application allows you to:
- **Select Input/Output folders:** Easily choose the folder containing NEF files and the output folder for JPGs using a built-in directory picker.
- **Adjust Conversion Parameters:** Set the JPEG quality, and if desired, enable resizing and specify the output dimensions.
- **Multi-threaded Conversion:** Improve performance by choosing the number of concurrent threads used for processing your images.
- **Live Preview:** As each NEF file is processed, a thumbnail preview of the current image is shown on the right side of the window.
- **Progress & Abort:** The conversion progress is displayed via a progress bar and status messages. You can abort the conversion process, with visual feedback indicating that the abort was triggered.

## How It Works

1. **User Interface:**  
   The application is built with [Flet](https://flet.dev/) and displays a fixed-size window (900x600) divided into two columns:
   - **Left Column (1/3 width):** Contains the controls and settings – folder selection, JPEG quality, thread count, resize option, output dimensions, and the Convert/Abort buttons.
   - **Right Column (2/3 width):** Displays a centered preview of the currently processed NEF file.

2. **Image Processing:**  
   - The application uses [rawpy](https://github.com/letmaik/rawpy) to read NEF files, and [Pillow](https://python-pillow.org/) to convert and, optionally, resize them.
   - A thumbnail preview (up to 500×500 pixels) is generated for each image and displayed in the preview area.

3. **Multi-threading:**  
   - A `ThreadPoolExecutor` manages multiple threads (the number is user-configurable) to process files concurrently.
   - An abort flag allows the user to cancel processing. Tasks that have not yet started will be skipped once abort is triggered, though files already under processing may complete.

4. **Status Updates:**  
   - Progress is tracked and updated in real time via a progress bar and status messages.
   - The Abort button provides visual feedback ("Aborting...") when pressed.

## Requirements

- Python 3.8 or later
- [Flet](https://pypi.org/project/flet/)
- [rawpy](https://pypi.org/project/rawpy/)
- [Pillow](https://pypi.org/project/Pillow/)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/nef2jpg.git
   cd nef2jpg
