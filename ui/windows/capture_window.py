from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

from ui.windows.base_window import FloatingWindow
from core.utility import set_click_through

class CaptureWindow(FloatingWindow):
    # ---------- Signals ----------
    capture_ready = pyqtSignal(object)   # bytes
    capture_failed = pyqtSignal()

    def __init__(self):
        super().__init__("Capture", 320, 200)

        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # ---------- Layout ----------
        outer = QVBoxLayout(self.content_widget)
        outer.setContentsMargins(4, 4, 4, 4)

        # ---------- Container ----------
        self.container = QWidget()
        self.container.setObjectName("captureContainer")
        self._apply_style(active=False)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 0)
        shadow.setColor(Qt.black)
        self.container.setGraphicsEffect(shadow)

        outer.addWidget(self.container)

        # ---------- Inner ----------
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)

        self.content = QLabel()
        self.content.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.content)

        # ---------- State ----------
        self.capture_mode = "manual"
        self._interactive = False

    # ---------- Window Behavior ----------
    def closeEvent(self, event):
        event.ignore()
        self.hide()

    # ---------- Interaction ----------
    def set_interactive(self, enabled: bool):
        self._interactive = enabled
        set_click_through(self, not enabled)
        self._apply_style(active=enabled)

    def _apply_style(self, active: bool):
        self.container.setProperty("active", active)
        self.container.style().unpolish(self.container)
        self.container.style().polish(self.container)

        self.title_bar.setProperty("active", active)
        self.title_bar.style().unpolish(self.title_bar)
        self.title_bar.style().polish(self.title_bar)

    # ---------- Capture Mode ----------
    def set_capture_mode(self, mode: str):
        self.capture_mode = mode

    def get_capture_bytes(self):
        return self._grab_bytes()