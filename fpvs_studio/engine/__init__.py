"""Presentation engine interfaces and placeholders."""

from .dummy_presenter import DummyPresenter
from .presenter_base import Presenter, RunResult
from .real_presenter import RealPresenter

__all__ = ["DummyPresenter", "Presenter", "RunResult", "RealPresenter"]
