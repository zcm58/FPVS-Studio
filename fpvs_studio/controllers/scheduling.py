from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Optional


SegmentType = Literal["BLOCK", "REST"]


@dataclass
class RunSegment:
    """Represents a contiguous segment in an experiment run plan."""

    segment_type: SegmentType
    condition_id: Optional[str] = None
    duration_seconds: Optional[int] = None


@dataclass
class RunPlan:
    """Ordered list of run segments to be executed by a presenter.

    Future scheduling utilities will build a RunPlan from an
    ExperimentModel while accounting for rest periods, attention checks,
    and total cycles. Phase 0 keeps the structure available without
    implementing any scheduling logic.
    """

    segments: List[RunSegment]
