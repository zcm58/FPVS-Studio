from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QPlainTextEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from fpvs_studio.models import ExperimentModel


class ExperimentEditor(QWidget):
    """Widget for editing FPVS experiment settings."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        self.experiment_id_edit = QLineEdit()
        self.name_edit = QLineEdit()
        general_group = QGroupBox("General")
        general_layout = QFormLayout()
        general_layout.addRow("Experiment ID", self.experiment_id_edit)
        general_layout.addRow("Name", self.name_edit)
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)

        # Timing
        self.base_rate_spin = QDoubleSpinBox()
        self.base_rate_spin.setRange(0.0, 1000.0)
        self.base_rate_spin.setDecimals(3)

        self.oddball_rate_spin = QDoubleSpinBox()
        self.oddball_rate_spin.setRange(0.0, 1000.0)
        self.oddball_rate_spin.setDecimals(3)

        self.image_on_spin = QDoubleSpinBox()
        self.image_on_spin.setRange(0.0, 10000.0)
        self.image_on_spin.setDecimals(3)

        self.blank_spin = QDoubleSpinBox()
        self.blank_spin.setRange(0.0, 10000.0)
        self.blank_spin.setDecimals(3)

        self.block_duration_spin = QSpinBox()
        self.block_duration_spin.setRange(0, 36000)

        timing_group = QGroupBox("Timing")
        timing_layout = QFormLayout()
        timing_layout.addRow("Base rate (Hz)", self.base_rate_spin)
        timing_layout.addRow("Oddball rate (Hz)", self.oddball_rate_spin)
        timing_layout.addRow("Image on (ms)", self.image_on_spin)
        timing_layout.addRow("Blank (ms)", self.blank_spin)
        timing_layout.addRow("Block duration (s)", self.block_duration_spin)
        timing_group.setLayout(timing_layout)
        layout.addWidget(timing_group)

        # Scheduling
        self.num_cycles_spin = QSpinBox()
        self.num_cycles_spin.setRange(0, 10000)

        self.randomize_check = QCheckBox("Randomize within cycle")
        self.rest_check = QCheckBox("Enable rest between cycles")

        self.rest_default_spin = QSpinBox()
        self.rest_default_spin.setRange(0, 3600)

        scheduling_group = QGroupBox("Scheduling")
        scheduling_layout = QFormLayout()
        scheduling_layout.addRow("Number of cycles", self.num_cycles_spin)
        scheduling_layout.addRow(self.randomize_check)
        scheduling_layout.addRow(self.rest_check)
        scheduling_layout.addRow("Rest duration (s)", self.rest_default_spin)
        scheduling_group.setLayout(scheduling_layout)
        layout.addWidget(scheduling_group)

        # Attention
        self.attention_enabled_check = QCheckBox("Enable attention task")
        self.fixation_min_spin = QSpinBox()
        self.fixation_min_spin.setRange(0, 10000)
        self.fixation_max_spin = QSpinBox()
        self.fixation_max_spin.setRange(0, 10000)

        attention_group = QGroupBox("Attention")
        attention_layout = QFormLayout()
        attention_layout.addRow(self.attention_enabled_check)
        attention_layout.addRow("Fixation min changes", self.fixation_min_spin)
        attention_layout.addRow("Fixation max changes", self.fixation_max_spin)
        attention_group.setLayout(attention_layout)
        layout.addWidget(attention_group)

        # Texts
        self.instruction_text_edit = QPlainTextEdit()
        self.attention_question_edit = QPlainTextEdit()

        texts_group = QGroupBox("Texts")
        texts_layout = QFormLayout()
        texts_layout.addRow("Instructions", self.instruction_text_edit)
        texts_layout.addRow("Attention question", self.attention_question_edit)
        texts_group.setLayout(texts_layout)
        layout.addWidget(texts_group)

        layout.addStretch()

    def set_experiment(self, experiment: ExperimentModel) -> None:
        """Populate the editor with values from the experiment model."""

        self.experiment_id_edit.setText(experiment.experiment_id)
        self.name_edit.setText(experiment.name)
        self.base_rate_spin.setValue(experiment.base_rate_hz)
        self.oddball_rate_spin.setValue(experiment.oddball_rate_hz)
        self.image_on_spin.setValue(experiment.image_on_ms)
        self.blank_spin.setValue(experiment.blank_ms)
        self.block_duration_spin.setValue(experiment.block_duration_seconds)
        self.num_cycles_spin.setValue(experiment.num_cycles)
        self.randomize_check.setChecked(experiment.randomize_within_cycle)
        self.rest_check.setChecked(experiment.rest_enabled)
        self.rest_default_spin.setValue(experiment.rest_default_seconds)
        self.attention_enabled_check.setChecked(experiment.attention_enabled)
        self.fixation_min_spin.setValue(experiment.fixation_min_changes)
        self.fixation_max_spin.setValue(experiment.fixation_max_changes)
        self.instruction_text_edit.setPlainText(experiment.instruction_text)
        self.attention_question_edit.setPlainText(experiment.attention_question_text)

    def apply_to_model(self, experiment: ExperimentModel) -> None:
        """Write editor values back into the provided experiment model."""

        experiment.experiment_id = self.experiment_id_edit.text()
        experiment.name = self.name_edit.text()
        experiment.base_rate_hz = self.base_rate_spin.value()
        experiment.oddball_rate_hz = self.oddball_rate_spin.value()
        experiment.image_on_ms = self.image_on_spin.value()
        experiment.blank_ms = self.blank_spin.value()
        experiment.block_duration_seconds = self.block_duration_spin.value()
        experiment.num_cycles = self.num_cycles_spin.value()
        experiment.randomize_within_cycle = self.randomize_check.isChecked()
        experiment.rest_enabled = self.rest_check.isChecked()
        experiment.rest_default_seconds = self.rest_default_spin.value()
        experiment.attention_enabled = self.attention_enabled_check.isChecked()
        experiment.fixation_min_changes = self.fixation_min_spin.value()
        experiment.fixation_max_changes = self.fixation_max_spin.value()
        experiment.instruction_text = self.instruction_text_edit.toPlainText()
        experiment.attention_question_text = self.attention_question_edit.toPlainText()
