import pytesseract
import pyautogui
import os
import sys
import numpy as np
import threading
from pynput import keyboard
from PIL import Image
import cv2
from PyQt5 import QtWidgets, QtGui, QtCore
import PyQt5
from PyQt5.QtCore import pyqtSignal, QObject, QTimer
QT_DEBUG_PLUGINS = 1

qt_plugins = os.path.join(
    os.path.dirname(__file__), 
    "venv", "Lib", "site-packages", "PyQt5", "Qt5", "plugins"
)
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = qt_plugins
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.
    SCRIPT_DIR = sys._MEIPASS
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

TESSERACT_PATH = os.path.join(SCRIPT_DIR, "Tesseract-OCR", "tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
os.environ['TESSDATA_PREFIX'] = os.path.join(SCRIPT_DIR, "Tesseract-OCR", "tessdata")

def map_name_to_text():
    global map_name_global
    global screen_size_x
    global screen_size_y

    screen_size_x, screen_size_y = pyautogui.size()
    crop_x = int(screen_size_x * 0.35)
    crop_y = int(screen_size_y * 0.75)
    width = int(screen_size_x * 0.65)
    height = int(screen_size_y * 0.9)

    screenshot = pyautogui.screenshot(
        'screenshot.png',
        region=(crop_x, crop_y, width - crop_x, height - crop_y)
        )
    
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    cv2.imwrite("debug_screenshot.png", img)

    img = Image.open("screenshot.png")
    img.load()
    try:
        text = pytesseract.image_to_string(img, output_type=pytesseract.Output.STRING)
        text = text.replace('’', '\'')
    except Exception as e:
        print(e)
        return

    try:
        text = text.strip()
        temp = text.split('\n')
        temp2 = temp[0].split(' - ')
        text = temp2[1]
        map_name_global = text + '.webp'
        print(map_name_global)
    except Exception as e:
        map_name_global = ''
        print(e)

class OverlayWindow(QtWidgets.QWidget):
    toggle_signal = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool |
            QtCore.Qt.WindowTransparentForInput
        )
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.label = QtWidgets.QLabel(self)
        self.label.setScaledContents(True)
        self.overlay_visible = False
        self.move(0, 0)
        self.setWindowOpacity(0.7)

        self.toggle_signal.connect(self.toggle_overlay)

    def display_map(self, map_name, window_size):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        map_path = os.path.join(base_dir, 'maps', map_name)

        if not os.path.exists(map_path):
            print("Missing map: ", map_path)
            return
        
        pix = QtGui.QPixmap(map_path)
        pix = pix.scaled(*window_size, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)

        self.label.setPixmap(pix)
        self.resize(pix.width(), pix.height())

        if not self.overlay_visible:
            self.show()
            self.overlay_visible = True

    def toggle_overlay(self):
        if self.overlay_visible:
            self.hide()
            self.overlay_visible = False
        else:
            if map_name_global:
                if screen_size_y == 1080:
                    self.display_map(map_name_global, (300, 300))
                elif screen_size_y == 1440:
                    self.display_map(map_name_global, (500, 500))
                else:
                    print('what is that screen resolution')
                    self.display_map(map_name_global, (500, 500))
            else:
                print('No map yet')

app = QtWidgets.QApplication(sys.argv)
overlay = OverlayWindow()

def on_press(key):
    try:
        if key.char == 'p':
            map_name_to_text()

        if key.char == 'l':
             overlay.toggle_signal.emit()

        if key.char == 'k':
            print("Exiting...")
            listener.stop()
            QTimer.singleShot(0, app.quit)

    except AttributeError:
        pass
print('Finished loading')
print('Manual: \nP: get map info while on pause(ESC)\nL: toggle map display\nK: exit')
listener = keyboard.Listener(on_press=on_press)
listener.start()
sys.exit(app.exec_())