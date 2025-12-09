from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ConditionModel:
    """Defines the assets and trigger codes for an FPVS condition."""

    id: str
    label: str
    trigger_code_base: int
    trigger_code_oddball: int
    base_image_dir: Path
    oddball_image_dir: Path
