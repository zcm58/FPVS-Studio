from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .condition import ConditionModel


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
    instruction_text: str
    attention_question_text: str
    monitor_refresh_hz: Optional[int] = None
    conditions: List[ConditionModel] = field(default_factory=list)
