import pytest
from paralegal_time.formats.formatter_1998b import (
    generate_ledes_1998b, format_ledes_date, LEDES_1998B_HEADER
)

def test_format_ledes_date():
    assert format_ledes_date("2026-10-26") == "20261026"
    assert format_ledes_date("2026/10/26") == "20261026"
    assert format_ledes_date("20261026") == "20261026"

def test_generate_ledes_1998b_structure():
    meta = {
        "invoice_date": "2026-10-26",
        "invoice_number": "INV-1001",
        "client_id": "CL-01",
        "matter_id": "MAT-01",
        "billing_start": "2026-10-01",
        "billing_end": "2026-10-26",
        "description": "October Legal Services",
        "law_firm_id": "FIRM-01"
    }
    line_items = [
        {
            "line_number": 1,
            "type": "F",
            "billed_seconds": 3600,
            "rate_cents": 15000,
            "total_cents": 15000,
            "date": "2026-10-15",
            "task_code": "L110",
            "activity_code": "A104",
            "description": "Fact investigation and document review",
            "timekeeper_id": "TK-01",
            "timekeeper_name": "Woodyard, Alan",
            "timekeeper_class": "LA"
        }
    ]

    output = generate_ledes_1998b(meta, line_items)
    lines = output.splitlines()

    assert lines[0] == "LEDES1998B[]"
    assert lines[1] == LEDES_1998B_HEADER

    # Check line item fields
    item_line = lines[2]
    assert item_line.endswith("[]")
    
    # Strip terminator and split by pipe
    fields = item_line[:-2].split("|")
    assert len(fields) == 24
    assert fields[0] == "20261026"       # INVOICE_DATE
    assert fields[1] == "INV-1001"       # INVOICE_NUMBER
    assert fields[4] == "150.00"         # INVOICE_TOTAL
    assert fields[9] == "F"              # TYPE
    assert fields[10] == "1.00"          # UNITS
    assert fields[12] == "150.00"        # TOTAL
    assert fields[14] == "L110"          # TASK_CODE
    assert fields[16] == "A104"          # ACTIVITY_CODE
