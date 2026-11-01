"""
title_toolkit.cadastral.bowditch
Calculates traverse misclosure, precision ratios, Compass Rule (Bowditch) adjustments,
and Shoelace parcel acreage for legal descriptions.
Maintained strictly by Alan Woodyard.
"""

import math
from typing import List, Dict, Any, Tuple

UNIT_FACTORS = {
    "FEET": 1.0,
    "FOOT": 1.0,
    "FT": 1.0,
    "VARA_TX": 100.0 / 36.0,  # Texas Statutory Vara: 33 1/3 in = 2.7778 ft
    "VARA_CA": 33.0 / 12.0,   # California 1851 Vara: 33.0 in = 2.75 ft
    "CHAIN": 66.0,            # Gunter's Chain
    "LINK": 0.66,             # Gunter's Link (7.92 in)
    "ROD": 16.5,              # Rod / Pole / Perch
}

def dms_to_decimal(degrees: float, minutes: float = 0.0, seconds: float = 0.0) -> float:
    return degrees + (minutes / 60.0) + (seconds / 3600.0)

def bearing_to_azimuth(prefix: str, angle_deg: float, suffix: str) -> float:
    p = prefix.upper().strip().rstrip(".")
    s = suffix.upper().strip().rstrip(".")

    if p in ("N", "NORTH") and s in ("E", "EAST"):
        return math.radians(angle_deg)
    elif p in ("S", "SOUTH") and s in ("E", "EAST"):
        return math.radians(180.0 - angle_deg)
    elif p in ("S", "SOUTH") and s in ("W", "WEST"):
        return math.radians(180.0 + angle_deg)
    elif p in ("N", "NORTH") and s in ("W", "WEST"):
        return math.radians(360.0 - angle_deg)
    else:
        raise ValueError(f"Invalid quadrant bearing format: {prefix} {angle_deg} {suffix}")

def normalize_distance(dist: float, unit_str: str = "FEET", jurisdiction: str = "TX") -> float:
    u = unit_str.upper().strip().rstrip(".")
    if "VARA" in u:
        return dist * (UNIT_FACTORS["VARA_TX"] if jurisdiction == "TX" else UNIT_FACTORS["VARA_CA"])
    for key, factor in UNIT_FACTORS.items():
        if u.startswith(key):
            return dist * factor
    return dist

def calculate_traverse(calls: List[Dict[str, Any]], jurisdiction: str = "TX") -> Dict[str, Any]:
    perimeter = 0.0
    legs = []

    for call in calls:
        if call.get("is_curve", False):
            radius = normalize_distance(call["radius"], call.get("unit", "FEET"), jurisdiction)
            arc_len = normalize_distance(call["arc_length"], call.get("unit", "FEET"), jurisdiction)
            delta = arc_len / radius
            chord_dist = 2.0 * radius * math.sin(delta / 2.0)

            c_p, (c_d, c_m, c_s), c_suf = call["chord_bearing"]
            azimuth = bearing_to_azimuth(c_p, dms_to_decimal(c_d, c_m, c_s), c_suf)

            dist_used = chord_dist
            perimeter += arc_len
            curve_data = {"is_curve": True, "radius": radius, "delta": delta, "arc_length": arc_len}
        else:
            p, (d, m, s), suf = call["bearing"]
            azimuth = bearing_to_azimuth(p, dms_to_decimal(d, m, s), suf)
            dist_used = normalize_distance(call["distance"], call.get("unit", "FEET"), jurisdiction)
            perimeter += dist_used
            curve_data = {"is_curve": False}

        lat = dist_used * math.cos(azimuth)
        dep = dist_used * math.sin(azimuth)
        legs.append({"dist": dist_used, "azimuth": azimuth, "lat": lat, "dep": dep, "curve": curve_data})

    sum_lat = sum(leg["lat"] for leg in legs)
    sum_dep = sum(leg["dep"] for leg in legs)
    misclosure = math.sqrt(sum_lat**2 + sum_dep**2)

    precision_denom = (perimeter / misclosure) if misclosure > 1e-7 else float("inf")
    is_defective = precision_denom < 5000.0

    # Bowditch Compass Rule Corrections
    adjusted_coords = [(0.0, 0.0)]
    curr_e, curr_n = 0.0, 0.0

    for leg in legs:
        c_lat = -sum_lat * (leg["dist"] / perimeter)
        c_dep = -sum_dep * (leg["dist"] / perimeter)
        adj_lat = leg["lat"] + c_lat
        adj_dep = leg["dep"] + c_dep
        curr_n += adj_lat
        curr_e += adj_dep
        adjusted_coords.append((curr_e, curr_n))

    # Gauss Shoelace Area Formula
    shoelace = 0.0
    for i in range(len(adjusted_coords) - 1):
        shoelace += (adjusted_coords[i][0] * adjusted_coords[i+1][1]) - \
                    (adjusted_coords[i+1][0] * adjusted_coords[i][1])
    polygon_area = abs(shoelace) / 2.0

    # Curve segment adjustments
    curve_adjust = 0.0
    for leg in legs:
        if leg["curve"]["is_curve"]:
            r = leg["curve"]["radius"]
            d = leg["curve"]["delta"]
            seg_area = 0.5 * (r**2) * (d - math.sin(d))
            curve_adjust += seg_area

    net_sqft = polygon_area + curve_adjust
    net_acres = net_sqft / 43560.0

    return {
        "perimeter_feet": perimeter,
        "misclosure_feet": misclosure,
        "precision_ratio": f"1:{int(precision_denom)}" if precision_denom != float("inf") else "1:INF",
        "precision_value": precision_denom,
        "is_defective": is_defective,
        "area_sqft": net_sqft,
        "area_acres": net_acres,
        "balanced_coords": adjusted_coords
    }
