import tkinter as tk
import keyboard
import pyperclip
import pytesseract
from PIL import Image, ImageGrab


def ocr(image: Image) -> str:
    """
        OCR using pytesseract
    """
    return pytesseract.image_to_string(image)


def auto_detect_lines(image: Image, region: list[int]) -> tuple[list[int], list[int]]:
    hlines, vlines = [], []
    image_gray = image.convert('L')
    empty_since = 0

    for pixelrow in range(image_gray.height):
        pixeldata = [image_gray.getpixel((pixelcol, pixelrow)) for pixelcol in range(image_gray.width)]
        if abs(max(pixeldata) - min(pixeldata)) < 40:
            empty_since += 1
        elif empty_since > 15:
            hlines += [pixelrow - int(empty_since / 2) + region[1]]
            empty_since = 0
        else:
            empty_since = 0

    for pixelcol in range(image_gray.width):
        pixeldata = [image_gray.getpixel((pixelcol, pixelrow)) for pixelrow in range(image_gray.height)]
        if abs(max(pixeldata) - min(pixeldata)) < 40:
            empty_since += 1
        elif empty_since > 30:
            vlines += [pixelcol - int(empty_since / 2) + region[0]]
            empty_since = 0
        else:
            empty_since = 0

    if hlines: hlines.pop(0)
    if vlines: vlines.pop(0)
    return hlines, vlines


