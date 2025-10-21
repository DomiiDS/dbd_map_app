import pytesseract
import pyautogui
from pynput import keyboard
from PIL import Image
import cv2
def map_name_to_text():
    screen_size_x, screen_size_y = pyautogui.size()
    crop = int(screen_size_y * 0.7)
    width = int(screen_size_x * 0.4) - 50
    height = screen_size_y - crop - 60
    print(height)
    screenshot = pyautogui.screenshot('screenshot.png',region=(0, crop, width, height))
    img = cv2.imread('screenshot.png')
    mask = cv2.inRange(img, (250, 250, 250), (255, 255, 255))
    text = pytesseract.image_to_string(mask)
    cv2.imwrite("mask.png", mask)
    print(text)
def on_press(key):
    try:
        if key.char == 'p':
            map_name_to_text()
    except AttributeError:
        pass

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
listener = keyboard.Listener(on_press=on_press)
listener.start()
while True:
    pass