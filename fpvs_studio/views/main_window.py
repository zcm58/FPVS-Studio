from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from fpvs_studio.controllers.experiment_controller import ExperimentController
from fpvs_studio.views.experiment_editor import ExperimentEditor


class MainWindow(QMainWindow):
    """Root window for FPVS Studio configuration UI."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("FPVS Studio")

        self.controller = ExperimentController()
        self.editor = ExperimentEditor(self)
        self.setCentralWidget(self.editor)

        self._create_actions()

        self.controller.new_experiment()
        self.editor.set_experiment(self.controller.experiment)

    def _create_actions(self) -> None:
        file_menu = self.menuBar().addMenu("&File")

        new_action = QAction("&New", self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("&Open...", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("&Save", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def new_file(self) -> None:
        self.controller.new_experiment()
        self.editor.set_experiment(self.controller.experiment)

    def open_file(self) -> None:
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Open Experiment",
            "",
            "JSON Files (*.json);;All Files (*)",
        )
        if not path_str:
            return

        path = Path(path_str)
        try:
            self.controller.load_from_path(path)
        except Exception as exc:  # pylint: disable=broad-except
            QMessageBox.critical(self, "Error", f"Failed to load file: {exc}")
            return

        self.editor.set_experiment(self.controller.experiment)

    def save_file(self) -> None:
        self.editor.apply_to_model(self.controller.experiment)
        try:
            self.controller.save()
        except ValueError:
            self.save_file_as()
        except Exception as exc:  # pylint: disable=broad-except
            QMessageBox.critical(self, "Error", f"Failed to save file: {exc}")

    def save_file_as(self) -> None:
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            "Save Experiment",
            "",
            "JSON Files (*.json);;All Files (*)",
        )
        if not path_str:
            return

        path = Path(path_str)
        self.editor.apply_to_model(self.controller.experiment)
        try:
            self.controller.save_to_path(path)
        except Exception as exc:  # pylint: disable=broad-except
            QMessageBox.critical(self, "Error", f"Failed to save file: {exc}")

