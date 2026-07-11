"""Pure orbit lap tracking helpers for Gravity Courier."""

from __future__ import annotations

from dataclasses import dataclass
import math

from .constants import LAP_COMPLETION_RADIANS


def wrap_angle_delta(delta: float) -> float:
    """Wrap an angle delta to the [-pi, pi] range."""
    while delta > math.pi:
        delta -= math.tau
    while delta < -math.pi:
        delta += math.tau
    return delta


def consume_completed_laps(
    accumulated_angle: float,
    threshold: float = LAP_COMPLETION_RADIANS,
) -> tuple[int, float]:
    """Return completed signed laps and the remaining accumulated angle."""
    laps = 0
    while accumulated_angle >= threshold:
        laps += 1
        accumulated_angle -= threshold
    while accumulated_angle <= -threshold:
        laps += 1
        accumulated_angle += threshold
    return laps, accumulated_angle


@dataclass
class OrbitLapTracker:
    """Track signed angular progress for one active planet visit."""

    prev_angle: float | None = None
    accumulated_angle: float = 0.0
    completed_laps: int = 0
    transfer_ready: bool = False
    transfer_triggered: bool = False

    def update_angle(self, angle: float) -> int:
        """Update with a new polar angle and return newly completed laps."""
        if self.prev_angle is None:
            self.prev_angle = angle
            return 0

        self.accumulated_angle += wrap_angle_delta(angle - self.prev_angle)
        self.prev_angle = angle
        laps, self.accumulated_angle = consume_completed_laps(self.accumulated_angle)
        if laps:
            self.completed_laps += laps
            self.transfer_ready = True
        return laps

    @property
    def turn_progress(self) -> float:
        return self.completed_laps + abs(self.accumulated_angle) / math.tau
