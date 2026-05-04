from ui.windows.chat_window import ChatWindow
from ui.windows.capture_window import CaptureWindow
from ui.windows.text_window import TextWindow

from core.llm_client import LLMClient
from core.llm_worker import LLMWorker
from core.capture_service import CaptureService, ContextStreamWorker
from core.textract_ocr import TextractOCR
from core.vector_store import FaissVectorStore

class AppController:
    def __init__(self):
        self.capture = CaptureWindow()
        self.text = TextWindow()
        self.chat = ChatWindow()

        # ---------- Services ----------
        self.llm_client = LLMClient()
        self.capture_service = CaptureService()

        # placeholders (you will implement)
        self.ocr_engine = TextractOCR()
        self.vector_store = FaissVectorStore()

        self.stream_worker = None
        self.current_mode = "manual"

        # ---------- Layout ----------
        self.chat.move(100, 100)
        self.capture.move(450, 100)
        self.text.move(800, 100)

        # ---------- Wiring ----------
        self.chat.toggle_edit_mode.connect(self.capture.set_interactive)
        self.chat.toggle_notepad.connect(self.text.setVisible)

        self.chat.change_capture_mode.connect(self._handle_capture_mode)
        self.chat.update_notepad.connect(self.text.set_context)

        self.chat.request_capture.connect(self._handle_capture)
        self.chat.send_prompt.connect(self._handle_prompt)

        self.show_all()

    # ---------- Capture (manual) ----------
    def _handle_capture(self):
        if self.current_mode == "manual":
            data = self.capture_service.grab(self.capture)

            if data:
                self.chat.set_pending_capture(data)
            else:
                self.chat.capture_failed()

            return

        # ---- LIVE MODE TOGGLE ----
        if self.stream_worker:
            self._stop_stream()
        else:
            self._start_stream()

    # ---------- Streaming ----------
    def _handle_capture_mode(self, mode: str):
        self.current_mode = mode

        if mode == "manual":
            self._stop_stream()

    def _start_stream(self):
        if self.stream_worker or not self.ocr_engine or not self.vector_store:
            return

        self.stream_worker = ContextStreamWorker(
            self.capture_service,
            self.capture,
            self.ocr_engine,
            self.vector_store,
            interval_ms=500
        )

        self.stream_worker.context_ready.connect(self._on_stream_context)
        self.stream_worker.error.connect(self.chat.capture_failed)

        self.stream_worker.start()

    def _stop_stream(self):
        if not self.stream_worker:
            return

        self.stream_worker.stop()
        self.stream_worker = None

    def _on_stream_context(self, text: str):
        self.text.append_context(text)

    # ---------- LLM ----------
    def _handle_prompt(self, image, user_text):
        # ---- Retrieve from FAISS ----
        retrieved = self.vector_store.search(user_text, k=5)
        memory = "\n\n".join(retrieved)

        print(retrieved)

        # ---- Mode-aware context ----
        if self.current_mode == "live":
            context = "[STREAMED CONTEXT]\n" + memory
        else:
            manual_context = self.text.get_context()
            context = manual_context + "\n\n[MEMORY]\n" + memory

        payload = {
            "context": context,
            "image": image,
            "user": user_text
        }

        self.worker = LLMWorker(self.llm_client, payload)
        self.worker.finished.connect(self.chat.on_response)
        self.worker.error.connect(self.chat.on_error)
        self.worker.start()

    def show_all(self):
        self.capture.show()
        self.chat.show()