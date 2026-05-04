from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import QBuffer, QIODevice

class CaptureService:
    # ---------- SINGLE FRAME ----------
    def grab(self, window) -> bytes | None:
        if not window.isVisible():
            return None

        geo = window.frameGeometry()

        screen = QGuiApplication.screenAt(geo.center())
        if not screen:
            return None

        screen_geo = screen.geometry()

        x = geo.x() - screen_geo.x()
        y = geo.y() - screen_geo.y()

        pixmap = screen.grabWindow(
            0,
            x,
            y,
            geo.width(),
            geo.height()
        )

        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        pixmap.save(buffer, "PNG")

        return bytes(buffer.data())