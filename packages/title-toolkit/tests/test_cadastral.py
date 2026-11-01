import pytest
from title_toolkit.cadastral.bowditch import (
    calculate_traverse,
    normalize_distance,
    bearing_to_azimuth,
    dms_to_decimal,
    UNIT_FACTORS
)

def test_vara_conversions():
    # Texas Statutory Vara: 33 1/3 inches = 100/36 ft (~2.7778 ft)
    tx_dist = normalize_distance(36.0, "VARA", jurisdiction="TX")
    assert abs(tx_dist - 100.0) < 1e-4

    # California 1851 Vara: 33.0 inches = 2.75 ft
    ca_dist = normalize_distance(100.0, "VARA", jurisdiction="CA")
    assert abs(ca_dist - 275.0) < 1e-4

def test_quadrant_bearing_azimuth_conversion():
    # Quadrant I: N 45 E -> 45 deg
    assert abs(bearing_to_azimuth("N", 45.0, "E") - 0.785398) < 1e-4
    # Quadrant II: S 45 E -> 135 deg
    assert abs(bearing_to_azimuth("S", 45.0, "E") - 2.356194) < 1e-4
    # Quadrant III: S 45 W -> 225 deg
    assert abs(bearing_to_azimuth("S", 45.0, "W") - 3.926991) < 1e-4
    # Quadrant IV: N 45 W -> 315 deg
    assert abs(bearing_to_azimuth("N", 45.0, "W") - 5.497787) < 1e-4

def test_closed_traverse_computation():
    calls = [
        {"bearing": ("N", (45, 20, 15), "E"), "distance": 145.25, "unit": "FEET"},
        {"bearing": ("S", (44, 39, 45), "E"), "distance": 200.00, "unit": "FEET"},
        {"bearing": ("S", (45, 20, 15), "W"), "distance": 145.25, "unit": "FEET"},
        {"bearing": ("N", (44, 39, 45), "W"), "distance": 200.02, "unit": "FEET"},
    ]
    res = calculate_traverse(calls, jurisdiction="TX")

    assert res["perimeter_feet"] > 690.0
    assert res["misclosure_feet"] < 0.05
    assert res["precision_value"] > 10000.0  # Well above 1:5,000 threshold
    assert res["is_defective"] is False
    assert res["area_acres"] > 0.65  # ~0.667 Acres
