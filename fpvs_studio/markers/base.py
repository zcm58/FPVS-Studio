from __future__ import annotations

from typing import Protocol


class MarkerBackend(Protocol):
    """Protocol for sending numeric markers to an external backend."""

    def send(self, code: int) -> None:
        """Send a numeric trigger code to the configured backend."""

    def close(self) -> None:
        """Clean up resources associated with the backend."""
