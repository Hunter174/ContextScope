import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from core.app_controller import AppController

BASE_DIR = Path(__file__).resolve().parents[1]
STYLE_FILE = (BASE_DIR / "ui" / "styles" / "styles.qss")

def load_stylesheet():
    if not STYLE_FILE.exists():
        return ""
    return STYLE_FILE.read_text()

def run_app():
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())
    controller = AppController()
    sys.exit(app.exec_())