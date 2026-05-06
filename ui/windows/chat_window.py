from PyQt5.QtWidgets import (
    QVBoxLayout, QLineEdit, QPushButton, QHBoxLayout,
    QComboBox, QWidget, QLabel, QScrollArea,
    QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

import markdown

from ui.windows.base_window import FloatingWindow


class ChatWindow(FloatingWindow):
    # ---------- Signals ----------
    toggle_edit_mode = pyqtSignal(bool)
    toggle_notepad = pyqtSignal(bool)
    request_capture = pyqtSignal()
    change_capture_mode = pyqtSignal(str)
    send_prompt = pyqtSignal(object, str)  # (image, text)
    update_notepad = pyqtSignal(str)

    def __init__(self):
        super().__init__("Chat", 320, 400)

        self.pending_capture = None

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # ---------- Controls Row ----------
        controls = QHBoxLayout()
        controls.setSpacing(6)
        controls.setContentsMargins(4, 6, 4, 6)

        btn_h = 32

        def _btn(text):
            b = QPushButton(text)
            b.setFixedHeight(btn_h)
            b.setCursor(Qt.ArrowCursor)
            b.setFocusPolicy(Qt.NoFocus)
            return b

        # ---- Notepad ----
        self.btn_notepad = _btn("📝")
        self.btn_notepad.setCheckable(True)

        # ---- Mode ----
        self.mode_select = QComboBox()
        self.mode_select.addItems(["Manual", "Live"])
        self.mode_select.setFixedHeight(btn_h)

        # ---- Capture ----
        self.capture_btn = _btn("Capture")
        self.capture_btn.setCheckable(True)
        self._streaming = False

        # ---- Edit / Show Toggle ----
        self.btn_toggle = _btn("Edit")
        self.btn_toggle.setCheckable(True)

        controls.addWidget(self.btn_notepad)
        controls.addWidget(self.mode_select)
        controls.addWidget(self.capture_btn)

        controls.addStretch()

        controls.addWidget(self.btn_toggle)

        # ---------- Chat Area ----------
        self.chat_area = QScrollArea()
        self.chat_area.setWidgetResizable(True)
        self.chat_area.setObjectName("chatArea")

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(6)

        self.chat_area.setWidget(self.chat_container)

        # ---------- Input ----------
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type a message...")

        # ---------- Layout ----------
        layout.addLayout(controls)
        layout.addWidget(self.chat_area)
        layout.addWidget(self.input)

        self.content_widget.setLayout(layout)

        # ---------- Connections ----------
        self.mode_select.currentTextChanged.connect(self._on_mode_changed)
        self.capture_btn.clicked.connect(self._on_capture_clicked)

        self.btn_toggle.toggled.connect(self._on_toggle_edit)
        self.btn_notepad.toggled.connect(self._on_toggle_notepad)

        self.input.returnPressed.connect(self.handle_input)

        self._on_mode_changed("Manual")

        # ---- FORCE INITIAL STATE SYNC ----
        self.btn_toggle.setChecked(True)
        self.btn_toggle.toggled.emit(True)

    # ---------- UI → Signals ----------
    def _on_toggle_edit(self, checked):
        self.toggle_edit_mode.emit(checked)
        self.btn_toggle.setText("Hide" if checked else "Edit")

    def _on_toggle_notepad(self, checked):
        self.toggle_notepad.emit(checked)

    def _on_mode_changed(self, mode_text):
        mode = "live" if mode_text == "Live" else "manual"
        self.change_capture_mode.emit(mode)

        if mode == "manual":
            self.capture_btn.setCheckable(False)
            self.capture_btn.setText("Capture")
            self.capture_btn.setChecked(False)

        else:
            self.capture_btn.setCheckable(True)
            self.capture_btn.setText("Start ●")
            self.capture_btn.setChecked(False)

    def _on_capture_clicked(self):
        if not self.capture_btn.isCheckable():
            # manual mode
            self.request_capture.emit()
            return

        # ---- live mode toggle ----
        self._streaming = self.capture_btn.isChecked()

        if self._streaming:
            self.capture_btn.setText("Stop ●")
        else:
            self.capture_btn.setText("Start ●")

        self.request_capture.emit()  # reused as toggle signal

    # ---------- External Hooks ----------
    def set_pending_capture(self, img_bytes):
        self.pending_capture = img_bytes
        self.add_message("Capture queued for next message", sender="assistant")

    def capture_failed(self):
        self.add_message("Capture failed", sender="assistant")

    # ---------- Chat UI ----------
    def add_message(self, text, sender="user", is_markdown=False):
        bubble = QLabel()
        bubble.setWordWrap(True)
        bubble.setContentsMargins(10, 6, 10, 6)

        if is_markdown:
            html = markdown.markdown(text)
            bubble.setText(html)
            bubble.setTextFormat(Qt.RichText)
        else:
            bubble.setText(text)
            bubble.setTextFormat(Qt.PlainText)

        bubble.setObjectName(
            "userBubble" if sender == "user" else "assistantBubble"
        )

        wrapper = QHBoxLayout()
        wrapper.setContentsMargins(0, 0, 0, 0)

        max_width = int(self.chat_area.viewport().width() * 0.7)

        if sender == "user":
            bubble.setMaximumWidth(max_width)
            bubble.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

            wrapper.addStretch()
            wrapper.addWidget(bubble)

        else:
            bubble.setMaximumWidth(max_width)
            bubble.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

            wrapper.addWidget(bubble)
            wrapper.addStretch()  # forces left alignment

        container = QWidget()
        container.setLayout(wrapper)

        self.chat_layout.addWidget(container)
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        QTimer.singleShot(
            0,
            lambda: self.chat_area.verticalScrollBar().setValue(
                self.chat_area.verticalScrollBar().maximum()
            ),
        )

    def show_loading(self):
        self.loading_widget = QLabel("Assistant is typing...")
        self.loading_widget.setObjectName("loadingBubble")

        wrapper = QHBoxLayout()
        wrapper.addWidget(self.loading_widget)
        wrapper.addStretch()

        container = QWidget()
        container.setLayout(wrapper)

        self.chat_layout.addWidget(container)
        self.scroll_to_bottom()

    def remove_loading(self):
        if hasattr(self, "loading_widget"):
            self.loading_widget.deleteLater()
            self.loading_widget = None

    # ---------- Input ----------
    def handle_input(self):
        text = self.input.text().strip()
        if not text:
            return

        self.add_message(text, sender="user")
        self.input.clear()

        self.show_loading()
        self.input.setEnabled(False)

        self.send_prompt.emit(self.pending_capture, text)
        self.pending_capture = None

    # ---------- Response Hooks (called by manager) ----------
    def on_response(self, result: dict):
        self.remove_loading()

        response_text = result.get("response", "")
        notepad_text = result.get("notepad", "")

        self.add_message(response_text, sender="assistant", is_markdown=True)

        # ---- SEND TO NOTEPAD ----
        if notepad_text:
            self.update_notepad.emit(notepad_text)

        self.input.setEnabled(True)
        self.input.setFocus()

    def on_error(self, error_msg):
        self.remove_loading()
        self.add_message(f"Error: {error_msg}", sender="assistant")

        self.input.setEnabled(True)

    def closeEvent(self, event):
        # This app controls everything if destroyed the program ends
        QApplication.quit()
        event.accept()