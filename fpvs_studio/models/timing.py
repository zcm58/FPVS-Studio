from __future__ import annotations

from dataclasses import dataclass
import math
from typing import TYPE_CHECKING

from .exceptions import TimingValidationError

if TYPE_CHECKING:
    from .experiment import ExperimentModel


@dataclass
class TimingDerived:
    """Derived timing values computed from an experiment configuration.

    The values in this structure represent frame-level timing derived from
    experiment parameters and a monitor refresh rate. All values are integer
    counts except for ``frame_duration_ms`` which conveys the duration of a
    single refresh period.
    """

    frames_per_second: int
    frames_per_base_cycle: int
    oddball_every_n_base: int
    image_on_frames: int
    blank_frames: int
    frame_duration_ms: float


def compute_timing(experiment: "ExperimentModel", monitor_refresh_hz: int) -> TimingDerived:
    """Compute frame-based timing for an experiment given the monitor refresh rate.

    Enforces that:
    - monitor_refresh_hz / base_rate_hz is an integer (frames_per_base_cycle).
    - base_rate_hz / oddball_rate_hz is an integer (oddball_every_n_base).
    - image_on_ms and blank_ms snap cleanly to integer frame counts, and:
      - If a nonzero ms value would round to 0 frames, raise TimingValidationError.
      - image_on_frames + blank_frames <= frames_per_base_cycle.

    Raises:
        TimingValidationError: if any of these constraints fail.

    Example:
        >>> from fpvs_studio.models import ExperimentModel, ConditionModel
        >>> exp = ExperimentModel(
        ...     experiment_id="demo",
        ...     name="Demo",
        ...     base_rate_hz=6.0,
        ...     oddball_rate_hz=1.2,
        ...     image_on_ms=50.0,
        ...     blank_ms=116.67,
        ...     block_duration_seconds=60,
        ...     num_cycles=10,
        ...     randomize_within_cycle=False,
        ...     rest_enabled=False,
        ...     rest_default_seconds=0,
        ...     attention_enabled=False,
        ...     fixation_min_changes=0,
        ...     fixation_max_changes=0,
        ...     instruction_text="",
        ...     attention_question_text="",
        ... )
        >>> timing = compute_timing(exp, 60)
        >>> timing.frames_per_base_cycle
        10
        >>> timing.oddball_every_n_base
        5
    """

    base_rate = experiment.base_rate_hz
    oddball_rate = experiment.oddball_rate_hz

    if base_rate <= 0:
        raise TimingValidationError(
            "Base rate must be greater than zero.",
            base_rate_hz=base_rate,
            oddball_rate_hz=oddball_rate,
            monitor_refresh_hz=monitor_refresh_hz,
        )

    if oddball_rate <= 0:
        raise TimingValidationError(
            "Oddball rate must be greater than zero.",
            base_rate_hz=base_rate,
            oddball_rate_hz=oddball_rate,
            monitor_refresh_hz=monitor_refresh_hz,
        )

    if monitor_refresh_hz <= 0:
        raise TimingValidationError(
            "Monitor refresh rate must be greater than zero.",
            base_rate_hz=base_rate,
            oddball_rate_hz=oddball_rate,
            monitor_refresh_hz=monitor_refresh_hz,
        )

    frames_per_second = monitor_refresh_hz
    frames_per_base_cycle_float = frames_per_second / base_rate
    frames_per_base_cycle = int(round(frames_per_base_cycle_float))
    if not math.isclose(
        frames_per_base_cycle_float, frames_per_base_cycle, rel_tol=0.0, abs_tol=1e-6
    ):
        raise TimingValidationError(
            "Monitor refresh rate must be an integer multiple of the base rate.",
            base_rate_hz=base_rate,
            oddball_rate_hz=oddball_rate,
            monitor_refresh_hz=monitor_refresh_hz,
        )

    oddball_every_n_base_float = base_rate / oddball_rate
    oddball_every_n_base = int(round(oddball_every_n_base_float))
    if not math.isclose(
        oddball_every_n_base_float, oddball_every_n_base, rel_tol=0.0, abs_tol=1e-6
    ):
        raise TimingValidationError(
            "Base rate must be an integer multiple of the oddball rate.",
            base_rate_hz=base_rate,
            oddball_rate_hz=oddball_rate,
            monitor_refresh_hz=monitor_refresh_hz,
        )

    frame_duration_ms = 1000.0 / frames_per_second

    def ms_to_frames(ms: float) -> int:
        frames_float = ms / frame_duration_ms
        frames = int(round(frames_float))
        if ms > 0 and frames == 0:
            raise TimingValidationError(
                "Nonzero duration is too short to fit into a single frame.",
                base_rate_hz=base_rate,
                oddball_rate_hz=oddball_rate,
                monitor_refresh_hz=monitor_refresh_hz,
            )
        if not math.isclose(frames_float, frames, rel_tol=0.0, abs_tol=1e-6):
            raise TimingValidationError(
                "Duration does not align to a whole number of frames.",
                base_rate_hz=base_rate,
                oddball_rate_hz=oddball_rate,
                monitor_refresh_hz=monitor_refresh_hz,
            )
        return frames

    image_on_frames = ms_to_frames(experiment.image_on_ms)
    blank_frames = ms_to_frames(experiment.blank_ms)

    if image_on_frames + blank_frames > frames_per_base_cycle:
        raise TimingValidationError(
            "Image on + blank duration exceeds base cycle length.",
            base_rate_hz=base_rate,
            oddball_rate_hz=oddball_rate,
            monitor_refresh_hz=monitor_refresh_hz,
        )

    return TimingDerived(
        frames_per_second=frames_per_second,
        frames_per_base_cycle=frames_per_base_cycle,
        oddball_every_n_base=oddball_every_n_base,
        image_on_frames=image_on_frames,
        blank_frames=blank_frames,
        frame_duration_ms=frame_duration_ms,
    )
