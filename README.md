# Ria's Table OCR

![logo](logo.svg)

## Windows Executable release
1. Downlad and install [Tesseract for windows](https://github.com/UB-Mannheim/tesseract/wiki)
2. Get the latest software from the [release page](https://github.com/rms95/rias-table-ocr/releases/latest)

## Usage
1. Start `ria-table-ocr`
2. Go the table you wish to capture, hit `ctrl + shift + t`
3. Select the region of the table.
4. Add/remove borders where required
5. (Optional) Limit allowed characters by click numeric
6. Copy the table using `ctrl + shift + c`

## Development
1. Clone this repo: `git clone https://github.com/rms95/rias-table-ocr.git`
2. Create a Python venv in the repo using `cd rias-table-ocr` `pip -m venv .venv`
3. Activate the venv using `./.venv/Scripts/activate`
4. Install as editable package: `pip install --editable .`
