from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import random

from fpvs_studio.controllers.scheduling import build_run_plan, draw_attention_changes, RunPlan
from fpvs_studio.engine.presenter_base import Presenter, RunResult
from fpvs_studio.markers.null_marker import NullMarkerBackend
from fpvs_studio.models.exceptions import TimingValidationError
from fpvs_studio.models.experiment import ExperimentModel
from fpvs_studio.models.timing import TimingDerived


@dataclass
class RunConfig:
    participant_id: str
    output_dir: Path
    rng_seed: Optional[int] = None


class RunController:
    """
    Orchestrates a single FPVS run:
    - Validates timing
    - Builds a RunPlan
    - Draws n_fixation_changes
    - Calls a Presenter with a NullMarkerBackend
    """

    def __init__(self, presenter: Presenter) -> None:
        self._presenter = presenter

    def run_experiment(
        self,
        experiment: ExperimentModel,
        config: RunConfig,
    ) -> RunResult:
        rng = random.Random(config.rng_seed)
        config.output_dir.mkdir(parents=True, exist_ok=True)

        if experiment.monitor_refresh_hz is None:
            raise TimingValidationError(
                "Monitor refresh rate must be set before running.",
                base_rate_hz=experiment.base_rate_hz,
                oddball_rate_hz=experiment.oddball_rate_hz,
                monitor_refresh_hz=None,
            )

        _timing: TimingDerived = experiment.derive_timing(experiment.monitor_refresh_hz)

        run_plan: RunPlan = build_run_plan(experiment, rng)
        n_changes = draw_attention_changes(experiment, rng)

        result = self._presenter.run_experiment(
            experiment=experiment,
            participant_id=config.participant_id,
            run_plan=run_plan,
            n_fixation_changes=n_changes,
            marker=NullMarkerBackend(),
        )

        return result
