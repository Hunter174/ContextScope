from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication, QPushButton
from PyQt5.QtCore import Qt, QPoint


class FloatingWindow(QWidget):
    BASE_MARGIN = 8  # resize edge thickness
    def __init__(self, title="", width=300, height=100):
        super().__init__()

        # ---------- DPI Scaling ----------
        self.scale = self.get_scale_factor()
        self.MARGIN = int(self.BASE_MARGIN * self.scale)

        self.setWindowTitle(title)
        self.resize(int(width * self.scale), int(height * self.scale))

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setMouseTracking(True)

        # ---------- Layout ----------
        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(4, 4, 4, 4)
        self.outer_layout.setSpacing(0)

        # ---------- Title Bar ----------
        self.title_bar = QWidget()
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setCursor(Qt.SizeAllCursor)

        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(6, 2, 6, 2)
        title_layout.setSpacing(4)

        self.title_label = QLabel(title)

        # DPI-aware font sizing
        font = self.title_label.font()
        font.setPointSizeF(9 * self.scale)
        self.title_label.setFont(font)

        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        # ---------- Window Buttons ----------
        btn_size = int(16 * self.scale)

        self.btn_min = self._make_btn("—", btn_size)
        self.btn_max = self._make_btn("□", btn_size)
        self.btn_close = self._make_btn("✕", btn_size)

        title_layout.addWidget(self.btn_min)
        title_layout.addWidget(self.btn_max)
        title_layout.addWidget(self.btn_close)

        # Let height be driven by content
        self.title_bar.setMinimumHeight(int(18 * self.scale))
        self.title_bar.setSizePolicy(
            self.title_bar.sizePolicy().horizontalPolicy(),
            self.title_bar.sizePolicy().Fixed
        )

        self.outer_layout.addWidget(self.title_bar)

        # ---------- Button Actions ----------
        self.btn_min.clicked.connect(self.showMinimized)
        self.btn_max.clicked.connect(self._toggle_max_restore)
        self.btn_close.clicked.connect(self.close)

        # ---------- Content Area ----------
        self.content_widget = QWidget()
        self.outer_layout.addWidget(self.content_widget)

        # ---------- State ----------
        self._drag_pos = None
        self._resizing = False
        self._resize_dir = None

        # ---------- Drag ONLY on title bar ----------
        self.title_bar.mousePressEvent = self._start_drag
        self.title_bar.mouseMoveEvent = self._drag_move
        self.title_bar.mouseReleaseEvent = self._stop_drag

    def _make_btn(self, text, btn_size):
        btn = QPushButton(text)
        btn.setFixedSize(btn_size, btn_size)
        btn.setCursor(Qt.ArrowCursor)  # prevents resize cursor bleed
        btn.setFocusPolicy(Qt.NoFocus)
        return btn

    def _toggle_max_restore(self):
        if self.isMaximized():
            self.showNormal()
            self.btn_max.setText("□")
        else:
            self.showMaximized()
            self.btn_max.setText("❐")

    # ---------- DPI ----------
    def get_scale_factor(self):
        screen = QApplication.primaryScreen()
        dpi = screen.logicalDotsPerInch()
        return dpi / 96.0

    # ---------- Dragging (Title Bar Only) ----------
    def _start_drag(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos()

    def _drag_move(self, event):
        if self._drag_pos:
            delta = QPoint(event.globalPos() - self._drag_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._drag_pos = event.globalPos()

    def _stop_drag(self, event):
        self._drag_pos = None

    # ---------- Mouse Press (Resize Only) ----------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._resize_dir = self._get_resize_direction(event.pos())
            if self._resize_dir:
                self._resizing = True

    # ---------- Mouse Move ----------
    def mouseMoveEvent(self, event):
        if self._resizing:
            self._resize(event.globalPos())
        else:
            self._update_cursor(event.pos())

    # ---------- Mouse Release ----------
    def mouseReleaseEvent(self, event):
        self._resizing = False
        self._resize_dir = None

    # ---------- Resize Logic ----------
    def _get_resize_direction(self, pos):
        x, y, w, h = pos.x(), pos.y(), self.width(), self.height()
        m = self.MARGIN

        directions = {
            "left": 0 <= x <= m,
            "right": w - m <= x <= w,
            "top": 0 <= y <= m,
            "bottom": h - m <= y <= h
        }

        if directions["top"] and directions["left"]:
            return "top_left"
        if directions["top"] and directions["right"]:
            return "top_right"
        if directions["bottom"] and directions["left"]:
            return "bottom_left"
        if directions["bottom"] and directions["right"]:
            return "bottom_right"
        if directions["left"]:
            return "left"
        if directions["right"]:
            return "right"
        if directions["top"]:
            return "top"
        if directions["bottom"]:
            return "bottom"

        return None

    def _resize(self, global_pos):
        rect = self.geometry()

        if "right" in self._resize_dir:
            rect.setRight(global_pos.x())
        if "bottom" in self._resize_dir:
            rect.setBottom(global_pos.y())
        if "left" in self._resize_dir:
            rect.setLeft(global_pos.x())
        if "top" in self._resize_dir:
            rect.setTop(global_pos.y())

        # DPI-scaled minimum size
        min_w = int(150 * self.scale)
        min_h = int(100 * self.scale)

        if rect.width() < min_w:
            rect.setWidth(min_w)
        if rect.height() < min_h:
            rect.setHeight(min_h)

        self.setGeometry(rect)

    # ---------- Cursor Feedback ----------
    def _update_cursor(self, pos):
        # ---- If hovering child widget (buttons etc.), restore default ----
        child = self.childAt(pos)
        if child and child is not self:
            self.unsetCursor()
            return

        # ---- Strict edge detection (override noisy resize detection) ----
        margin = 6  # adjust as needed for resize thickness
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()

        left = x <= margin
        right = x >= w - margin
        top = y <= margin
        bottom = y >= h - margin

        direction = None
        if top and left:
            direction = "top_left"
        elif top and right:
            direction = "top_right"
        elif bottom and left:
            direction = "bottom_left"
        elif bottom and right:
            direction = "bottom_right"
        elif left:
            direction = "left"
        elif right:
            direction = "right"
        elif top:
            direction = "top"
        elif bottom:
            direction = "bottom"

        cursors = {
            "left": Qt.SizeHorCursor,
            "right": Qt.SizeHorCursor,
            "top": Qt.SizeVerCursor,
            "bottom": Qt.SizeVerCursor,
            "top_left": Qt.SizeFDiagCursor,
            "bottom_right": Qt.SizeFDiagCursor,
            "top_right": Qt.SizeBDiagCursor,
            "bottom_left": Qt.SizeBDiagCursor,
        }

        if direction:
            self.setCursor(cursors[direction])
            return

        # ---- Title bar (move cursor) ----
        if self.title_bar.geometry().contains(pos):
            self.setCursor(Qt.SizeAllCursor)
            return

        # ---- Default ----
        self.unsetCursor()