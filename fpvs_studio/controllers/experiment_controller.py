from __future__ import annotations

from pathlib import Path

from fpvs_studio.config.serialization import load_experiment, save_experiment
from fpvs_studio.models import ConditionModel, ExperimentModel


class ExperimentController:
    """Controller for managing ExperimentModel state."""

    def __init__(self) -> None:
        self.experiment: ExperimentModel
        self.current_path: Path | None = None
        self.new_experiment()

    def new_experiment(self) -> None:
        """Create a fresh ExperimentModel with sensible defaults."""

        self.experiment = ExperimentModel(
            experiment_id="",
            name="",
            base_rate_hz=6.0,
            oddball_rate_hz=1.2,
            image_on_ms=166.0,
            blank_ms=0.0,
            block_duration_seconds=60,
            num_cycles=1,
            randomize_within_cycle=True,
            rest_enabled=False,
            rest_default_seconds=30,
            attention_enabled=False,
            fixation_min_changes=0,
            fixation_max_changes=0,
            instruction_text="",
            attention_question_text="",
            monitor_refresh_hz=None,
            conditions=[],
        )
        self.current_path = None

    def set_conditions(self, conditions: list[ConditionModel]) -> None:
        """Replace the experiment's conditions with the provided sequence."""

        self.experiment.conditions = list(conditions)

    def load_from_path(self, path: Path) -> None:
        """Load experiment data from a manifest path."""

        self.experiment = load_experiment(path)
        self.current_path = path

    def save_to_path(self, path: Path) -> None:
        """Save the current experiment to the provided path."""

        save_experiment(self.experiment, path)
        self.current_path = path

    def save(self) -> None:
        """Save using the existing path, raising if none is set."""

        if self.current_path is None:
            raise ValueError("No current path set for saving. Use save_to_path().")
        save_experiment(self.experiment, self.current_path)
