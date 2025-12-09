from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class TimingDerived:
    """Derived timing values computed from an experiment configuration.

    This structure will be populated by future timing utilities that
    align experiment rates with monitor refresh characteristics. Phase 0
    keeps these fields optional to signal pending computation.
    """

    frames_per_second: int
    frames_per_base_cycle: Optional[int] = None
    oddball_every_n_base: Optional[int] = None
    image_on_frames: Optional[int] = None
    blank_frames: Optional[int] = None
