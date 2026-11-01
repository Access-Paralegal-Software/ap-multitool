"""Tests for firm timer policies and LEDES 1998B formatters."""

from datetime import date
from paralegal_time.timer.rules import FirmTimerPolicy, RoundingMode
from paralegal_time.ledes.formatter_1998b import LEDES1998BRecord, generate_ledes_1998b_header


def test_firm_timer_policy_six_minute_tenth():
    policy = FirmTimerPolicy(
        firm_id="FIRM-001",
        firm_name="Apex Legal",
        increment_minutes=6,
        minimum_minutes=6,
        rounding_mode=RoundingMode.UP,
    )

    # 1 second should round up to minimum increment (6 min = 0.1 hr)
    assert policy.calculate_billable_hours(1) == 0.1
    # 360 seconds (6 minutes) -> 0.1 hr
    assert policy.calculate_billable_hours(360) == 0.1
    # 361 seconds (6 min 1 sec) -> rounds up to 12 minutes = 0.2 hr
    assert policy.calculate_billable_hours(361) == 0.2
    # 3600 seconds (60 minutes) -> 1.0 hr
    assert policy.calculate_billable_hours(3600) == 1.0


def test_ledes_1998b_formatting():
    record = LEDES1998BRecord(
        invoice_date=date(2026, 10, 21),
        invoice_number="INV-2026-001",
        client_id="CL100",
        matter_id="M200",
        timekeeper_id="TK05",
        timekeeper_name="Taylor Paralegal",
        timekeeper_classification="PL",
        activity_date=date(2026, 10, 20),
        units=1.5,
        rate=175.0,
        description="Reviewed discovery responses and indexed exhibit tags.",
        task_code="L110",
        activity_code="A102",
    )

    assert record.line_total == 262.50
    pipe_line = record.to_pipe_delimited()
    assert "20261021|INV-2026-001|CL100|M200|FEE|1.50|175.00|262.50|20261020|L110|A102|TK05" in pipe_line
    assert generate_ledes_1998b_header().startswith("INVOICE_DATE|")
