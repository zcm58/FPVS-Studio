from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .condition import ConditionModel
from .exceptions import TimingValidationError
from .timing import TimingDerived, compute_timing


@dataclass
class ExperimentModel:
    """Container for FPVS experiment configuration.

    The model represents all user-configurable properties for a single
    FPVS experiment. Derived timing or scheduling information will be
    computed elsewhere based on these fields.
    """

    experiment_id: str
    name: str
    base_rate_hz: float
    oddball_rate_hz: float
    image_on_ms: float
    blank_ms: float
    block_duration_seconds: int
    num_cycles: int
    randomize_within_cycle: bool
    rest_enabled: bool
    rest_default_seconds: int
    attention_enabled: bool
    fixation_min_changes: int
    fixation_max_changes: int

    fixation_base_color: str = "#0000FF"
    fixation_target_color: str = "#FF0000"
    instruction_text: str = ""
    attention_question_text: str = ""
    monitor_refresh_hz: Optional[int] = None
    conditions: List["ConditionModel"] = field(default_factory=list)

    def derive_timing(self, monitor_refresh_hz: Optional[int] = None) -> TimingDerived:
        """Compute and validate frame-based timing for this experiment.

        If ``monitor_refresh_hz`` is not provided, the model's stored monitor
        refresh rate will be used. A :class:`TimingValidationError` is raised if
        timing cannot be represented cleanly at the given refresh rate.
        """

        refresh_rate = monitor_refresh_hz if monitor_refresh_hz is not None else self.monitor_refresh_hz
        if refresh_rate is None:
            raise TimingValidationError(
                "Monitor refresh rate must be specified to derive timing.",
                base_rate_hz=self.base_rate_hz,
                oddball_rate_hz=self.oddball_rate_hz,
                monitor_refresh_hz=self.monitor_refresh_hz,
            )

        return compute_timing(self, refresh_rate)
