"""Metes-and-bounds deed parser for boundary legal descriptions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SurveyCall:
    """A single metes-and-bounds survey call (bearing and distance)."""

    quadrant: str  # e.g., "NE", "NW", "SE", "SW"
    degrees: int
    minutes: int
    seconds: float
    distance_feet: float
    monument: Optional[str] = None

    @property
    def azimuth_degrees(self) -> float:
        """Convert quadrant bearing to 0-360 azimuth."""
        dec_deg = self.degrees + (self.minutes / 60.0) + (self.seconds / 3600.0)
        q = self.quadrant.upper()
        if q == "NE":
            return dec_deg
        elif q == "SE":
            return 180.0 - dec_deg
        elif q == "SW":
            return 180.0 + dec_deg
        elif q == "NW":
            return 360.0 - dec_deg
        return dec_deg


# Regex matching: N 45° 30' 15" E 125.50 feet or North 45 deg 30 min East 100 ft
_BEARING_PATTERN = re.compile(
    r"""(?P<ns>[NS]|NORTH|SOUTH)\s*
        (?P<deg>\d{1,3})\s*(?:°|deg|degrees|\s)?\s*
        (?:(?P<min>\d{1,2})\s*(?:'|min|minutes|\s)?)?\s*
        (?:(?P<sec>\d{1,2}(?:\.\d+)?)\s*(?:"|sec|seconds)?)?\s*
        (?P<ew>[EW]|EAST|WEST)\s*
        (?:a\s+distance\s+of\s+)?
        (?P<dist>\d+(?:\.\d+)?)\s*(?:'|feet|ft)""",
    re.IGNORECASE | re.VERBOSE,
)


def parse_metes_and_bounds(text: str) -> List[SurveyCall]:
    """Parse text containing metes-and-bounds survey calls."""
    calls: List[SurveyCall] = []
    for match in _BEARING_PATTERN.finditer(text):
        ns = match.group("ns")[0].upper()
        ew = match.group("ew")[0].upper()
        quadrant = f"{ns}{ew}"
        degrees = int(match.group("deg"))
        minutes = int(match.group("min") or 0)
        seconds = float(match.group("sec") or 0.0)
        distance = float(match.group("dist"))

        calls.append(
            SurveyCall(
                quadrant=quadrant,
                degrees=degrees,
                minutes=minutes,
                seconds=seconds,
                distance_feet=distance,
            )
        )
    return calls
