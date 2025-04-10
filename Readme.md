# NEF to JPG Converter

A Flet-based GUI tool for converting Nikon NEF (RAW) files to JPEG images.  
Multi-threaded. Real-time preview. Abortable.

Built for speed and simplicity.


![image](https://github.com/user-attachments/assets/8f775b23-a19e-4e9d-a38b-ae70acaeeeaa)

---

## Features

- Select input/output folders.
- Adjustable JPEG quality.
- Optional resize with custom width/height.
- Multi-threaded conversion (user-defined thread count).
- Live preview of current image being converted.
- Progress bar + status updates.
- Abort button to cancel processing.

---

## How It Works

1. Built with [Flet](https://flet.dev/) for cross-platform GUI.
2. Uses [rawpy](https://pypi.org/project/rawpy/) to read NEF files.
3. Uses [Pillow](https://pypi.org/project/Pillow/) for image conversion and resizing.
4. Multi-threaded with `ThreadPoolExecutor`.
5. Real-time progress and preview updates while converting.

---

## Releases

Download the latest Windows executable from:

➡️ [https://github.com/ril3y/nef2jpg/releases](https://github.com/ril3y/nef2jpg/releases)

> Download the latest `.exe` file from the Releases section — no Python install required!

---

## Requirements (for source usage)

- Python 3.8+
- rawpy
- Pillow
- flet

---

## Installation (from source)

```bash
git clone https://github.com/ril3y/nef2jpg.git
cd nef2jpg
python -m venv venv
venv\Scripts\activate  # or source venv/bin/activate
pip install -r requirements.txt
python nef2jpg.py
