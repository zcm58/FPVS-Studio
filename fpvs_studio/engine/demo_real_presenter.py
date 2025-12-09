from __future__ import annotations

import random
import sys
from pathlib import Path

from fpvs_studio.config.serialization import load_experiment
from fpvs_studio.controllers.scheduling import build_run_plan, draw_attention_changes
from fpvs_studio.engine.real_presenter import RealPresenter
from fpvs_studio.markers.null_marker import NullMarkerBackend


def main(argv: list[str]) -> int:
    if len(argv) < 4:
        print("Usage: python -m fpvs_studio.engine.demo_real_presenter <experiment.json> <participant_id> <output_dir>")
        return 1

    experiment_path = Path(argv[1])
    participant_id = argv[2]
    output_dir = Path(argv[3])

    experiment = load_experiment(experiment_path)

    if experiment.monitor_refresh_hz is None:
        print("Error: experiment.monitor_refresh_hz must be set for RealPresenter.")
        return 2

    rng = random.Random(12345)
    run_plan = build_run_plan(experiment, rng)
    n_changes = draw_attention_changes(experiment, rng)

    presenter = RealPresenter(base_output_dir=output_dir)
    result = presenter.run_experiment(
        experiment=experiment,
        participant_id=participant_id,
        run_plan=run_plan,
        n_fixation_changes=n_changes,
        marker=NullMarkerBackend(),
    )

    print("RunResult:")
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
