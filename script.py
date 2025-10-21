import pytesseract
import pyautogui
import os
import threading
from pynput import keyboard
from PIL import Image, ImageTk
import cv2
import tkinter as tk
def map_name_to_text():
    global map_name_global
    screen_size_x, screen_size_y = pyautogui.size()
    crop = int(screen_size_y * 0.7)
    width = int(screen_size_x * 0.4) - 50
    height = screen_size_y - crop - 60
    screenshot = pyautogui.screenshot('screenshot.png',region=(0, crop, width, height))
    img = cv2.imread('screenshot.png')
    mask = cv2.inRange(img, (250, 250, 250), (255, 255, 255))
    text = pytesseract.image_to_string(mask)
    text = text.strip()
    cv2.imwrite("mask.png", mask)
    map_name_global = text + '.webp'
    print(map_name_global)
root = tk.Tk()
root.withdraw()
overlay = tk.Toplevel(root)
overlay.withdraw()
overlay.overrideredirect(True)
overlay.attributes("-topmost", True)
overlay.attributes("-alpha", 0.5)
overlay.geometry("800x800")

label = tk.Label(overlay, borderwidth=0, highlightthickness=0)
label.pack()

overlay_visible = False

def display_map(map_name='Wreckers.webp', window_size=(500, 500)):
    """Show or update the overlay image."""
    global overlay_visible

    base_dir = os.path.dirname(os.path.abspath(__file__))
    map_path = os.path.join(base_dir, 'maps', map_name)


    img = Image.open(map_path).convert("RGBA")
    img = img.resize(window_size, Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(img)

    label.config(image=photo)
    label.image = photo

    overlay.geometry(f"{window_size[0]}x{window_size[1]}")

    if not overlay_visible:
        overlay.deiconify()
        overlay_visible = True

def toggle_overlay():
    global overlay_visible
    if overlay_visible:
        overlay.withdraw()
        overlay_visible = False
    else:
        display_map(map_name_global)

def on_press(key):
    try:
        if key.char == 'p':
            map_name_to_text()
        if key.char == 'l':
             root.after(0, toggle_overlay)
        if key.char == 'q':
            print("Exiting...")
            listener.stop()
            root.after(0, root.quit)
    except AttributeError:
        pass
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
listener = keyboard.Listener(on_press=on_press)
listener.start()
root.mainloop()