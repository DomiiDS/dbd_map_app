import pytesseract
import pyautogui
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
print(pytesseract.image_to_string(Image.open('test2.png')))
screen_size_x, screen_size_y = pyautogui.size()
print(type(screen_size_y))
crop = int(screen_size_y * 0.7)
width = int(screen_size_x * 0.4)
height = screen_size_y - crop
screenshot = pyautogui.screenshot('screenshot.png',region=(0, crop, width, height))