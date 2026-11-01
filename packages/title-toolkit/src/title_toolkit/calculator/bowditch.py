"""Bowditch (Compass Rule) traverse closure calculator."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple
from title_toolkit.parser.deed_parser import SurveyCall


@dataclass
class ClosureResult:
    """Mathematical result of Bowditch traverse closure analysis."""

    total_perimeter: float
    misclosure_latitude: float
    misclosure_departure: float
    linear_misclosure: float
    precision_ratio: float  # e.g., 10000 means 1:10,000
    is_closed: bool


def calculate_bowditch_closure(calls: List[SurveyCall], tolerance_ft: float = 0.1) -> ClosureResult:
    """Calculate survey traverse closure error using the Bowditch (Compass) method.

    Latitude = distance * cos(azimuth)
    Departure = distance * sin(azimuth)
    """
    if not calls:
        return ClosureResult(0.0, 0.0, 0.0, 0.0, 0.0, False)

    total_dist = 0.0
    sum_lat = 0.0
    sum_dep = 0.0

    for call in calls:
        total_dist += call.distance_feet
        rad = math.radians(call.azimuth_degrees)
        lat = call.distance_feet * math.cos(rad)
        dep = call.distance_feet * math.sin(rad)
        sum_lat += lat
        sum_dep += dep

    linear_misclosure = math.sqrt(sum_lat**2 + sum_dep**2)
    precision_ratio = (total_dist / linear_misclosure) if linear_misclosure > 0.000001 else float("inf")

    return ClosureResult(
        total_perimeter=round(total_dist, 4),
        misclosure_latitude=round(sum_lat, 5),
        misclosure_departure=round(sum_dep, 5),
        linear_misclosure=round(linear_misclosure, 5),
        precision_ratio=round(precision_ratio, 1),
        is_closed=linear_misclosure <= tolerance_ft,
    )