class RiaTable:
    def __init__(self) -> None:
        # Create window
        self.root = tk.Tk()
        self.root.attributes("-alpha", 0.7)
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.config(cursor="cross")
        self.root.update()

        # Close root when escape is pressed
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self.image: Image = None
        self.image_data: dict = None
        self.region = [None, None, None, None]
        self.hlines = []
        self.vlines = []
        self.tesseract_params = {}

        # Draw black rectangle (10,10,100,100)
        self.canvas = tk.Canvas(self.root, width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight())

        # First capture a region
        self.capture_region()
        self.root.mainloop()


    def capture_region(self):
        """
            Capture a region of the screen
        """

        # Mouse down event
        def mousedown(event):
            self.region[0:2] = event.x, event.y
        self.root.bind('<Button-1>', mousedown)

        # Mouse move event
        def motion(event):
            if self.region[0] is None or self.region[1] is None:
                return
            x, y = event.x, event.y
            self.canvas.delete("all")
            self.canvas.create_rectangle(self.region[0], self.region[1], x, y, fill="black", outline="purple")
            self.canvas.pack()
        self.root.bind('<Motion>', motion)

        # Mouse up event
        def mouseup(event):
            # Complete region
            self.region[2:4] = event.x, event.y
            if self.region[0] > self.region[2]:
                self.region[0], self.region[2] = self.region[2], self.region[0]
            if self.region[1] > self.region[3]:
                self.region[1], self.region[3] = self.region[3], self.region[1]

            # Unbind events
            self.root.unbind('<Button-1>')
            self.root.unbind('<Motion>')
            self.root.unbind('<ButtonRelease-1>')

            # Capture the region while hiding the window
            self.root.withdraw()
            self.image = ImageGrab.grab(self.region)
            self.update_image_data()
            self.root.deiconify()

            # Go to next step
            self.define_lines()
        self.root.bind('<ButtonRelease-1>', mouseup)

    def update_image_data(self):
        self.image_data = pytesseract.image_to_data(self.image, output_type='dict', config="--psm 6 " + " ".join(f'-c {k}="{v}"' for k, v in self.tesseract_params.items()))
        # print(self.image_data)

    def define_lines(self):
        """
            Define lines in the region
        """
        # Add input textbox at 10, 10
        allowed_chars = tk.Entry(self.root)
        allowed_chars.insert(0, "")
        allowed_chars.pack()
        allowed_chars.place(x=self.region[0] + 70, y=self.region[1] - 60, width=200, height=30)
        def allowed_chars_change(event):
            self.tesseract_params["tessedit_char_whitelist"] = allowed_chars.get()
            if not self.tesseract_params["tessedit_char_whitelist"]:
                del self.tesseract_params["tessedit_char_whitelist"]
            self.update_image_data()
            update_screen()
        allowed_chars.bind('<KeyRelease>', allowed_chars_change)

        # Ctrl1 to numeric mode
        numeric_button = tk.Button(self.root, text="Numeric")
        numeric_button.pack()
        numeric_button.place(x=self.region[0], y=self.region[1] - 60, width=60, height=30)
        def numeric_mode(event):
            allowed_chars.delete(0, tk.END)
            allowed_chars.insert(0, "0123456789 ")
            allowed_chars_change(None)
        numeric_button.bind('<Button-1>', numeric_mode)

        # Line autodetection
        self.hlines, self.vlines = auto_detect_lines(self.image, self.region)

        def test_region(x, y, region):
            return x > region[0] and x <= region[2] and y > region[1] and y <= region[3]

        region_xbar = self.region[0] - 20, self.region[1], self.region[0], self.region[3]
        region_ybar = self.region[0], self.region[1] - 20, self.region[2], self.region[1]
        self.last_action = None

        def update_screen():
            self.canvas.delete("all")
            self.canvas.create_rectangle(*self.region, fill="black", outline="purple")
            self.canvas.create_rectangle(region_xbar, fill="white", outline="purple")
            self.canvas.create_rectangle(region_ybar, fill="white", outline="purple")
            for x in self.hlines:
                self.canvas.create_line(self.region[0], x, self.region[2], x, fill="red", width=2)
            for y in self.vlines:
                self.canvas.create_line(y, self.region[1], y, self.region[3], fill="red", width=2)
            for i, text in enumerate(self.image_data["text"]):
                if text.strip():
                    self.canvas.create_rectangle(
                        self.image_data["left"][i] + self.region[0],
                        self.image_data["top"][i] + self.region[1],
                        self.image_data["left"][i] + self.region[0] + self.image_data["width"][i],
                        self.image_data["top"][i] + self.region[1] + self.image_data["height"][i], outline="green")
            self.canvas.pack()

        # Mouse move event
        def motion(event):
            update_screen()
            if test_region(event.x, event.y, region_xbar):
                self.root.config(cursor="sb_right_arrow")
            elif test_region(event.x, event.y, region_ybar):
                self.root.config(cursor="sb_down_arrow")
            else:
                self.root.config(cursor="cross")
        self.root.bind('<Motion>', motion)

        # Left click to add lines
        def click(event):
            if test_region(event.x, event.y, region_xbar):
                self.hlines.append(event.y)
                self.last_action = 'h'
            elif test_region(event.x, event.y, region_ybar):
                self.vlines.append(event.x)
                self.last_action = 'v'
            update_screen()
        self.root.bind('<Button-1>', click)

        # R-key to auto-repeat
        def autorepeat(event):
            if self.last_action == 'h' and len(self.hlines) > 1:
                self.hlines.append(self.hlines[-1] * 2 - self.hlines[-2])
            elif self.last_action == 'v' and len(self.vlines) > 1:
                self.vlines.append(self.vlines[-1] * 2 - self.vlines[-2])
            update_screen()
        self.root.bind('r', autorepeat)

        # Right click to delete lines
        def rightclick(event):
            if test_region(event.x, event.y, region_xbar):
                for i, x in enumerate(self.hlines):
                    if abs(x - event.y) < 10:
                        del self.hlines[i]
            elif test_region(event.x, event.y, region_ybar):
                for i, y in enumerate(self.vlines):
                    if abs(y - event.x) < 10:
                        del self.vlines[i]
            update_screen()
        self.root.bind('<Button-3>', rightclick)

        # Ctrl+C event
        def copy(event):
            self.update_image_data()
            self.root.destroy()
            vlines = [self.region[0]] + sorted(self.vlines) + [self.region[2]]
            hlines = [self.region[1]] + sorted(self.hlines) + [self.region[3]]

            def extract_cell(x, y):
                found = []
                cell_region = (vlines[x] - self.region[0], hlines[y] - self.region[1], vlines[x+1] - self.region[0], hlines[y+1] - self.region[1])
                for i, text in enumerate(self.image_data["text"]):
                    if text.strip() == '':
                        continue
                    if test_region(self.image_data["left"][i], self.image_data["top"][i], cell_region):
                        found.append(text)
                return " ".join(found)

            # Split the image by hlines and vlines
            # Generate empty 2d array
            table = [[('') for y in range(len(vlines) - 1)] for z in range(len(hlines) - 1)]
            for y in range(len(hlines) - 1):
                for x in range(len(vlines) - 1):
                    table[y][x] = extract_cell(x, y)
            table_str = '\n'.join(['\t'.join(row) for row in table])

            # Table to clipboard
            pyperclip.copy(table_str)
            print(f"OCR result (copied to clipboad):\n{table_str}")
        self.root.bind('<Control-C>', copy)

        update_screen()


def main():

    while True:
        # Bind the hotkey to the function
        shortcut = "ctrl + shift + t"
        keyboard.add_hotkey(shortcut, RiaTable)

        # Wait indefinitely for the hotkey to be pressed
        print(f"Waiting for {shortcut}...")
        keyboard.wait()


if __name__ == "__main__":
    main()
