"""Tests for deed call parsing and Bowditch closure calculator."""

from title_toolkit.calculator.bowditch import calculate_bowditch_closure
from title_toolkit.parser.deed_parser import SurveyCall, parse_metes_and_bounds


def test_square_traverse_perfect_closure():
    # 100x100 square: North 100, East 100, South 100, West 100
    calls = [
        SurveyCall(quadrant="NE", degrees=0, minutes=0, seconds=0, distance_feet=100.0),   # North
        SurveyCall(quadrant="NE", degrees=90, minutes=0, seconds=0, distance_feet=100.0),  # East
        SurveyCall(quadrant="SE", degrees=0, minutes=0, seconds=0, distance_feet=100.0),   # South
        SurveyCall(quadrant="NW", degrees=90, minutes=0, seconds=0, distance_feet=100.0),  # West
    ]

    result = calculate_bowditch_closure(calls)
    assert result.total_perimeter == 400.0
    assert result.linear_misclosure < 0.001
    assert result.is_closed is True


def test_parse_deed_text():
    deed_text = """
    Beginning at a 1/2-inch iron rod set; thence North 45 deg 00 min East 141.42 feet;
    thence South 45 deg 00 min East 141.42 feet;
    thence South 45 deg 00 min West 141.42 feet;
    thence North 45 deg 00 min West 141.42 feet to the point of beginning.
    """
    calls = parse_metes_and_bounds(deed_text)
    assert len(calls) == 4
    result = calculate_bowditch_closure(calls)
    assert result.is_closed is True
