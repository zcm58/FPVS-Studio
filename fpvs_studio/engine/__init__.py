"""Presentation engine interfaces and placeholders."""

from .dummy_presenter import DummyPresenter
from .presenter_base import Presenter, RunResult

try:  # Optional import: RealPresenter requires heavy graphics dependencies
    from .real_presenter import RealPresenter
except Exception:  # pragma: no cover - fallback when optional deps are missing
    RealPresenter = None  # type: ignore[assignment]

__all__ = ["DummyPresenter", "Presenter", "RunResult", "RealPresenter"]
