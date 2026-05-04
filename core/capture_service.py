from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import QBuffer, QIODevice, QThread, pyqtSignal
import time
import hashlib


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


import time
import hashlib
from PyQt5.QtCore import QThread, pyqtSignal


class ContextStreamWorker(QThread):
    context_ready = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, capture_service, window, ocr_engine, vector_store, interval_ms=500):
        super().__init__()

        self.capture_service = capture_service
        self.window = window
        self.ocr_engine = ocr_engine
        self.vector_store = vector_store

        self.interval = interval_ms / 1000.0
        self._running = False

        self._last_hash = None
        self._last_text = None
        self._last_ocr_time = 0
        self.cooldown = 2.0

        # ---- NEW: buffer logic ----
        self._buffer = ""
        self._last_append_time = time.time()

        self.max_chars = 1200            # soft sequence length
        self.inactivity_timeout = 4.0    # seconds

    def _hash(self, data: bytes):
        return hashlib.md5(data).hexdigest()

    def _preview(self, text, n=120):
        text = text.replace("\n", " ")
        return text[:n] + ("..." if len(text) > n else "")

    def _compute_delta(self, prev, curr):
        if not prev:
            return curr

        if curr.startswith(prev):
            return curr[len(prev):]

        # fallback (OCR drift)
        return curr

    def _flush_buffer(self, reason):
        if not self._buffer.strip():
            return

        print(f"\n[FLUSH - {reason}]")
        print("[STORED CHUNK]", self._preview(self._buffer, 200))
        print("[CHUNK SIZE]", len(self._buffer))

        self.vector_store.add(self._buffer.strip())

        self._buffer = ""

    def run(self):
        self._running = True

        try:
            while self._running:
                img_bytes = self.capture_service.grab(self.window)

                if not img_bytes:
                    time.sleep(self.interval)
                    continue

                current_hash = self._hash(img_bytes)
                if current_hash == self._last_hash:
                    if self._buffer and (time.time() - self._last_append_time) > self.inactivity_timeout:
                        self._flush_buffer("inactivity")
                    time.sleep(self.interval)
                    continue

                self._last_hash = current_hash

                now = time.time()
                if (now - self._last_ocr_time) < self.cooldown:
                    time.sleep(self.interval)
                    continue

                self._last_ocr_time = now

                text = self.ocr_engine.extract(img_bytes)

                if text and text != self._last_text:
                    delta = self._compute_delta(self._last_text, text)
                    self._last_text = text

                    if delta.strip():
                        self._buffer += " " + delta
                        self._last_append_time = time.time()

                if len(self._buffer) >= self.max_chars:
                    self._flush_buffer("max_len")

                if self._buffer and (time.time() - self._last_append_time) > self.inactivity_timeout:
                    self._flush_buffer("inactivity")

                self.context_ready.emit(text if text else "")
                time.sleep(self.interval)

        except Exception as e:
            self.error.emit(str(e))

        finally:
            # ---- GUARANTEED FINAL FLUSH ----
            self._flush_buffer("shutdown")

    def stop(self):
        self._running = False
        self.wait()