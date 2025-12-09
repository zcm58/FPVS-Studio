from __future__ import annotations

from fpvs_studio.controllers import RunPlan
from fpvs_studio.models import ExperimentModel
from fpvs_studio.markers import MarkerBackend

from .presenter_base import Presenter, RunResult


class DummyPresenter(Presenter):
    """Placeholder presenter that mirrors the presenter interface."""

    def run_experiment(
        self,
        experiment: ExperimentModel,
        participant_id: str,
        run_plan: RunPlan,
        n_fixation_changes: int,
        marker: MarkerBackend,
    ) -> RunResult:
        """Stub method that will later trigger FPVS playback."""

        return RunResult(success=False, message="Presenter not implemented")
