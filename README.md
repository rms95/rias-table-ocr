# Ria's Table OCR

## Installation
1. Install Python and [Tesseract](https://tesseract-ocr.github.io/tessdoc/Installation.html)
2. Create a Python venv using `pip -m venv .venv`
3. Activate the venv using `./.venv/Scripts/activate`
4. Install Ria's Table OCR: `pip install git+https://github.com/rms95/rias-table-ocr.git@main`

## Usage
1. Start `riatableocr` in the .venv
2. Go the table you wish to capture, hit `ctrl + shift + t`
3. Select the region of the table.
4. Add/remove borders where required
5. (Optional) Limit allowed characters by click numeric
6. Copy the table using `ctrl + c`
