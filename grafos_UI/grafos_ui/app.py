from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from .ui import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Grafos UI")
    window = MainWindow()
    window.show()
    return app.exec()
