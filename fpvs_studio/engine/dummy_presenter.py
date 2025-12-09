from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from fpvs_studio.controllers.scheduling import RunPlan
from fpvs_studio.engine.presenter_base import Presenter, RunResult
from fpvs_studio.markers.base import MarkerBackend
from fpvs_studio.models.experiment import ExperimentModel


class DummyPresenter(Presenter):
    """
    Dummy presenter that simulates a run without any rendering or hardware.

    It iterates the RunPlan, counts block segments, and writes simple CSV logs
    with synthetic timestamps. No markers are sent and no graphics are shown.
    """

    def __init__(self, base_output_dir: Path) -> None:
        self._base_output_dir = base_output_dir

    def run_experiment(
        self,
        experiment: ExperimentModel,
        participant_id: str,
        run_plan: RunPlan,
        n_fixation_changes: int,
        marker: MarkerBackend,
    ) -> RunResult:
        self._base_output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = f"{experiment.experiment_id}_{participant_id}_{timestamp}"
        event_log_path = self._base_output_dir / f"{prefix}_events.csv"
        summary_path = self._base_output_dir / f"{prefix}_summary.csv"

        block_count = 0
        current_time = datetime.now()
        event_rows: list[str] = []
        for segment in run_plan:
            segment_start = current_time.isoformat()
            event_rows.append(
                f"{segment_start},segment_start,{segment.segment_type},{segment.condition_id or ''}"
            )
            if segment.segment_type == "BLOCK":
                block_count += 1
            current_time += timedelta(seconds=segment.duration_seconds or 0)
            event_rows.append(
                f"{current_time.isoformat()},segment_end,{segment.segment_type},{segment.condition_id or ''}"
            )

        true_change_count = n_fixation_changes
        reported_change_count: Optional[int]
        if n_fixation_changes == 0:
            reported_change_count = 0
        elif n_fixation_changes > 1:
            reported_change_count = n_fixation_changes - 1
        else:
            reported_change_count = n_fixation_changes

        confirmed = True
        correct = reported_change_count == true_change_count
        absolute_error = abs(reported_change_count - true_change_count)

        event_log_path.write_text("timestamp,event_type,segment_type,condition_id\n" + "\n".join(event_rows))
        summary_content = "\n".join(
            [
                "participant_id,experiment_id,n_fixation_changes,reported_change_count,correct,absolute_error",
                f"{participant_id},{experiment.experiment_id},{n_fixation_changes},{reported_change_count},{correct},{absolute_error}",
                f"blocks,{block_count},true_changes,{true_change_count},confirmed,{confirmed}",
            ]
        )
        summary_path.write_text(summary_content)

        return RunResult(
            participant_id=participant_id,
            experiment_id=experiment.experiment_id,
            aborted=False,
            abort_reason=None,
            attention_enabled=experiment.attention_enabled,
            n_fixation_changes=n_fixation_changes,
            true_change_count=true_change_count,
            reported_change_count=reported_change_count,
            confirmed=confirmed,
            correct=correct,
            absolute_error=absolute_error,
            event_log_path=event_log_path,
            run_summary_path=summary_path,
        )
