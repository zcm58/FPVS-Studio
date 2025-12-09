"""Presentation engine interfaces and placeholders."""

from .dummy_presenter import DummyPresenter
from .presenter_base import Presenter, RunResult

__all__ = ["DummyPresenter", "Presenter", "RunResult"]
