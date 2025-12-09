from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Protocol

from fpvs_studio.controllers.scheduling import RunPlan
from fpvs_studio.markers.base import MarkerBackend
from fpvs_studio.models.experiment import ExperimentModel


@dataclass
class RunResult:
    """Summary of a single FPVS experiment run for one participant."""

    participant_id: str
    experiment_id: str

    aborted: bool = False
    abort_reason: Optional[str] = None

    attention_enabled: bool = False
    n_fixation_changes: int = 0
    true_change_count: int = 0
    reported_change_count: Optional[int] = None
    confirmed: bool = False
    correct: Optional[bool] = None
    absolute_error: Optional[int] = None

    event_log_path: Optional[Path] = None
    run_summary_path: Optional[Path] = None


class Presenter(Protocol):
    """Interface for FPVS experiment presenters."""

    def run_experiment(
        self,
        experiment: ExperimentModel,
        participant_id: str,
        run_plan: RunPlan,
        n_fixation_changes: int,
        marker: MarkerBackend,
    ) -> RunResult:
        """Execute an FPVS experiment and return a summary."""
