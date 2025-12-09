from __future__ import annotations

from .base import MarkerBackend


class NullMarkerBackend(MarkerBackend):
    """Development marker backend that performs no operations."""

    def send(self, code: int) -> None:  # noqa: D401
        """No-op send implementation."""

    def close(self) -> None:  # noqa: D401
        """No-op close implementation."""
