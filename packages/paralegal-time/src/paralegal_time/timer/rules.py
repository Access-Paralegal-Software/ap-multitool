"""Multi-firm timer rules and rounding logic."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum


class RoundingMode(str, Enum):
    UP = "up"
    NEAREST = "nearest"
    DOWN = "down"


@dataclass
class FirmTimerPolicy:
    """Policy governing billing increments and rounding rules for a specific firm."""

    firm_id: str
    firm_name: str
    increment_minutes: int = 6  # Standard 0.1 hour
    minimum_minutes: int = 6
    rounding_mode: RoundingMode = RoundingMode.UP

    def calculate_billable_hours(self, elapsed_seconds: int) -> float:
        """Calculate billable hours based on firm policy."""
        if elapsed_seconds <= 0:
            return 0.0

        elapsed_minutes = elapsed_seconds / 60.0
        effective_minutes = max(elapsed_minutes, float(self.minimum_minutes))

        units = effective_minutes / float(self.increment_minutes)
        if self.rounding_mode == RoundingMode.UP:
            rounded_units = math.ceil(units)
        elif self.rounding_mode == RoundingMode.DOWN:
            rounded_units = math.floor(units)
        else:
            rounded_units = round(units)

        billable_minutes = rounded_units * self.increment_minutes
        return round(billable_minutes / 60.0, 2)
