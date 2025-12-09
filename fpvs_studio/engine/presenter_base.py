from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from fpvs_studio.controllers import RunPlan
from fpvs_studio.models import ExperimentModel

if False:  # type checking aid without runtime import cycles
    from fpvs_studio.markers import MarkerBackend


@dataclass
class RunResult:
    """Summary of an experiment execution."""

    success: bool
    message: str = ""


class Presenter(Protocol):
    """Interface for presenting FPVS experiments to participants."""

    def run_experiment(
        self,
        experiment: ExperimentModel,
        participant_id: str,
        run_plan: RunPlan,
        n_fixation_changes: int,
        marker: "MarkerBackend",
    ) -> RunResult:
        """Run the experiment with the provided plan and marker backend."""
