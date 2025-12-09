from __future__ import annotations

from PySide6.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    """Root window for FPVS Studio configuration UI."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("FPVS Studio")
