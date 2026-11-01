"""
paralegal_time.rules
Core timekeeping, multi-firm rounding algorithms, and ABA 93-379 no-overlap validation.
Maintained strictly by Alan Woodyard.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple

class RoundingMethod(str, Enum):
    UP = "up"
    NEAREST = "nearest"
    DOWN = "down"

class RoundingScope(str, Enum):
    ENTRY = "entry"
    DAY_ALLOCATE = "day_allocate"

@dataclass
class RoundingRule:
    increment_s: int = 360  # Default: 0.1 hr (6 minutes)
    method: RoundingMethod = RoundingMethod.UP
    grace_s: int = 0
    minimum_s: int = 0
    scope: RoundingScope = RoundingScope.ENTRY

def round_seconds(raw_s: int, rule: RoundingRule) -> int:
    """Rounds raw seconds according to the specified rule."""
    if raw_s <= 0:
        return 0

    inc = rule.increment_s
    rem = raw_s % inc

    if rule.method == RoundingMethod.DOWN:
        val = (raw_s // inc) * inc
    elif rule.method == RoundingMethod.NEAREST:
        if rem * 2 >= inc:
            val = ((raw_s // inc) + 1) * inc
        else:
            val = (raw_s // inc) * inc
    else:  # UP
        if rem <= rule.grace_s:
            val = (raw_s // inc) * inc
        else:
            val = ((raw_s // inc) + 1) * inc

    return max(val, rule.minimum_s)

def round_day_allocate(raw_seconds_list: List[int], rule: RoundingRule) -> List[int]:
    """
    Rounds daily total once, then distributes increments to activities by largest remainder.
    Prevents per-entry billing inflation on multiple short tasks.
    """
    if not raw_seconds_list:
        return []

    total_raw = sum(raw_seconds_list)
    total_billed = round_seconds(total_raw, rule)
    inc = rule.increment_s
    total_units = total_billed // inc

    # Base allocations
    base_allocated = [(s // inc) * inc for s in raw_seconds_list]
    allocated_units = sum(b // inc for b in base_allocated)
    remaining_units = total_units - allocated_units

    # Sort indices by largest remainder descending
    remainders = [(i, raw_seconds_list[i] % inc) for i in range(len(raw_seconds_list))]
    remainders.sort(key=lambda x: x[1], reverse=True)

    result = list(base_allocated)
    for i in range(min(remaining_units, len(remainders))):
        idx = remainders[i][0]
        if raw_seconds_list[idx] > 0:
            result[idx] += inc

    return result

def validate_no_overlap(existing_blocks: List[Tuple[int, int]], new_start: int, new_end: int) -> bool:
    """
    Asserts no time collision for a timekeeper across different matters or firms.
    Input intervals are [start_ms, end_ms]. Returns True if valid, False if overlapping.
    """
    for start, end in existing_blocks:
        if max(start, new_start) < min(end, new_end):
            return False
    return True
