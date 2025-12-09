from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from fpvs_studio.views import MainWindow


def main() -> None:
    """Launch the FPVS Studio configuration interface."""

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
