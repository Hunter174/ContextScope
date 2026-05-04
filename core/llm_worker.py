from PyQt5.QtCore import QThread, pyqtSignal

class LLMWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, client, payload):
        super().__init__()
        self.client = client
        self.payload = payload

    def run(self):
        try:
            result = self.client.run(self.payload)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))