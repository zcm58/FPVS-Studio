from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog, QInputDialog, QMainWindow, QMessageBox

from fpvs_studio.controllers.experiment_controller import ExperimentController
from fpvs_studio.controllers.run_controller import RunConfig, RunController
from fpvs_studio.engine.dummy_presenter import DummyPresenter
from fpvs_studio.models.exceptions import TimingValidationError
from fpvs_studio.views.experiment_editor import ExperimentEditor


class MainWindow(QMainWindow):
    """Root window for FPVS Studio configuration UI."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("FPVS Studio")

        self._controller = ExperimentController()
        self._editor = ExperimentEditor(self)
        self.setCentralWidget(self._editor)

        self._create_actions()

        self._controller.new_experiment()
        self._editor.set_experiment(self._controller.experiment)

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

        run_menu = self.menuBar().addMenu("&Run")
        run_action = QAction("Run (Simulation)...", self)
        run_action.triggered.connect(self.run_simulation)
        run_menu.addAction(run_action)

    def new_file(self) -> None:
        self._controller.new_experiment()
        self._editor.set_experiment(self._controller.experiment)

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
            self._controller.load_from_path(path)
        except Exception as exc:  # pylint: disable=broad-except
            QMessageBox.critical(self, "Error", f"Failed to load file: {exc}")
            return

        self._editor.set_experiment(self._controller.experiment)

    def save_file(self) -> None:
        self._editor.apply_to_model(self._controller.experiment)
        try:
            self._controller.save()
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
        self._editor.apply_to_model(self._controller.experiment)
        try:
            self._controller.save_to_path(path)
        except Exception as exc:  # pylint: disable=broad-except
            QMessageBox.critical(self, "Error", f"Failed to save file: {exc}")

    def run_simulation(self) -> None:
        participant_id, ok = QInputDialog.getText(
            self, "Run (Simulation)", "Enter participant ID:"
        )
        if not ok or not participant_id.strip():
            return

        output_dir = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", ""
        )
        if not output_dir:
            return

        self._editor.apply_to_model(self._controller.experiment)
        presenter = DummyPresenter(Path(output_dir))
        run_controller = RunController(presenter)
        config = RunConfig(participant_id=participant_id.strip(), output_dir=Path(output_dir))

        try:
            result = run_controller.run_experiment(self._controller.experiment, config)
        except TimingValidationError as exc:
            QMessageBox.critical(self, "Timing error", str(exc))
            return
        except Exception as exc:  # pylint: disable=broad-except
            QMessageBox.critical(self, "Run error", str(exc))
            return

        attention_text = "Yes" if result.attention_enabled else "No"
        reported = result.reported_change_count
        reported_text = "N/A" if reported is None else str(reported)
        correctness_text = "N/A" if result.correct is None else str(result.correct)
        abs_error_text = "N/A" if result.absolute_error is None else str(result.absolute_error)
        event_log_text = str(result.event_log_path) if result.event_log_path else "(not recorded)"
        summary_path_text = str(result.run_summary_path) if result.run_summary_path else "(not recorded)"

        message_lines = [
            f"Run completed for participant {result.participant_id}.",
            f"Attention enabled: {attention_text}",
            f"N changes: {result.n_fixation_changes}; reported: {reported_text}; correct: {correctness_text}; abs error: {abs_error_text}",
            f"Event log: {event_log_text}",
            f"Summary: {summary_path_text}",
        ]

        QMessageBox.information(self, "Run summary", "\n".join(message_lines))

