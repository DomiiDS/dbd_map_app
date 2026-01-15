import pytesseract
import pyautogui
import mss
import os
import sys
import numpy as np
from pynput import keyboard
import cv2
import logging
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, QObject, QTimer
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon

def toggle_hotkeys():
    """"
    toggling hotkeys to avoid usage outside of game
    """ 
    global hotkeys_enabled
    hotkeys_enabled = not hotkeys_enabled
    enable_action.setChecked(hotkeys_enabled)

def map_name_to_text():
    """
    converting map name to string
    """ 
    global map_name_global
    global screen_size_x
    global screen_size_y

    screen_size_x, screen_size_y = pyautogui.size() # get user screen resolution
    crop_x = int(screen_size_x * 0.35)
    crop_y = int(screen_size_y * 0.75)
    width = int(screen_size_x * 0.65)
    height = int(screen_size_y * 0.9) # shape screenshot area accordingly
    with mss.mss() as sct: 
        region = {
            "top": crop_y,
            "left": crop_x,
            "width": width - crop_x,
            "height": height - crop_y
        }
        img = sct.grab(region) # capture screenshot
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        
    try:
        text = pytesseract.image_to_string(frame, output_type=pytesseract.Output.STRING) # convert screenshot text into string using Tesseract OCR
        text = text.replace('’', '\'')
        text = text.replace('|', 'I')
    except Exception as e:
        logging.error(e)
        return

    try:
        text = text.strip()
        temp = text.split('\n')
        temp2 = temp[0].split(' - ')
        text = temp2[1]
        map_name_global = text + '.webp' # extract map name and add extension
        logging.info(map_name_global)
    except Exception as e:
        map_name_global = ''
        logging.error(e)

class OverlayWindow(QtWidgets.QWidget):
    toggle_signal = pyqtSignal()
    def __init__(self):
        super().__init__() # window setup
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
        """
        choosing and displaying map
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        map_path = os.path.join(base_dir, 'maps', map_name)

        if not os.path.exists(map_path):
            logging.error("Missing map: ", map_path)
            return
        
        pix = QtGui.QPixmap(map_path) # add map image to overlay
        pix = pix.scaled(*window_size, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation) 

        self.label.setPixmap(pix)
        self.resize(pix.width(), pix.height())

        if not self.overlay_visible:
            self.show()
            self.overlay_visible = True

    def toggle_overlay(self):
        """
        toggling overlay
        """
        if self.overlay_visible: # toggle controls
            self.hide()
            self.overlay_visible = False
        else:
            if map_name_global:
                if screen_size_y == 1080: # resolution resolving and displaying adequate size
                    self.display_map(map_name_global, (300, 300))
                elif screen_size_y == 1440:
                    self.display_map(map_name_global, (500, 500))
                else:
                    logging.info('Unsupported screen resolution - defaulting to 1440p')
                    self.display_map(map_name_global, (500, 500))
            else:
                logging.error('No map yet')


def shutdown():
    try:
        listener.stop()
    except:
        pass
    app.quit()

def on_press(key):
    """
    key listener to catch input
    """
    try:
        if hotkeys_enabled == False:
            return
        if key.char == 'p':
            map_name_to_text()
        if key.char == 'l':
             overlay.toggle_signal.emit()

    except AttributeError:
        pass

appdata = os.getenv('APPDATA')
log_dir = os.path.join(appdata, 'DBDMaps', 'logs')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, 'app.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='a', encoding='utf-8')
    ]
) # logging support

hotkeys_enabled = False
QT_DEBUG_PLUGINS = 1
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.
    SCRIPT_DIR = sys._MEIPASS
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

TESSERACT_PATH = os.path.join(SCRIPT_DIR, "Tesseract-OCR", "tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
os.environ['OMP_THREAD_LIMIT'] = '1'
os.environ['TESSDATA_PREFIX'] = os.path.join(SCRIPT_DIR, "Tesseract-OCR", "tessdata")

app = QtWidgets.QApplication(sys.argv)
overlay = OverlayWindow()
icon_path = os.path.join(SCRIPT_DIR, 'maps', 'icon.png')
tray = QSystemTrayIcon(QIcon(icon_path), app) # tray app support instead of taskbar
menu = QMenu()

enable_action = menu.addAction('Enable hotkeys')
enable_action.setCheckable(True)
enable_action.setChecked(False)
enable_action.triggered.connect(toggle_hotkeys)
quit_action = menu.addAction('Quit')
quit_action.triggered.connect(shutdown)
tray.setContextMenu(menu)
tray.show()
listener = keyboard.Listener(on_press=on_press)
listener.start()
sys.exit(app.exec_())