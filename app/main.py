import sys
from PyQt5.QtWidgets import QApplication
from core.app_controller import AppController


def load_stylesheet(path):
    with open(path, "r") as f:
        return f.read()

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet("../ui/styles/styles.qss"))
    manager = AppController()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()