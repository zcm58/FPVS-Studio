"""Custom exceptions for FPVS Studio domain models."""

from __future__ import annotations


class TimingValidationError(ValueError):
    """Raised when FPVS timing parameters are incompatible with the monitor refresh rate."""

    def __init__(
        self,
        message: str,
        *,
        base_rate_hz: float | None = None,
        oddball_rate_hz: float | None = None,
        monitor_refresh_hz: int | None = None,
    ) -> None:
        super().__init__(message)
        self.base_rate_hz = base_rate_hz
        self.oddball_rate_hz = oddball_rate_hz
        self.monitor_refresh_hz = monitor_refresh_hz
