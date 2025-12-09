from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, List, Literal, Optional

from fpvs_studio.models.experiment import ExperimentModel


SegmentType = Literal["BLOCK", "REST"]


@dataclass
class RunSegment:
    """Represents a contiguous segment in an experiment run plan."""

    segment_type: SegmentType
    condition_id: Optional[str] = None
    duration_seconds: Optional[int] = None
    cycle_index: Optional[int] = None
    block_index: Optional[int] = None
    after_cycle_index: Optional[int] = None
    after_block_index: Optional[int] = None


@dataclass
class RunPlan:
    """Ordered list of run segments to be executed by a presenter.

    Future scheduling utilities will build a RunPlan from an
    ExperimentModel while accounting for rest periods, attention checks,
    and total cycles. Phase 0 keeps the structure available without
    implementing any scheduling logic.
    """

    segments: List[RunSegment]

    def __iter__(self) -> Iterable[RunSegment]:
        return iter(self.segments)


def build_run_plan(
    experiment: ExperimentModel,
    rng: random.Random,
) -> RunPlan:
    """Build a deterministic run plan for the given experiment."""

    if not experiment.conditions:
        raise ValueError("Experiment must have at least one condition to build a run plan.")

    if experiment.num_cycles < 1:
        raise ValueError("Experiment must have at least one cycle to build a run plan.")

    if experiment.rest_default_seconds < 0:
        raise ValueError("Rest duration cannot be negative.")

    condition_ids = [condition.id for condition in experiment.conditions]
    total_blocks = experiment.num_cycles * len(condition_ids)
    segments: List[RunSegment] = []
    block_index = 0

    for cycle_index in range(experiment.num_cycles):
        cycle_conditions = list(condition_ids)
        if experiment.randomize_within_cycle:
            rng.shuffle(cycle_conditions)

        for condition_id in cycle_conditions:
            segments.append(
                RunSegment(
                    segment_type="BLOCK",
                    condition_id=condition_id,
                    duration_seconds=experiment.block_duration_seconds,
                    cycle_index=cycle_index,
                    block_index=block_index,
                )
            )
            block_index += 1

            is_last_block = block_index == total_blocks
            if (
                experiment.rest_enabled
                and experiment.rest_default_seconds > 0
                and not is_last_block
            ):
                segments.append(
                    RunSegment(
                        segment_type="REST",
                        duration_seconds=experiment.rest_default_seconds,
                        after_cycle_index=cycle_index,
                        after_block_index=block_index - 1,
                    )
                )

    return RunPlan(segments=segments)


def draw_attention_changes(
    experiment: ExperimentModel,
    rng: random.Random,
) -> int:
    """Draw the number of fixation color changes for an experiment."""

    if not experiment.attention_enabled:
        return 0

    if experiment.fixation_min_changes < 0:
        raise ValueError("Minimum fixation changes cannot be negative.")

    if experiment.fixation_max_changes < 0:
        raise ValueError("Maximum fixation changes cannot be negative.")

    if experiment.fixation_min_changes > experiment.fixation_max_changes:
        raise ValueError("Minimum fixation changes cannot exceed the maximum value.")

    return rng.randint(experiment.fixation_min_changes, experiment.fixation_max_changes)
