from __future__ import annotations

from typing import Iterable

from fpvs_studio.models import ConditionModel, ExperimentModel


class ExperimentController:
    """Controller for managing ExperimentModel state.

    This controller will eventually respond to UI events, validate
    updates, and emit notifications to views. Phase 0 maintains the
    minimal interface and data references only.
    """

    def __init__(self, experiment: ExperimentModel) -> None:
        self._experiment = experiment

    @property
    def experiment(self) -> ExperimentModel:
        """Return the current experiment configuration."""

        return self._experiment

    def set_conditions(self, conditions: Iterable[ConditionModel]) -> None:
        """Replace the experiment's conditions with the provided sequence."""

        self._experiment.conditions = list(conditions)
