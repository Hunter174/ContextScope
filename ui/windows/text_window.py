from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from ui.windows.base_window import FloatingWindow


class TextWindow(FloatingWindow):
    def __init__(self):
        super().__init__("Text", 320, 240)

        outer = QVBoxLayout(self.content_widget)
        outer.setContentsMargins(4, 4, 4, 4)

        self.container = QWidget()
        self.container.setObjectName("captureContainer")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 0)
        shadow.setColor(Qt.black)
        self.container.setGraphicsEffect(shadow)

        outer.addWidget(self.container)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(6, 6, 6, 6)

        self.textbox = QTextEdit()
        self.textbox.setObjectName("contextTextbox")
        self.textbox.setPlaceholderText("Paste or type context here...")
        self.textbox.setAcceptRichText(False)

        layout.addWidget(self.textbox)

        row = QHBoxLayout()
        self.clear_btn = QPushButton("Clear")

        self.clear_btn.setCursor(Qt.ArrowCursor)
        self.clear_btn.setFocusPolicy(Qt.NoFocus)

        row.addWidget(self.clear_btn)
        layout.addLayout(row)

        self.clear_btn.clicked.connect(self.textbox.clear)

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    # ---------- Context API ----------
    def get_context(self) -> str:
        return self.textbox.toPlainText() or ""

    def set_context(self, text: str):
        self.textbox.setPlainText(text)

    def append_context(self, text: str):
        current = self.textbox.toPlainText()
        if current:
            self.textbox.setPlainText(current + "\n" + text)
        else:
            self.textbox.setPlainText(text)